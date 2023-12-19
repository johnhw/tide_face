#ifndef __TIDE_BASE_H__
#define __TIDE_BASE_H__
#include <stdint.h>
#include <time.h>

#define TIDE_DEBUG 1
#define DAY_SECONDS 86400
#define HOUR_SECONDS 3600
#define MINUTE_SECONDS 60
#define YEAR_SECONDS 31536000
#define MIN_EVENT_GAP_SECONDS 3600

#define MAX_TIDE_AMP 12.0f
#define MAX_TIDE_SPEED 0.001f
#define MAX_TIDE_PHASE 6.283185307179586f
#define M_PI 3.14159265358979323846
#define UNQUANTIZE_AMP(X) ((X/65535.0f)*MAX_TIDE_AMP)
#define UNQUANTIZE_PHASE(X) ((X/65535.0f)*MAX_TIDE_PHASE)

// meters
#define MAX_TIDE_ERROR 0.1f 
#define MAX_TIDE_EVENTS 6

#define STATION_TYPE_NONE 0
/* Full harmonic station */
#define STATION_TYPE_HARMONIC 1
/* Offsets from a reference station, 
including time + level shifts (secondary ports) */
#define STATION_TYPE_REFERENCE 2
/* Station where we only know the time of high water */
#define STATION_TYPE_CLOCK 3

typedef struct tidal {
        uint8_t type;
        char *name;
        int base_year;
        int n_years;
        float lat;
        float lon; 
        float neaps_range;
        float springs_range;
        float offset;   
        float *speeds;
        uint16_t *amps; // amplitude for year base_year+i = amps[n_constituents*i]
        uint16_t *phases;
        uint8_t n_constituents;
        float mean_error;
        struct tidal *previous;
} tidal;

tidal  *tidal_stations;

/* Tidal event enumeration */
#define TIDE_NONE 0 
#define TIDE_HIGH 1
#define TIDE_LOW 2

/* A tidal event; high/low water */
typedef struct tidal_event 
{
    uint8_t type; /* TIDE_NONE, TIDE_HIGH, TIDE_LOW */
    time_t time; /* seconds since epoch */
    float level; /* m */
    float neap_spring; /* 0.0 -> 1.0 */
} tidal_event;

/* Tide prediction table for 24 hours before and 48 hours after midnight on a given day */
typedef struct tide_table {
    time_t base_time; /* midnight on the day in question */
    tidal *station; /* tidal station */
    float levels[72]; /* hourly tide levels */
    tidal_event events[3][MAX_TIDE_EVENTS]; /* HW/LW events for yesterday, today, tomorrow */
} tide_table;

float find_tide_event_near(tidal *station, tidal_event *event, time_t t0, time_t t1, float ntide);
void populate_tide_table(tide_table *table, tidal *station, time_t base_time, int tz_hours, int tz_mins);
float add_tide_event(tidal *station, time_t t, tidal_event *event, tidal_event *events, float last_tide);
void fill_day_tide_table(tidal_event *events, float *levels, tidal *station, time_t t0);
float predict_tide(uint32_t t, tidal *station, int d);
void test_tides(tidal *station, time_t *times, float *levels);
void get_tide_events_near(time_t t, tide_table *table, tidal_event **prev, tidal_event **next);
float interpolate_tide_table(time_t t, tide_table *table);
time_t make_time(uint32_t year, uint32_t month, uint32_t day, uint32_t hour, uint32_t minute, uint32_t second);
tidal *find_tidal_station(char *name, int year);




#endif