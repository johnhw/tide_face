import json, os, math 
import click, time 


def predict_tide(t, constituents, station, d=0, epoch_year=None):
    """Predict the tide at a given time t, using the constituents
    and station data"""
    def unpack_tz(tz):
        return tz//100, tz%100

    def epoch(year):
        """Return the Unix time at the start of the year"""
        return time.mktime((year, 1, 1, 0, 0, 0, 0, 0, 0))

    def rads_per_second(degrees_per_hour):
        return math.radians(degrees_per_hour/3600)
    
    # get the epoch (start of year, 1st Jan) for the year this is in
    if epoch_year is None:
        year = time.gmtime(t)[0]
    else:
        year = epoch_year
    t = t - epoch(year)    
    deriv_shift = (math.pi / 2) * d
    # compute how many seconds to add to the phase
    hour, min = unpack_tz(station["zone_offset"])    
    time_shift = (hour * 3600 + min * 60)      
    tide = station["offset"]
    for k, v in station["constituents"].items():
        base = constituents[k]
        year_constituents = base["years"][str(year)]
        speed = rads_per_second(base["speed"])        
        amp = v["amp"] * year_constituents["node_factor"]        
        phase = math.radians(year_constituents["equilibrium"]-v["phase"]) 
        term = amp * math.cos(speed * (t - time_shift) + phase + deriv_shift)                
        tide += term * (speed ** d) # chain rule
    # convert to meters if required 
    if station["units"]=="feet":
        tide *= 0.3048
    return tide 

def compute_error_for_year(station, constituents, year, min_year):
    # iterate over each hour in the year
    error = 0
    t = time.mktime((year, 1, 1, 0, 0, 0, 0, 0, 0))
    for hour in range(0, 365*24):
        t = t + 3600
        tide = predict_tide(t, constituents, station)        
        tide2 = predict_tide(t, constituents, station, epoch_year=min_year)
        error += abs(tide - tide2)
    return error / (365*24)

def quantize(val, quantize):
    max_val, step = quantize
    return math.floor((val / max_val) / step) * step * max_val

import copy
def round_station(station, min_amp, quantize_amp, quantize_phase):
    """Round the amplitude and phase of the constituents"""
    amp_phase = {}
    count_zero = 0
    station = copy.deepcopy(station)
    for c_name in station["constituents"]:
        amp = quantize(station["constituents"][c_name]["amp"], quantize_amp)
        epoch = quantize(station["constituents"][c_name]["phase"], quantize_phase)
        if amp<min_amp:
            amp = 0
            count_zero += 1
        amp_phase[c_name] = {"amp":amp, "phase":epoch}    
    station["constituents"] = amp_phase
    print(f"Zeroed {count_zero} constituents of {len(station['constituents'])}, remaining: {len(station['constituents'])-count_zero}")
    return station

def round_constituents(constituents, quantize_amp, quantize_phase, quantize_speed):
    """Round the amplitude and phase of the constituents"""
    amp_phase = {}
    constituents = copy.deepcopy(constituents)
    for c_name in constituents:
        speed = quantize(constituents[c_name]["speed"], quantize_speed)
        constituents[c_name]["speed"] = speed
        years = constituents[c_name]["years"]
        for year in years:
            node_factor = quantize(years[year]["node_factor"], quantize_amp)
            equilibrium = quantize(years[year]["equilibrium"], quantize_phase)
            years[year] = {"node_factor":node_factor, "equilibrium":equilibrium}
        constituents[c_name]["years"] = years        
    return constituents

def compute_error_quantize(station, constituents, year, min_amp=1e-3, quantize_amp=(4,1e-3), quantize_phase=(361,1e-3), quantize_speed=(0.005, 1e-3)):
    error = 0
    t = time.mktime((year, 1, 1, 0, 0, 0, 0, 0, 0))
    q_station = round_station(station, min_amp, quantize_amp, quantize_phase)
    q_constituents = round_constituents(constituents, quantize_amp, quantize_phase, quantize_speed)
    for hour in range(0, 365*24):
        t = t + 3600
        tide = predict_tide(t, constituents, station)
        tide2 = predict_tide(t, q_constituents, q_station)
        error += abs(tide - tide2)
    return error / (365*24)

def compute_error(station, constituents, min_year, max_year):
    """Compare the error in the tide prediction for a station
    when the constituents are used for the year they were measured
    and when they are used for the year they are being predicted for"""

    for year in range(min_year, max_year):
        error = compute_error_for_year(station, constituents, year, min_year)
        print(f"{station['name']} {year} {error}")
    




station_fields = {"latitude":"lat", "longitude":"lon", "name":"name", "station_id":"id", "zone_offset":"zone_offset", "datum_offset":"offset", "level_units":"units"}
@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--min-amplitude", type=float, default=1e-3, help="Minimum amplitude to include in output")
@click.option("--station", type=str, default=None, help="Station to extract")
def cli(input_file, station, min_amplitude=1e-3):
    """This script extracts tidal data form a TCD converted JSON file"""
    with open(input_file, "r") as f:
        data = json.load(f)
    stations = data["tide_records"]
    all_stations = []
    station_name = station
    constituents = {}
    c_names = []
    
    for constituent in data["constituents"]:
        name = constituent["constituent_name"]
        constituents[name] = ({"speed":constituent["speed"], "n":constituent["constituent_number"], "name":name, "years":constituent["years"]})
        c_names.append(name)
    
    speeds = [constituents[c_name]["speed"] for c_name in constituents]
    print("Max speed", max(speeds))
    min_year = 2023
    max_year = 2100
    for station in stations:
        # only process type 1 for now
        if station["record_type"] == 1:# and station["name"].startswith(station_name):
            amp_phase = {}
            for c_name, amp, epoch in zip(c_names, station["amplitude"], station["epoch"]):                            
                amp_phase[c_name] = {"amp":amp, "phase":epoch}
            station_data = {v:station[k] for k,v in station_fields.items()}        
            station_data["constituents"] = amp_phase
            min_amp = 3e-2 
            quantize_amp = (2, 0.00002)
            quantize_phase = (360, 0.00002)
            quantize_speed = (180, 0.00002**2)

            # #compute_error(station_data, constituents, min_year, max_year)
            # for min_amp in [1e-4, 1e-3, 1e-2, 1.5e-2]:
            #     for quantize_amp in [(2, 0.00002)]:
            #         quantize_phase = (360, 0.00002)
            #         quantize_speed = (180, 0.00002**2)
            #         #for quantize_phase in [(361,1e-3), (361,1e-2), (361,1e-1), (361,1e-0)]:
            #             #for quantize_speed in [(0.005, 1e-3), (0.005, 1e-2), (0.005, 1e-1), (0.005, 1e-0)]:
            error = compute_error_quantize(station_data, constituents, 2023, min_amp, quantize_amp, quantize_phase, quantize_speed)
            print(f"{station['name']} {min_amp} {quantize_amp} {quantize_phase} {quantize_speed} {error}")
                    
         
    

if __name__=="__main__":
    cli()