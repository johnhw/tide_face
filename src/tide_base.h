#ifndef __TIDE_BASE_H__
#define __TIDE_BASE_H__
#include <stdint.h>
#include <time.h>

#define TIDE_DEBUG 1

/* Time constants */
#define DAY_SECONDS 86400
#define HOUR_SECONDS 3600
#define MINUTE_SECONDS 60
#define YEAR_SECONDS 31536000
#define MIN_EVENT_GAP_SECONDS 3600

#define M_PI 3.14159265358979323846

/* De-quantization constants for 16 bit storage */
#define MAX_TIDE_AMP 12.0f
#define MAX_TIDE_PHASE 6.283185307179586f
#define UNQUANTIZE_AMP(X) ((X/65535.0f)*MAX_TIDE_AMP)
#define UNQUANTIZE_PHASE(X) ((X/65535.0f)*MAX_TIDE_PHASE)

// meters
#define MAX_TIDE_ERROR 0.1f 
// per day
#define MAX_TIDE_EVENTS 6


struct tidal_harmonic;

/* Wrapper for a tidal station */
typedef struct tidal_station
{    
    char *name;
    struct tidal_offset *offset;  
    struct tidal_harmonic *harmonic; 
    struct tidal_station *previous;
} tidal_station;

/* Simple offset, like Dover+02:15 */
/* Also used for CLOCK stations */
typedef struct tidal_offset
{
    float time_offset;
    float level_offset;
    float level_scale;    
} tidal_offset;


typedef struct tidal_harmonic {
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
        /* Amplitudes and phases are per year, stored as a [n_years, n_constituents] flattened array */
        uint16_t *amps; // amplitude for year base_year+i = amps[n_constituents*i]
        uint16_t *phases;
        uint8_t n_constituents;
        float mean_error;        
} tidal_harmonic;

tidal_station  *tidal_stations;

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

#define TIDE_TABLE_TIMES 72 

/* Tide prediction table for 24 hours before and 48 hours after midnight on a given day */
typedef struct tide_table {
    time_t base_time; /* midnight on the day in question */
    tidal_station *station; /* tidal station */
    float levels[TIDE_TABLE_TIMES]; /* hourly tide levels */
    tidal_event events[3][MAX_TIDE_EVENTS]; /* HW/LW events for yesterday, today, tomorrow */    
} tide_table;

float find_tide_event_near(tidal_station *station, tidal_event *event, time_t t0, time_t t1, float ntide);
void populate_tide_table(tide_table *table, tidal_station *station, time_t base_time, int tz_hours, int tz_mins);
float add_tide_event(tidal_station *station, time_t t, tidal_event *event, tidal_event *events, float last_tide);
void fill_day_tide_table(tidal_event *events, float *levels, tidal_station *station, time_t t0);
float predict_tide(time_t t, tidal_station *h_station, int d);
void test_tides(tidal_station *station, time_t *times, float *levels);
void get_tide_events_near(time_t t, tide_table *table, tidal_event **prev, tidal_event **next);
float interpolate_tide_level(time_t t, tide_table *table);
float interpolate_tide_rate(time_t t, tide_table *table);
time_t make_time(uint32_t year, uint32_t month, uint32_t day, uint32_t hour, uint32_t minute, uint32_t second);
tidal_station *find_tidal_station(char *name);
void update_range(tidal_event *events, float *hw, float *lw);

#endif