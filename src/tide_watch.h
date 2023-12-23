#include "tide_base.h"

#define MODE_NONE 0
#define MODE_STATION_NAME 1
#define MODE_STATION_EVENT 2
#define MODE_SELECT_STATION 3

typedef struct tide_face {
    tide_table current_table;
    time_t last_update;     
    tidal_station *current_station;    
    uint8_t mode; 
    uint8_t event_day, event_number; // day/index of the current event    
    float level; // current tide level at last_update
    int tz_hours, tz_mins; // timezone offset
} tide_face;

void tf_ensure_tide_table(tide_face *face, time_t now);


