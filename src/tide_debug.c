#include "tide_base.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

/* These functions are only used for debugging */
/* Print a single event */
void print_tide_event(tidal_event *event)
{    
    char *event_type, *neap_spring;
    if(!event) return;
    switch(event->type)
    {
        case TIDE_NONE: event_type = "--"; break;
        case TIDE_HIGH: event_type = "HW"; break;
        case TIDE_LOW: event_type = "LW"; break;
    }
    
    if(event->neap_spring<0.25) neap_spring = "Neap";
    else if(event->neap_spring>0.75) neap_spring = "Spring";
    else neap_spring = "Mid";

    char *datetime = ctime(&event->time);
    datetime[strlen(datetime)-1] = '\0';
    if(event->type==TIDE_NONE) 
        printf("--\n");
    else
        printf("%s %s %2.2fm %s\n", event_type, datetime, event->level, neap_spring);
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
        printf("%s %2.2fm\n", datetime, table->levels[i]);
        t += 3600;
    }
    /* And then the events */
    printf("\nYesterday\n");
    for(int i=0;i<MAX_TIDE_EVENTS;i++)    
        print_tide_event(&table->events[0][i]);        
    printf("\nToday\n");
    for(int i=0;i<MAX_TIDE_EVENTS;i++)    
        print_tide_event(&table->events[1][i]);        
   printf("\nTomorrow\n");
    for(int i=0;i<MAX_TIDE_EVENTS;i++)    
        print_tide_event(&table->events[2][i]);        
   
    printf("\n");
   printf("Tide interpolated now\n");
    t = time(NULL);
    datetime = ctime(&t);
    datetime[strlen(datetime)-1] = '\0';
    printf("%s %2.2fm %+2.2fm/h\n", datetime, interpolate_tide_level(t, table), interpolate_tide_rate(t, table));
    
    printf("\n");
    float hw, lw;
    update_range(table->events[1], &hw, &lw);
    printf("Todays range: HW %2.2fm LW %2.2fm\n", hw, lw);
    printf("\n");

    printf("Tide events before and after now\n");
    tidal_event *prev, *next;
    get_tide_events_near(t, table, &prev, &next);
    print_tide_event(prev);
    print_tide_event(next);
}

/* Iterate over all stations and print their tide tables */
void print_all_tables()
{
    tide_table table;
    tidal_station *station = tidal_stations;
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



int main(int argc, char **argv) {
    time_t now;
    tidal_station *station; 
    //test_tides(&station_millport_scotland_2023, station_millport_scotland_2023_test_times, station_millport_scotland_2023_test_tides);
    if(argc<2) {
        /* Dump the names of all known stations */
        printf("Usage: %s <station name>\n\n", argv[0]);        
        printf("Known stations:\n");
        tidal_station *station = tidal_stations;
        while(station!=NULL) {
            printf("%45s\t(%d-%d)\n", station->name, station->harmonic->base_year, station->harmonic->base_year + station->harmonic->n_years);
            station = station->previous;
        }
        return 1;
    }
    
    /* Get current time */
    now = time(NULL);
    
    
    /* Find the station */
    station = find_tidal_station(argv[1]);
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

