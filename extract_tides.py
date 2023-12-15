import json, math
import click, time 
from textwrap import dedent
import re
import matplotlib.pyplot as plt
import numpy as np
import random
from scipy.optimize import curve_fit
from dump_tides import dump_station, dump_station_years
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
        print(constituent)
        nodes = [constituents[constituent]["years"][k]["node_factor"] for k in constituents[constituent]["years"]]
        ph_shift = [constituents[constituent]["speed"] * (24 * 365.25) for _ in constituents[constituent]["years"]] 
        eqs = [constituents[constituent]["years"][k]["equilibrium"] for k in constituents[constituent]["years"]]
        fig, ax = plt.subplots(2,1, figsize=(24,12))
        corrections = []
        while np.mean(np.abs(nodes))>0.05 and len(corrections)<3:
            node_fit = fit_sin(np.array(range(len(nodes))), np.array(nodes))
            
            ax[0].plot(nodes - np.mean(nodes), label=constituent)
            nodes = nodes - node_fit["fitfunc"](np.array(range(len(nodes))))
            ax[0].plot(nodes - np.mean(nodes), label=constituent)
            print(f"Avg. residual: {np.mean(np.abs(nodes))}")
            corrections.append({"amp":node_fit["amp"], "phase":node_fit["phase"], "freq":node_fit["freq"], "offset":node_fit["offset"]})
        
        ph_shift = np.array(ph_shift)                 
        prad = np.unwrap(np.radians(np.array(eqs)-np.array(ph_shift)%360))
        mean_shift = np.mean(np.diff(prad))        

        prad = prad - mean_shift * np.arange(len(prad))
        prad = prad - np.mean(prad)
        print(mean_shift)
        ax[1].plot(prad, label="phase")        
        ax[1].axhline(0, color="black")
        
        
        fig.savefig(f"node_{constituent}.png")

    


station_fields = {"latitude":"lat", "longitude":"lon", "name":"name", "station_id":"id", "zone_offset":"zone_offset", "datum_offset":"offset", "level_units":"units"}

# extract type 2 records (reference stations with offsets)
@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--min-amplitude", type=float, default=1e-3, help="Minimum amplitude to include in output")
@click.option("--station", type=str, default=None, help="Station to extract")
@click.option("--year", type=int, default=None, help="Year to extract")
def cli(input_file, station, year, min_amplitude):    
    """This script extracts tidal data form a TCD converted JSON file"""
    if year is None:
        year = time.gmtime()[0]
        print(f"Using current year {year}")

    station_name = station
    with open(input_file, "r") as f:
        data = json.load(f)
    stations = data["tide_records"]
    constituents = {}
    
    for constituent in data["constituents"]:
        name = constituent["constituent_name"]
        constituents[name] = ({"speed":constituent["speed"], "n":constituent["constituent_number"], "name":name, "years":constituent["years"]})

    
    #analyse_constituents(constituents)
            
    for station in stations:
        # only process type 1 for now
        if station["record_type"] == 1 and station["name"].startswith(station_name):            
            station_data = {v:station[k] for k,v in station_fields.items()}        
            station_data["constituents"] = {c_name:{"amp":amp, "phase":epoch} for c_name, amp, epoch in zip(constituents.keys(), station["amplitude"], station["epoch"])}                        
            #dump_station_years(station_data, year, year+5, constituents, min_amplitude)   
            for h, t, l in find_tide_events(time.time(), 5, constituents, station_data):
                print(f"{'HW' if h else 'LW'}\t{time.asctime(time.localtime(t))}\t{l:3.2f}m")      
            
    


if __name__=="__main__":
    cli()