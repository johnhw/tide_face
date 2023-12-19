import json, math
import click, time 
from textwrap import dedent
import re
import matplotlib.pyplot as plt
import numpy as np
import random
from scipy.optimize import curve_fit
from dump_tides import  dump_station_years, dump_clock_station, finalise_tides
from predict_tide import find_tide_event, find_tide_events

def node_curve(x, frequency, amplitude, phase, offset):
    return amplitude * np.sin(frequency * x + phase) + offset

def equilibrium_curve(x, increment, frequency, amplitude, phase):
    return amplitude * np.arctan(np.cos(frequency * x + phase), np.sin(frequency*x+phase)) + increment * x

def fit_sin(tt, yy):
    '''Fit sin to the input time sequence, and return fitting parameters "amp", "omega", "phase", "offset", "freq", "period" and "fitfunc"'''
    tt = np.array(tt)
    yy = np.array(yy)
    ff = np.fft.fftfreq(len(tt), (tt[1]-tt[0]))   # assume uniform spacing
    Fyy = abs(np.fft.fft(yy))
    guess_freq = abs(ff[np.argmax(Fyy[1:])+1])   # excluding the zero frequency "peak", which is related to offset
    guess_amp = np.std(yy) * 2.**0.5
    guess_offset = np.mean(yy)
    guess = np.array([guess_amp, 2.*np.pi*guess_freq, 0., guess_offset])

    def sinfunc(t, A, w, p, c):  return A * np.sin(w*t + p) + c
    popt, pcov = curve_fit(sinfunc, tt, yy, p0=guess)
    A, w, p, c = popt
    f = w/(2.*np.pi)
    fitfunc = lambda t: A * np.sin(w*t + p) + c
    return {"amp": A, "omega": w, "phase": p, "offset": c, "freq": f, "period": 1./f, "fitfunc": fitfunc, "maxcov": np.max(pcov), "rawres": (guess,popt,pcov)}

def analyse_constituents(constituents):
    # plot the data
    for constituent in constituents:        
        # print(constituent)
        # nodes = [constituents[constituent]["years"][k]["node_factor"] for k in constituents[constituent]["years"]]
        ph_shift = [constituents[constituent]["speed"] * (24 * 365.25) for _ in constituents[constituent]["years"]] 
        eqs = [constituents[constituent]["years"][k]["equilibrium"] for k in constituents[constituent]["years"]]
        # fig, ax = plt.subplots(2,1, figsize=(24,12))
        # corrections = []
        # while np.mean(np.abs(nodes))>0.05 and len(corrections)<3:
        #     node_fit = fit_sin(np.array(range(len(nodes))), np.array(nodes))
            
        #     ax[0].plot(nodes - np.mean(nodes), label=constituent)
        #     nodes = nodes - node_fit["fitfunc"](np.array(range(len(nodes))))
        #     ax[0].plot(nodes - np.mean(nodes), label=constituent)
        #     print(f"Avg. residual: {np.mean(np.abs(nodes))}")
        #     corrections.append({"amp":node_fit["amp"], "phase":node_fit["phase"], "freq":node_fit["freq"], "offset":node_fit["offset"]})
        
        ph_shift = np.array(ph_shift)                 
        prad = np.unwrap(np.radians(np.array(eqs)-np.array(ph_shift)%360))
        mean_shift = np.degrees(np.mean(np.diff(prad)))
        print(constituent, mean_shift)

        # prad = prad - mean_shift * np.arange(len(prad))
        # prad = prad - np.mean(prad)
        # print(mean_shift)
        # ax[1].plot(prad, label="phase")        
        # ax[1].axhline(0, color="black")
        
        
        # fig.savefig(f"node_{constituent}.png")

    


station_fields = {"latitude":"lat", "longitude":"lon", "name":"name", "station_id":"id", "zone_offset":"zone_offset", "datum_offset":"offset", "level_units":"units"}

# extract type 2 records (reference stations with offsets)
@click.command()
@click.argument("input-file", type=click.Path(exists=True))
@click.option("--min-amplitude", type=float, default=1e-3, help="Minimum amplitude to include in output")
@click.option("--stations", type=str, default=None, help="Stations to extract, space separated")
@click.option("--base-year", type=int, default=None, help="Base year to extract from")
@click.option("--years", type=int, default=5, help="Number of years to extract")
@click.option("--output-file", type=click.Path(), default="tide_data.c", help="Output file")
def cli(input_file, stations, years, base_year, min_amplitude, output_file):    
    
    """This script extracts tidal data form a TCD converted JSON file"""
    if base_year is None:
        base_year = time.gmtime()[0]
        print(f"Using current year {base_year}")

    with open(input_file, "r") as f:
        data = json.load(f)

    all_stations = data["tide_records"]    
    stations = stations.split(" ") 

    constituents = {}    
    for constituent in data["constituents"]:
        name = constituent["constituent_name"]
        constituents[name] = ({"speed":constituent["speed"], "n":constituent["constituent_number"], "name":name, "years":constituent["years"]})    
                    
    with open(output_file, "w") as f:
        prev_name = dump_clock_station(constituents, file=f, prev_name=None)
        analyse_constituents(constituents)
                
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