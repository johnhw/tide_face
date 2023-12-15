
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
    