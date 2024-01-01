from textwrap import dedent
import re
from predict_tide import predict_tide, unpack_tz, epoch, rads_per_second, seconds_tz, find_tide_events
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

def float_seq(seq):
    """Return a string of floats, with high precision (16 decimal places)"""    
    return ", ".join([f"{x:0.16e}" for x in seq])


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

def get_tidal_range(time, constituents, station):
    events = find_tide_events(time, 3, constituents, station)
    highs = [e for e in events if e.event_type=="high"]
    lows = [e for e in events if e.event_type=="low"]
    return highs[0].level - lows[0].level
    
    
    

def generate_tests(station, year, constituents, phases, speeds, amps, n_samples=400):
    """Generate a set of test times and tides for the given station and year.
    The tides are generated using the predict_tide function, and the quantized
    tides are generated using the predict_c_tide function. The mean error is
    returned, along with the test times and tide levels."""    
    min_time = epoch(year)
    max_time = epoch(year+1)
    test_times = [random.randint(min_time, max_time) for _ in range(0, 96)]
    test_tides = [predict_tide(t, constituents, station) for t in test_times]
    total_error = 0

    # very slow but we only do it once
    test_ranges = [get_tidal_range(time, constituents, station) for time in test_times]
    neaps_range, springs_range = min(test_ranges), max(test_ranges)
    
    for i in range(n_samples):
        time = random.randint(min_time, max_time)
        tide = predict_tide(time, constituents, station)        
        quantized = predict_c_tide(time, year,  quantize_seq(16, MAX_PHASE, phases), quantize_seq(32, MAX_SPEED, speeds),  quantize_seq(16, MAX_AMP, amps), station["offset"])
        total_error += abs(tide - quantized)
    mean_error = total_error / n_samples
    return test_times, test_tides, mean_error, neaps_range, springs_range

def make_c_name(name):
    c_name = re.sub(r'[^a-zA-Z0-9_]', '_', name).lower()
    c_name = re.sub(r"_+", "_", c_name)
    return c_name

def dump_clock_station(constituents, file=None):
    # create a fake station with a single constituent, M2, with amplitude 1.0 and phase 0.0
    clock_station = {"name":"CLOCK", "lat":0.0, "lon":0.0, "offset":0.0, "units":"meters", "zone_offset":0.0, "constituents":{"M2":{"amp":1.0, "phase":0.0}}}
    clock_constituents = {"M2":constituents["M2"]}    
    # theoretically only valid for 2000 and 2001, but we don't care
    return dump_station_years(clock_station, 2000, 2001, clock_constituents, 0.0, file=file)

def dump_station_offset(name, reference_station_name,  time_offset, level_offset, level_scale, prev_name=None, file=None):
    prev_name = prev_name if prev_name is not None else "NULL"
    print(dedent(f"""
                    tidal_offset station_{name}_offset = {{
                        .time_offset = {time_offset:.0f},
                        .level_offset = {level_offset:.5f},
                        .level_scale= {level_scale:.5f},
                    }};

                    tidal_station station_{name} = {{                       
                            .name = station_{reference_station_name}_name,
                            .previous = &{prev_name},
                            .harmonic = &station_{reference_station_name}_data,                        
                            .offset = &station_{name}_offset,
                    }};
        """), file=file)
    return f"station_{name}"
    
    

def dump_station_years(station, min_year, max_year, constituents, min_amp,  include_tests=True, file=None):
    name = station["name"]
    c_name = make_c_name(name)
    
    year_data = []
    for year in range(min_year, max_year):
        amps, phases, speeds = extract_cycles(station, year, constituents, min_amp)
        test_times, test_tides, mean_error, neaps_range, springs_range = generate_tests(station, year, constituents, phases, speeds, amps)
        year_data.append({"year":year, "amps":amps, "phases":phases, "speeds":speeds, "mean_error":mean_error, "test_times":test_times, "test_tides":test_tides, "neaps_range":neaps_range, "springs_range":springs_range})
    
    speeds = year_data[0]["speeds"] # always constant
    neaps_range = year_data[0]["neaps_range"]
    springs_range = year_data[0]["springs_range"]
    mean_error = sum([y["mean_error"] for y in year_data]) / len(year_data)
    n_constituents = len(speeds)
    # concatenate all the amps and phases
    amps = []
    phases = []
    test_times = []
    test_tides = []
    for y in year_data:
        amps += y["amps"]
        phases += y["phases"]
        test_times += y["test_times"]
        test_tides += y["test_tides"]
    
    # quantize the amps and phases
    amps = get_seq(16, MAX_AMP, amps)
    phases = get_seq(16, MAX_PHASE, phases)
    speeds = float_seq(speeds)

    
    speed_name = f"station_{c_name}_{min_year}_speed"
    print(dedent(f"""                 
                    /* Mean error for {name} in {min_year}-{max_year} is approximately {mean_error:.5f}m */
                    char station_{c_name}_{min_year}_name [] = "{name}";                    
                    float station_{c_name}_{min_year}_speed [] = {{{speeds}}};                
                    uint16_t station_{c_name}_{min_year}_amp [] = {{{amps}}};
                    uint16_t station_{c_name}_{min_year}_phase [] = {{{phases}}};
                    tidal_harmonic station_{c_name}_{min_year}_data = {{
                            .base_year = {min_year},
                            .n_years = {max_year-min_year},
                            .lat = {station["lat"]},
                            .lon = {station["lon"]},
                            .neaps_range = {neaps_range},
                            .springs_range = {springs_range},
                            .offset = {station["offset"]},
                            .speeds = {speed_name},
                            .amps = station_{c_name}_{min_year}_amp,
                            .phases = station_{c_name}_{min_year}_phase,
                            .n_constituents = {n_constituents},
                            .mean_error = {mean_error},
                        
                    }};                                                    
"""), file=file)
    
    if include_tests:
        print(dedent(f"""
                    #ifdef TIDE_DEBUG
                    time_t station_{c_name}_{min_year}_test_times [] = {{{", ".join([str(t) for t in test_times])}}};
                    float station_{c_name}_{min_year}_test_tides [] = {{{", ".join([str(t) for t in test_tides])}}};
                    #endif
                """), file=file)    
    
    station_data = {"name":f"station_{c_name}_{min_year}", "mean_error":mean_error, "neaps_range":neaps_range, "springs_range":springs_range, "offset":station["offset"]}
    return station_data



def finalise_tides(prev_name, file=None):
    print(dedent(f"""
                    tidal_station * tidal_stations  = &{prev_name};                    
                """), file=file)
