import json
import click, time 
import re

from dump_tides import  dump_station_years, dump_clock_station, finalise_tides

station_fields = {"latitude":"lat", "longitude":"lon", "name":"name", "station_id":"id", "zone_offset":"zone_offset", "datum_offset":"offset", "level_units":"units"}

# extract type 2 records (reference stations with offsets)
@click.command()
@click.argument("input-file", type=click.Path(exists=True))
@click.option("--min-amplitude", type=float, default=1e-3, help="Minimum amplitude to include in output")
@click.option("--stations", type=str, default=None, help="Stations to extract, space separated")
@click.option("--base-year", type=int, default=None, help="Base year to extract from")
@click.option("--years", type=int, default=5, help="Number of years to extract")
@click.option("--output-file", type=click.Path(), default="src/tide_data.c", help="Output file")
def cli(input_file, stations, years, base_year, min_amplitude, output_file):        
    """Extracts tidal data form a TCD converted JSON file into
    a C source file.
    """
    if base_year is None:
        base_year = time.gmtime()[0]
        print(f"Using current year {base_year}")

    # load the data
    with open(input_file, "r") as f:
        data = json.load(f)

    all_stations = data["tide_records"]    
    stations = stations.split(" ") 

    # extract the fixed constituents
    constituents = {}    
    for constituent in data["constituents"]:
        name = constituent["constituent_name"]
        constituents[name] = ({"speed":constituent["speed"], "n":constituent["constituent_number"], "name":name, "years":constituent["years"]})    
                    
    with open(output_file, "w") as f:
        # write the clock station
        prev_name = dump_clock_station(constituents, file=f, prev_name=None)        
        
        for station in all_stations:
            # only process type 1 for now
            for possible_station in stations:
                if station["record_type"] == 1 and station["name"].startswith(possible_station):                                
                    station_data = {v:station[k] for k,v in station_fields.items()}                            
                    station_data["constituents"] = {c_name:{"amp":amp, "phase":epoch} for c_name, amp, epoch in zip(constituents.keys(), station["amplitude"], station["epoch"])}                                            
                    prev_name = dump_station_years(station_data, base_year, base_year+years, constituents, min_amplitude, file=f, prev_name=prev_name)                       
        finalise_tides(prev_name, file=f)
    

if __name__=="__main__":
    cli()