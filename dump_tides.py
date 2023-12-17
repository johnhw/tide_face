from textwrap import dedent
import re
from predict_tide import predict_tide, unpack_tz, epoch, rads_per_second, seconds_tz
import random, math

MAX_AMP = 12.0
MAX_PHASE = math.pi*2
MAX_SPEED = 0.001

def get_seq(bits, max_val, seq):
    """Quantize a sequence to the given number of bits,
    with the given max value and return a string of hex values"""
    elts = []
    for val in seq:
        elts.append(int((val / max_val) * ((2**bits)-1)))
    return ", ".join([f"0x{x:X}" for x in elts])

def quantize_seq(bits, max_val, seq):
    """Quantize the sequence to the given number of bits,
    with the given max value"""
    elts = []
    for val in seq:
        e = int((val / max_val) * ((2**bits)-1))
        elts.append(((e/((2**bits)-1.0)) * max_val))    
    return elts 

def predict_c_tide(t, year, phases, speeds, amps, offset):
    """Predict the tide at time t using the given constituents.
    as it would be in the C code"""
    tide = offset
    t = t - epoch(year)
    for phase, speed, amp in zip(phases, speeds, amps):
        tide += amp * math.cos(speed * t + phase)
    return tide




def extract_cycles(station, year, constituents, min_amp):
    """Combine constituent data with station data to extract the raw harmonic 
    oscillations for the given year. Exclude all oscillations with an amplitude
    less than min_amp"""
    amps = []
    phases = []
    speeds = []
    for c in station["constituents"]:
        station_amp = station["constituents"][c]["amp"]        
        node_factor = constituents[c]["years"][str(year)]["node_factor"]
        station_phase = station["constituents"][c]["phase"]
        equilib = constituents[c]["years"][str(year)]["equilibrium"]
        time_offset = seconds_tz(station["zone_offset"]) * rads_per_second(constituents[c]["speed"])
        amp = station_amp * node_factor        
        if station["units"]=="feet":
            scale = 0.3048
        elif station["units"]=="meters":
            scale = 1.0 
        if amp>min_amp:            
            amps.append(amp * scale)
            phase = math.radians(equilib - station_phase) - time_offset
            # force to radians in [0, 2pi]
            phase = phase % (2*math.pi)
            if phase<0:
                phase += 2*math.pi
            phases.append(phase)
            speeds.append(rads_per_second(constituents[c]["speed"]))
    return amps, phases, speeds

def generate_tests(station, year, constituents, phases, speeds, amps, n_samples=400):
    """Generate a set of test times and tides for the given station and year.
    The tides are generated using the predict_tide function, and the quantized
    tides are generated using the predict_c_tide function. The mean error is
    returned, along with the test times and tide levels."""    
    min_time = epoch(year)
    max_time = epoch(year+1)
    test_times = [random.randint(min_time, max_time) for _ in range(0, 32)]
    test_tides = [predict_tide(t, constituents, station) for t in test_times]
    total_error = 0
    
    for i in range(n_samples):
        time = random.randint(min_time, max_time)
        tide = predict_tide(time, constituents, station)        
        quantized = predict_c_tide(time, year,  quantize_seq(16, MAX_PHASE, phases), quantize_seq(32, MAX_SPEED, speeds),  quantize_seq(16, MAX_AMP, amps), station["offset"])
        total_error += abs(tide - quantized)
    mean_error = total_error / n_samples
    return test_times, test_tides, mean_error

def make_c_name(name):
    c_name = re.sub(r'[^a-zA-Z0-9_]', '_', name).lower()
    c_name = re.sub(r"_+", "_", c_name)
    return c_name

def dump_clock_station(constituents, prev_name=None, file=None):
    """Dump the simple default station that just has the single largest consituent (M2),
    with a phase of 0 and an amplitude of 1.0"""
    amps = [1.0]
    phases = [0.0]
    speeds = [rads_per_second(constituents["M2"]["speed"])]
    prev_name = prev_name if prev_name is not None else "NULL"
    print(dedent(f"""                                     
                    char station_CLOCK_name [] = "CLOCK";
                    uint32_t station_CLOCK_speed [] = {{{get_seq(32, MAX_SPEED, speeds)}}};
                    uint16_t station_CLOCK_amp [] = {{{get_seq(16, MAX_AMP, amps)}}};
                    uint16_t station_CLOCK_phase [] = {{{get_seq(16, MAX_PHASE, phases)}}};
                    tidal station_CLOCK = {{
                            .type = STATION_TYPE_CLOCK,
                            .name = station_CLOCK_name,
                            .year = 2000,
                            .lat = 0.0,
                            .lon = 0.0,
                            .offset = 0.0,
                            .speeds = station_CLOCK_speed,
                            .amps = station_CLOCK_amp,
                            .phases = station_CLOCK_phase,
                            .n_constituents = 1,
                            .mean_error = 0.0,
                            .previous = {prev_name},
                    }};                                        
"""), file=file)
    return f"station_CLOCK"

def dump_station(station, year, constituents, min_amp, speed_name=None, prev_name=None, include_tests=True, file=None):
    name = station["name"]
    c_name = make_c_name(name)
    
    amps, phases, speeds = extract_cycles(station, year, constituents, min_amp)
    test_times, test_tides, mean_error = generate_tests(station, year, constituents, phases, speeds, amps)
    
    prev_name = prev_name if prev_name is not None else "NULL"
    print(dedent(f"""                 
                    /* Mean error for {name} in {year} is approximately {mean_error:.3f}m */
                    char station_{c_name}_{year}_name [] = "{name}";
                    """), file=file)
    # don't store the speed if it's the same as the previous year
    if speed_name is None:
        print(dedent(f"""            
                    uint32_t station_{c_name}_{year}_speed [] = {{{get_seq(32, MAX_SPEED, speeds)}}};
                """), file=file)
        speed_name = f"station_{c_name}_{year}_speed"
    print(dedent(f"""
                    uint16_t station_{c_name}_{year}_amp [] = {{{get_seq(16, MAX_AMP, amps)}}};
                    uint16_t station_{c_name}_{year}_phase [] = {{{get_seq(16, MAX_PHASE, phases)}}};
                    """), file=file)
    if include_tests:
        print(dedent(f"""
                    #ifdef TIDE_DEBUG
                    time_t station_{c_name}_{year}_test_times [] = {{{", ".join([str(t) for t in test_times])}}};
                    float station_{c_name}_{year}_test_tides [] = {{{", ".join([str(t) for t in test_tides])}}};
                    #endif
                """), file=file)
        
    print(dedent(f"""
                    tidal station_{c_name}_{year} = {{
                            .type = STATION_TYPE_HARMONIC,
                            .name = station_{c_name}_{year}_name,
                            .year = {year},
                            .lat = {station["lat"]},
                            .lon = {station["lon"]},
                            .offset = {station["offset"]},
                            .speeds = {speed_name},
                            .amps = station_{c_name}_{year}_amp,
                            .phases = station_{c_name}_{year}_phase,
                            .n_constituents = {len(amps)},
                            .mean_error = {mean_error},
                            .previous = &{prev_name},
                    }};                                        
"""), file=file)
    return speed_name, f"station_{c_name}_{year}"

def dump_station_years(station, min_year, max_year, constituents, min_amp, include_tests=True, prev_name=None, file=None):
    """Dump the station for the given range of years."""
    speed_name = None    
    for year in range(min_year, max_year+1):
        speed_name, prev_name = dump_station(station, year, constituents, min_amp, speed_name, prev_name, file=file)
    return prev_name

def finalise_tides(prev_name, file=None):
    print(dedent(f"""
                    tidal * tidal_stations  = &{prev_name};                    
                """), file=file)
