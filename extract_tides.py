import json, os, math 
import click, time 


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
        #for i in range(1):
            # get time at start of the hour
            #gm_t = time.gmtime(time.time())
            #t = time.mktime((gm_t[0], gm_t[1], gm_t[2], gm_t[3]+i, 0, 0, 0, 0, 0))
            #print(target_station["name"], time.asctime(time.gmtime(t)), t, predict_tide(t, constituents, station))
            t = time.time() 
            print(t, f"{predict_tide(t, constituents, station):.6f}")
    return all_stations 
    

if __name__=="__main__":
    cli()