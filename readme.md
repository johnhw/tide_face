# Tidal predictions for SensorWatch

**WARNING: PREDICTIONS MADE WITH THIS SOFTWARE ARE NOT SUITABLE FOR NAVIGATION PURPOSES. ALWAYS CHECK TIDAL INFORMATION FROM OFFICIAL ADMIRALITY SOURCES.**

## Installation

## Instructions

To use the software you need to:
* Install `libtcd` and acquire `tcd` harmonics files (e.g. from the `xtides-data` package on Debian)
* Convert the `tcd` files to JSON using `tcd_extract.py`
* Extract the tide data for the stations you want to use using `extract_tides.py`
* Compile the firmware with the tide data baked in.

Once installed, you need to include the face in a configuration. There are two new faces:

* `tidal_clock` which is just like the simple time face, but replaces the seconds with a graphical tide height indicator in low power mode, and can also be shown by long pressing the alarm button.
* `tides` which gives the predictions for the current station.

### `tidal_clock`

The tide level is shown in the seconds indicator.
 


### `tides` face

The tides faces shows HW/LW events, starting with the last event before the current time. The face shows the time of the event, the tide height, and the type of tide (high/low, springs/neaps). The face also shows the next five events. 


```
        hi n 
    04:31 42
```
Previous event is high water, neaps, at 04:31, 4.2m

```
        lo s
    10:31 02
```
Next event is low water, springs, at 10:31, 0.2m

```

24H  hi = 
    07:19 32
```

Next event is 05:19 tomorrow, mid-tide, 3.2m


Tides less than 0 show as `-3` to mean `-0.3m`. Tides less than -1m are shown as `--`. Tides of 10m or greater show as `99` to mean `>9.9m`.
If time is shown in UTC, the LAP and BELL indicator will be shown.

Pressing `ALARM` will cycle through the next events. Tide events for tomorrow are shown with the `24H` indicator. Tides are not shown for the day after tomorrow. 

Hold `ALARM` to show the current station. Pressing `LIGHT` while the station is shown will enter the settings mode.

### Settings mode
You can scroll through the settings using `MODE`. Pressing `LIGHT` will cycle through the options for the current setting. Pressing `ALARM` will save the current setting and move to the next setting. Hold `MODE` to exit settings mode.
 The settings menu goes: `station`, `unit`, `utc`.

The menu will initially show the scrolling station name:
```
Millpo
```

The next page will show
```
    me:lt
```

which means meters, local time. The options can be `me/ft` and `lt/uc` for meters/feet and local/UTC time respectively.


### Computation
The face computes tide tables, rather than computing tide levels on demand. Tide tables are recomputed either once a day or whenever the specified station changes. This is quite an expensive operation, so it is not done regularly. Hourly tide levels are computed for the preceding 24 hours and next 48 hours from 00:00 on the current day, and tidal events (HW/LW) in that interval are also computed. Real-time tidal displays are based on interpolation between the hourly tide levels.

### Units
Units are always computed internally in metres. All configuration etc. as described below is only supported in meters. The tide heights are converted to feet or metres depending on the face's `unit` setting. The tide times are always computed in UTC but will be shown converted to the watch's current timezone unless the `utc` option is set.

## Getting tide data
`tide_face` uses harmonics files that are used by [`xtide`](http://www.flaterco.com/xtide/). These `tcd` files hold the tidal constituents for various stations. 

### Downloading TCD data
You can download these e.g. from a Debian repository `sudo apt install xtide-data xtide-data-nonfree`. You can also download them from [here](http://www.flaterco.com/xtide/files.html#harmonics) or [here](https://tidesandcurrents.noaa.gov/tide_predictions.html). The files are usually named `harmonics_<station>.tcd`.

### Converting TCD to JSON
`tide_face` uses a JSON format for the harmonics files. You can convert the files using the `tcd_extract.py` script. It extracts JSON data from `tcd` files. By default, it will scan all of the files in `/usr/share/xtide` and output the JSON data to the current path. You can specify a different directory as the first argument to the script. 

`tcd_extract.py` needs `libtcd` to be installed. You can install it using `sudo apt install libtcd-dev` on Debian. You can also download the source code from [here](http://www.flaterco.com/xtide/files.html#libtcd) and compile it yourself. You may need to set the path to the shared library at the top of `tcd_extract.py` if it is not in the default location.

### Extracting tide data
Generally, you only want to store a small amount of tide data on the watch itself as it is quite voluminous. The `extract_tides.py` script will extract the tide data for a given list of stations. By default, it will extract tidal data for the next five years; you can configure this with the `--years` option. You can adjust the base year if you want with `base_year`, but this is unlikely to be necessary.

```
python extract_tides.py --years 5 --stations "Millport Portpatrick Tobermory Dover Belfast"
```

Note: tidal data has annual corrections, so specific constants are needed for each calendar year. If you don't have the correct year's data stored, the tide data will be less accurate (usually not critically so, but it will be off by several minutes -- it may be worse at some stations).

You may also set a "minimum amplitude" for harmonics; a higher threshold will result in fewer harmonics being stored, but the tide data will be less accurate. The default value is 0.02m, which is probably fine for most purposes. You can adjust this with the `--min-amplitude` option.

This creates a C file, `tide_base.c`. This is included in `tide_base.c` and compiled into the firmware. You can also use the `--output` option to specify a different output file. 

#### Naming stations
You can give a short name to a station (to be shown on screen), by prefixing the station name with the short name, followed by `=`. For example, `mpot=Millport` will show the station as "mpot" on the watch. If you don't specify a short name, the station name will be used.

#### Secondary ports
You can specify secondary ports (i.e. corrections from a known station) by adding a `+` after the station name, followed by the correction in minutes. For example, `LittleCumbrae=Millport+5` will add 5 minutes to the tide times at Millport. You can also specify a negative correction, e.g. `LittleCumbrae=Millport-5`. You can specify hours in the format `Finnart=Millport+01:05` or just use minutes, e.g. `Finnart=Millport+65`. You may also give full secondary port corrections, in the format:

```
secondary=primary:t1&t2=mins,t3&t4=mins,mhws=adj,mlws=adj
```

like `Finnart=Millport:0000&0600=-40,1200&1800=-31,4.0=+0.7,2.2=-0.5`. This will set the tide times at Finnart to be 40 minutes earlier at 00:00 and 06:00, 31 minutes later at 12:00 and 18:00, and will adjust the heights of the 4.0m high water springs and 2.2m low water springs by 0.7m and -0.5m respectively. 

#### Basic tide clock
If you have no tidal data at all, but you know when high water was, you can use the special CLOCK station followed by an ISO 8601 date/time. This will use the specified time as the high water time, and will use the standard 6 hour 12.5 minute interval between high and low water. Tidal heights will always be shown as between -1 and +1 metres. 

```
python extract_tides.py --stations ANewPlace=CLOCK:2023-01-01T12:00
```

If you know the time and height of high water and low water, you can specify them both, e.g. `ANewPlace=CLOCK:2023-01-01T12:00,4.0,2023-01-01T18:00,2.0`. Note that a basic tide clock is not very accurate, especially over longer periods of time.


### CLI reference
```
usage: extract_tides.py [-h] [--years YEARS] [--stations STATIONS]
                        [--min-amplitude MIN_AMPLITUDE] [--base-year YEAR]
                        [--output OUTPUT]
```                

## License

This software is licensed under the MIT license. See `LICENSE` for details. The script to convert `xtide`-format tcd files to JSON is licensed under the GPL v2.0 license as it is based on the `libtcd` headers. See `tcd_extract/LICENSE` for details.

## Warning
This software is not suitable for navigation purposes. Always check tidal information from official Admirality sources. There may be errors in the software, and the data may be out of date. The software is provided as-is, with no warranty of any kind. Use at your own risk. You can verify the tidal data against `xtide` or external sources if you wish (see "viewing debug information") but any tests only show that the specific times in question are correct, not that the software is correct in general.