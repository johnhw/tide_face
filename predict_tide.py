import math, time

def unpack_tz(tz):
    return tz//100, tz%100

def epoch(year):
    """Return the Unix time at the start of the year"""
    return time.mktime((year, 1, 1, 0, 0, 0, 0, 0, 0))

def rads_per_second(degrees_per_hour):
    return math.radians(degrees_per_hour/3600)

def seconds_tz(tz):
    """Return the number of seconds in the timezone"""
    hour, min = unpack_tz(tz)
    return hour * 3600 + min * 60

def predict_tide(t, constituents, station, d=0, epoch_year=None):
    """Predict the tide at a given time t, using the constituents
    and station data"""

    
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
    tide = station["offset"] if d==0 else 0
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

def find_tide_event(t0, t1, constituents, station, epoch_year=None):
    """Find the nearest high/low water event to time t"""
        # compute the tide at the start and end of the interval
    tide0 = predict_tide(t0, constituents, station, d=1, epoch_year=epoch_year)
    tide1 = predict_tide(t1, constituents, station, d=1, epoch_year=epoch_year)
    if tide0*tide1>0:        
        print("NO!")
        return None    
    
    # do a binary search to find the event approximately
    for i in range(3):        
        t = (t0 + t1) / 2        
        tide = predict_tide(t, constituents, station, d=1, epoch_year=epoch_year)    
        t0, t1 = (t0, t) if tide*tide0<0 else (t, t1)
        
    # refine via Newton's method
    t_d = predict_tide(t, constituents, station, 1, epoch_year)
    t_d2 = predict_tide(t, constituents, station, 2, epoch_year)
    for i in range(3):        
        t = t - t_d / t_d2                
        t_d = predict_tide(t, constituents, station, 1, epoch_year)        
        t_d2 = predict_tide(t, constituents, station, 2, epoch_year)
    tide = predict_tide(t, constituents, station, 0, epoch_year)
    
    # return the time and tide level
    return t_d2<0, t, tide
        
    



def find_tide_events(t, bracket, constituents, station, epoch_year=None):
    """Find the n events in the bracket around time t.
    Bracket is the integer max number of events before/after t to search"""
    tidal_period = 12.4206012 * 3600 * 0.5 # guess for the tidal period in seconds
    events = {}
    
    for i in range(-bracket, bracket+1):
        t0 = t + i * tidal_period
        res = find_tide_event(t0-tidal_period/2, t0+tidal_period/2, constituents, station, epoch_year)
        if res:
            high, t1, level = res
            events[t1] = (high, t1, level)
    sorted_events = sorted(events.values(), key=lambda x:x[1])  
    return sorted_events
        