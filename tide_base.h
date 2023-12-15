#ifndef __TIDE_BASE_H__
#define __TIDE_BASE_H__
#include <stdint.h>
#include <time.h>

typedef struct tidal {
        char *name;
        int year;
        float lat;
        float lon; 
        float offset;   
        uint32_t *speeds;
        uint16_t *amps;
        uint16_t *phases;
        uint8_t n_constituents;
        float mean_error;
        struct tidal *previous;
} tidal;

tidal *tidal_stations = NULL;
#define REGISTER_TIDAL_STATION(X) (X)->previous = tidal_stations; tidal_stations = (X);

/* Tidal event enumeration */
#define TIDE_NONE 0 
#define TIDE_HIGH 1
#define TIDE_LOW 2

typedef struct tidal_event 
{
    uint8_t type;
    time_t time;
    float level;
} tidal_event;

/* Tide prediction table for 24 hours before and 48 hours after midnight on a given day */
typedef struct tide_table {
    time_t base_time;
    tidal *station; 
    float levels[72];
    tidal_event events[3][6];
} tide_table;

void populate_tide_table(tide_table *table, tidal *station, time_t base_time, int tz_hours, int tz_mins);


#define MAX_TIDE_AMP 12.0f
#define MAX_TIDE_SPEED 0.001f
#define MAX_TIDE_PHASE 6.283185307179586f
#define M_PI 3.14159265358979323846
#define UNQUANTIZE_AMP(X) ((X/65535.0f)*MAX_TIDE_AMP)
#define UNQUANTIZE_PHASE(X) ((X/65535.0f)*MAX_TIDE_PHASE)
#define UNQUANTIZE_SPEED(X) ((X/4294967295.0f)*MAX_TIDE_SPEED)
// meters
#define MAX_TIDE_ERROR 0.05f 

float predict_tide(uint32_t t, tidal *station, int d);
void test_tides(tidal *station, time_t *times, float *levels);
#endif