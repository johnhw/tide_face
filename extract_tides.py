import json, os, math 
import click, time 


def predict_tide_debug2(t, constituents, station):
    """Predict the tide at a given time t, using the constituents
    and station data"""
    tide = 0
    # compute the year this is in, and get seconds since the start of the year
    # note: times are in UTC
    for s0 in [-1, 0, 1]:
        year = time.gmtime(t)[0]
        t = t - epoch(year+s0)    
        hour, min = unpack_tz(station["zone_offset"])    
        t = t + ( hour * 3600 + min * 60) # NB check signs!    
        for s1 in [-1, 1]:
            for s2 in [-1, 1]:
                for s3 in [-1, 1]:
                    for s4 in [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75]:                    
                        tide = 0                    
                        for k, v in constituents.items():
                            if k in station["constituents"]:
                                year_constituents = v["years"][str(year)]
                                constituent = station["constituents"][k]
                                amp = constituent["amp"] * year_constituents["node_factor"] 
                                phase = math.radians(s1*constituent["phase"] + s2* year_constituents["equilibrium"]) # nb check signs!
                                speed = rads_per_second(v["speed"])
                                tide += amp * math.cos(s3*speed * t + phase + math.pi*s4)
                        print(f"{s0}\t{s1}\t{s2}\t{s3}\t{s4}\t{tide+station['offset']}")
    return tide + station["offset"]

def predict_tide_debug(t, constituents, station):
    """Predict the tide at a given time t, using the constituents
    and station data"""
    def unpack_tz(tz):
        return tz//100, tz%100

    def epoch(year):
        """Return the Unix time at the start of the year"""
        return time.mktime((year, 1, 1, 0, 0, 0, 0, 0, 0))

    def rads_per_second(degrees_per_hour):
        return math.radians(degrees_per_hour/3600)
    tide = 0
    # compute the year this is in, and get seconds since the start of the year
    # note: times are in UTC
    print(f"Start time: {t}")
    
    year = time.gmtime(t)[0]
    t = t - epoch(year)    
    hour, min = unpack_tz(station["zone_offset"])    
    phase_add = ( hour * 3600 + min * 60) # NB check signs!    
    print(f"Epoch: {epoch(year)}, Year: {year}")
    print(f"Phase add: {phase_add}")
    print(f"Since epoch: {t}")    
    print(f"Datum offset: {station['offset']}")

    
    tide = 0                    
    for k, v in constituents.items():
        if k in station["constituents"]:
            year_constituents = v["years"][str(year)]
            constituent = station["constituents"][k]
            amp = constituent["amp"] * year_constituents["node_factor"]
            phase = -(math.radians(constituent["phase"]) - phase_add * rads_per_second(v["speed"]))
            adj_phase = phase + math.radians(year_constituents["equilibrium"])
            if amp > 0:
                print(f"{k}\tamp: {constituent['amp']:4.5f}\tphase: {phase:4.3f}\tspeed:{rads_per_second(v['speed'])*10000:4.3f}\tNod: {year_constituents['node_factor']:4.6f}\tequilib {math.radians(year_constituents['equilibrium']):4.6f}\tadj_phase: {adj_phase:4.6f}") 
            
            speed = rads_per_second(v["speed"])
            tide += amp * math.cos(speed * t + adj_phase)
                    
    return tide + station["offset"]


def predict_tide(t, constituents, station):
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
    year = time.gmtime(t)[0]
    t = t - epoch(year)    
    # compute how many seconds to add to the phase
    hour, min = unpack_tz(station["zone_offset"])    
    phase_add = (hour * 3600 + min * 60) 
        
    tide = station["offset"]
    for k, v in station["constituents"].items():
        base = constituents[k]
        year_constituents = base["years"][str(year)]
        speed = rads_per_second(base["speed"])        
        amp = v["amp"] * year_constituents["node_factor"]        
        phase = math.radians(year_constituents["equilibrium"]-v["phase"]) - phase_add * speed
        tide += amp * math.cos(speed * t + phase)                
    # convert to meters if required 
    if station["units"]=="feet":
        tide *= 0.3048
    return tide 

station_fields = {"latitude":"lat", "longitude":"lon", "name":"name", "station_id":"id", "zone_offset":"zone_offset", "datum_offset":"offset", "level_units":"units"}
@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--min-amplitude", type=float, default=1e-3, help="Minimum amplitude to include in output")
@click.option("--station", type=str, default=None, help="Station to extract")
def cli(input_file, station, min_amplitude=1e-3):
    """This script extracts tidal data form a TCD converted
    JSON file"""
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
    
    for station in stations:
        # only process type 1 for now
        if station["record_type"] == 1:
            amp_phase = {}
            for c_name, amp, epoch in zip(c_names, station["amplitude"], station["epoch"]):            
                if amp > min_amplitude:
                    amp_phase[c_name] = {"amp":amp, "phase":epoch}
            station_data = {v:station[k] for k,v in station_fields.items()}        
            station_data["constituents"] = amp_phase
            all_stations.append(station_data) 

    target_station = None
    for station in all_stations:        
        if station["name"].startswith(station_name):
            print(station["name"])
            target_station = station             
            break 
    
    if target_station is not None:
        for i in range(1):
            # get time at start of the hour
            gm_t = time.gmtime(time.time())
            t = time.mktime((gm_t[0], gm_t[1], gm_t[2], gm_t[3]+i, 0, 0, 0, 0, 0))
            #print(target_station["name"], time.asctime(time.gmtime(t)), t, predict_tide(t, constituents, station))
            print(t, f"{predict_tide(t, constituents, station):.6f}")
    return all_stations 
    

if __name__=="__main__":
    cli()