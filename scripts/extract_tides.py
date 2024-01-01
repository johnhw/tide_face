import json
import click, time 
from station_parser import parse_station
from rich.table import Table
from rich.console import Console
from rich import print
from dump_tides import  dump_station_years, dump_clock_station, finalise_tides, dump_station_offset
from rich.logging import RichHandler
import logging
FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

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
        log.warning(f"No base year specified, using current year ({base_year})")
        
    log.info(f"Extracting data from {input_file} to {output_file} for {base_year} to {base_year+years}")

    # load the data
    with open(input_file, "r") as f:
        data = json.load(f)
    log.info(f"Read {len(data['tide_records'])} stations and {len(data['constituents'])} tidal constituents from {input_file}")

    all_stations = data["tide_records"]    
    cli_stations = parse_station(stations)    
    

    # extract all of the base stations we need
    base_stations = {}
    for station in cli_stations:        
        alias, details = station        
        base_stations[details.base_station] = None

    log.info(f"Extracting data for {len(cli_stations)} tidal stations from {len(base_stations)} reference stations")

    # extract the fixed constituents
    constituents = {}    
    for constituent in data["constituents"]:
        name = constituent["constituent_name"]
        constituents[name] = ({"speed":constituent["speed"], "n":constituent["constituent_number"], "name":name, "years":constituent["years"]})    
                        
    station_full_names = {}
    # create a table for the reference station data
    table = Table(title="Reference Stations")
    table.add_column("Name", justify="left", style="cyan")
    table.add_column("Lat.", justify="right", style="magenta")
    table.add_column("Lon.", justify="right", style="magenta")    
    table.add_column("Offset", justify="right", style="green")
    table.add_column("RMS error", justify="right", style="yellow")
    table.add_column("Np. range", justify="center", style="blue")
    table.add_column("Sp. range", justify="center", style="blue")

    with open(output_file, "w") as f:
        # write the clock station
        prev_name = dump_clock_station(constituents, file=f)        
        table.add_row("CLOCK", "0.0°", "0.0°", "0.0m", "0.0m", "2.0m", "2.0m")
        
        # write all of the base (harmonic) stations
        for possible_station in base_stations:            
            for station in all_stations:
                # only process type 1 for now                         
                if station["record_type"] == 1 and station["name"].startswith(possible_station):                                
                    station_data = {v:station[k] for k,v in station_fields.items()}                            
                    station_data["constituents"] = {c_name:{"amp":amp, "phase":epoch} for c_name, amp, epoch in zip(constituents.keys(), station["amplitude"], station["epoch"])}                                            
                    processed_data = dump_station_years(station_data, base_year, base_year+years, constituents, min_amplitude, file=f)   
                    base_stations[possible_station] = processed_data["name"]                    
                    table.add_row(station["name"], f"{station_data['lat']:.2f}°", f"{station_data['lon']:.2f}°", f"{station_data['offset']:.1f}m", f"{processed_data['mean_error']:.4f}m", f"{processed_data['neaps_range']:.2f}m", f"{processed_data['springs_range']:.2f}m")

        print(table)

        table = Table(title="Tidal Stations")
        table.add_column("Name", justify="left", style="white")
        table.add_column("Reference", justify="left", style="cyan")
        table.add_column("Level offset", justify="right", style="green")
        table.add_column("Level scale", justify="right", style="green")
        table.add_column("Time offset", justify="right", style="blue")
        # now write the offset stations as a linked list
        # using the names as aliases
        prev_name = None
        for station in cli_stations:
            alias, details = station
            prev_name = dump_station_offset(alias, base_stations[details.base_station], details.seconds_offset, details.level_offset, details.level_scale, prev_name=prev_name, file=f)
            table.add_row(alias, details.base_station, f"{details.level_offset:.2f}m", f"{details.level_scale:.2f}", f"{details.seconds_offset:.0f}s")
        print(table) 
        # now write all of the aliases/offsets
        finalise_tides(prev_name, file=f)
    log.info(f"Finished writing {output_file}")
    

if __name__=="__main__":
    cli()