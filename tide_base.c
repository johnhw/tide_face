#include "tide_base.h"
#include <math.h>
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#include "tide_data.c"

time_t make_time(uint32_t year, uint32_t month, uint32_t day, uint32_t hour, uint32_t minute, uint32_t second) {
    struct tm tm;
    tm.tm_year = year - 1900;
    tm.tm_mon = month - 1;
    tm.tm_mday = day;
    tm.tm_hour = hour;
    tm.tm_min = minute;
    tm.tm_sec = second;
    tm.tm_isdst = 0;
    return mktime(&tm);
}

/* Take a time in seconds since the epoch (UTC) 
    and predict the tide height in meters at that time. */
float predict_tide(uint32_t t, tidal *station, int d) {                    
    t = t - make_time(station->year, 1, 1, 0, 0, 0);
    float tide = (d>0) ? 0 : station->offset;
    float phase_shift = d * M_PI / 2.0f;
    for (int i=0; i<station->n_constituents; i++) {
        float speed = UNQUANTIZE_SPEED(station->speeds[i]);
        float amp = UNQUANTIZE_AMP(station->amps[i]);
        float phase = UNQUANTIZE_PHASE(station->phases[i]);
        float term = amp * cosf(speed * t + phase + phase_shift);
        term = d>0 ? term * powf(speed, d) : term;
        tide += term;
    }
    return tide;
}

/* Test the tide prediction for a station against a set of known times and levels. */
void test_tides(tidal *station, time_t *times, float *levels) {
    char *datetime;
    printf("Testing %s\n", station->name);
    for (int i=0; i<32; i++) {
        datetime = ctime(&times[i]);
        datetime[strlen(datetime)-1] = '\0';
        float tide = predict_tide(times[i], station, 0);
        printf("Time: %s, %2.2fm:%2.2fm\tError: %2.5fm\n", datetime, tide, levels[i], fabs(tide - levels[i]));
        assert(fabs(tide - levels[i]) < MAX_TIDE_ERROR);                            
    }
}

/* Case insensitive string comparison */
int insenstive_is_prefix(char *s1, char *s2) {
    while (*s1 && *s2) {
        if (tolower(*s1) != tolower(*s2)) return 0;
        s1++;
        s2++;
    }
    return *s1 == '\0';
}

/* Search the registry for a given station name and best-matching year. */
tidal *find_tidal_station(char *name, int year) {
    tidal *station = tidal_stations;
    tidal *best_station = NULL;
    int best_year = 0;    
    int match;
    
    while (station != NULL) {
        match = insenstive_is_prefix(name, station->name);
        if (match) {
            /* Exact match */
            if(station->year == year) {
                return station;
            }            
            else
            {                
                /* Possible year match */
                if(abs(station->year - year) < abs(best_year - year)) {
                    best_year = station->year;
                    best_station = station;
                }
            }
        }
        station = station->previous;
    }
    return best_station;
}

#define N_NEWTON 3
#define N_BINARY 4
void find_tide_event_near(tidal *station, tidal_event *event, time_t t0, time_t t1)
{
    float tide0, tide1;
    float t_d, t_d2;
    time_t t;
    int i;

    tide0 = predict_tide(t0, station, 1);
    tide1 = predict_tide(t1, station, 1);

    /* No event in this interval */
    if(tide0*tide1>0)
    {
        event->type = TIDE_NONE;
        event->level = 0.0;
        event->time = 0;
        return;
    }

    /* do a binary search to find the event approximately */
    for(i=0;i<N_BINARY;i++)
    {
        t = (t0 + t1) / 2;
        tide1 = predict_tide(t, station, 1);    
        if((tide1*tide0)<0)
        {
            t1 = t;
        }
        else
        {
            t0 = t;
        }
    }              
    /* Refine the event time */
    t_d = predict_tide(t, station, 1);
    t_d2 = predict_tide(t, station, 2);
    for(i=0;i<N_NEWTON;i++)
    {
        t = t - t_d / t_d2;
        t_d = predict_tide(t, station, 1);
        t_d2 = predict_tide(t, station, 2);
    }    
    /* Populate the event */
    event->time = t;
    event->level = predict_tide(t, station, 0);
    event->type = (t_d2<0) ? TIDE_HIGH : TIDE_LOW;    
}

/* Remove all events from the event list */
void clear_tide_events(tidal_event *events)
{
    for(int i=0;i<MAX_TIDE_EVENTS;i++)
    {
        events[i].type = TIDE_NONE;
        events[i].time = 0;
        events[i].level = 0.0;
    }
}

void add_tide_event(tidal *station, time_t t, tidal_event *event, tidal_event *events)
{
    int i;
    /* Find the first empty slot */
    for(i=0;i<MAX_TIDE_EVENTS;i++) if(events[i].type==TIDE_NONE) break;
    /* If the list is full, we can't add any more events */
    if(i==MAX_TIDE_EVENTS) return;
    /* Find the event near t */
    find_tide_event_near(station, event, t-1800, t+1800);
    /* If the event is outside the range, we can't add it */
    if(event->type==TIDE_NONE) return;
    /* If the event is a duplicate (or a near duplicate), we don't add it */
    for(int j=0;j<i;j++) if(abs(events[j].time-event->time)<MIN_EVENT_GAP_SECONDS) return;
    /* Add the event */
    events[i] = *event;
    /* Sort the list */
    for(int j=0;j<i;j++) for(int k=j+1;k<i;k++) if(events[j].time>events[k].time) {
        tidal_event tmp = events[j];
        events[j] = events[k];
        events[k] = tmp;
    }
}


void fill_day_tide_table(tidal_event *events, float *levels, tidal *station, time_t t0)    
{
    tidal_event event;
    /* Clear all events */
    clear_tide_events(events);
    /* Get the level, and any event in that hour */
    for(int i=0; i<24; i++) {
        levels[i] = predict_tide(t0, station, 0);
        add_tide_event(station, t0, &event, events);
        t0 += 3600;
    }
}

void populate_tide_table(tide_table *table, tidal *station, time_t base_time, int tz_hours, int tz_mins)
{
    
    /* Get midnight UTC on the base day */
    struct tm *tm = gmtime(&base_time);
    tm->tm_hour = 0;
    tm->tm_min = 0;
    tm->tm_sec = 0;
    time_t midnight = mktime(tm);
    
    /* adjust for time zone */
    midnight += (tz_hours * 60 * 60) + (tz_mins * 60);
    /* Already populated? */
    if(table->base_time==midnight && table->station==station) return;    
    /* Have we moved one day forwards? If so, copy what we can from the previous day */
    if(table->station==station && table->base_time==midnight-DAY_SECONDS) 
    {
        /* Shift the table back one day */
        for(int i=0; i<72; i++) table->levels[i] = table->levels[i+24];
        for(int i=0; i<3; i++) for(int j=0; j<MAX_TIDE_EVENTS; j++) table->events[i][j] = table->events[i][j+1];
        fill_day_tide_table(table->events[2], table->levels+48, station, midnight+DAY_SECONDS);        
        return;        
    }
    /* Have we moved one day backwards? If so, copy what we can from the next day */
    else if(table->station==station && table->base_time==midnight+DAY_SECONDS) 
    {
        /* Shift the table forward one day */
        for(int i=71; i>=0; i--) table->levels[i+24] = table->levels[i];
        for(int i=2; i>=0; i--) for(int j=MAX_TIDE_EVENTS-1; j>=0; j--) table->events[i][j+1] = table->events[i][j];
        fill_day_tide_table(table->events[0], table->levels, station, midnight-DAY_SECONDS);                
    }   

    /* Populate the levels table */
    time_t t0 = midnight - DAY_SECONDS;
    for(int i=0;i<3;i++)
    {
        fill_day_tide_table(table->events[i], table->levels+i*24, station, t0); 
        t0 += DAY_SECONDS; 
    }
    table->base_time = midnight;
    table->station = station;
}    



    


#ifdef TIDE_DEBUG
/* Print a single event */
void print_tide_event(tidal_event *event)
{
    char *event_type;
    switch(event->type)
    {
        case TIDE_NONE: event_type = "--"; break;
        case TIDE_HIGH: event_type = "HW"; break;
        case TIDE_LOW: event_type = "LW"; break;
    }
    char *datetime = ctime(&event->time);
    datetime[strlen(datetime)-1] = '\0';
    printf("%s %s %2.2f\n", event_type, datetime, event->level);
}

/* Print a tide table; this includes
the hourly tide predictions, and the
daily HW/LW events */
void print_tide_table(tide_table *table)
{
    char *datetime;
    time_t t;
    printf("Tide table for %s\n", table->station->name);
    t = table->base_time;
    for(int i=0;i<72;i++)
    {
        datetime = ctime(&t);
        datetime[strlen(datetime)-1] = '\0';
        printf("%s %2.2f\n", datetime, table->levels[i]);
        t += 3600;
    }
    /* And then the events */
    printf("Yesterday\n");
    for(int i=0;i<MAX_TIDE_EVENTS;i++)    
        print_tide_event(&table->events[0][i]);        
    printf("Today\n");
    for(int i=0;i<MAX_TIDE_EVENTS;i++)    
        print_tide_event(&table->events[1][i]);        
   printf("Tomorrow\n");
    for(int i=0;i<MAX_TIDE_EVENTS;i++)    
        print_tide_event(&table->events[2][i]);        
   
}

/* Iterate over all stations and print their tide tables */
void print_all_tables()
{
    tide_table table;
    tidal *station = tidal_stations;
    table.station = NULL;
    table.base_time = 0;
    printf("Tide tables\n");
    while(station!=NULL)
    {        
        populate_tide_table(&table, station, make_time(2023, 12, 17, 0, 0, 0), 0, 0);
        print_tide_table(&table);
        station = station->previous;
        printf("\n\n");
    }
}
#endif 


int main(int argc, char **argv) {
    time_t now;
    test_tides(&station_millport_scotland_2023, station_millport_scotland_2023_test_times, station_millport_scotland_2023_test_tides);
    if(argc<2) {
        printf("Usage: %s <station name>\n", argv[0]);
        return 1;
    }
    /* Get current time */
    now = time(NULL);
    /* Extract current year */
    struct tm *tm = gmtime(&now);    
    /* Find the station */
    tidal *station = find_tidal_station(argv[1], tm->tm_year+1900);
    if(!station) {
        printf("Station %s not found\n", argv[1]);
        return 1;
    }
    tide_table table;
    table.station = station;
    table.base_time = 0;
    populate_tide_table(&table, station, now, 0, 0);
    print_tide_table(&table);
    return 0;
}        