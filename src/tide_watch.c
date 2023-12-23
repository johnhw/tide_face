#include "tide_watch.h"
#include "tide_base.h"

tide_face face_data;

/* Guarantee that the tide table is populated for the current station and time */
void tf_ensure_tide_table(tide_face *face_data, time_t now)
{
    /* TODO: Verify time zone hasn't changed on the watch -- if it has, update tz_hours and tz_mins */
    populate_tide_table(&(face_data->current_table), face_data->current_station, now, face_data->tz_hours, face_data->tz_mins);
}


void tf_update_levels(tide_face *face_data, time_t now)
{
    tf_ensure_tide_table(face_data, now);
    face_data->level = interpolate_tide_table(now, &(face_data->current_table));
    face_data->last_update = now;
}

void tf_init(tide_face *face_data, time_t t, int tz_hours, int tz_mins)
{
    face_data->current_station = tidal_stations;    
    face_data->mode = MODE_STATION_NAME;
    face_data->event_day = 0;
    face_data->event_number = 0;
    face_data->tz_hours = tz_hours;
    face_data->tz_mins = tz_mins;
    tf_update_levels(face_data, t);
}

tidal_station *tf_cycle_station(tidal_station *station)
{
    tidal_station *next = station->previous;
    if(next==NULL)
        next = tidal_stations;
}

#define EVENT_NONE 0
#define EVENT_ALARM 1
#define EVENT_ALARM_LONG 2
#define EVENT_MODE 3
#define EVENT_LIGHT 4

void tf_event(tide_face *face, uint8_t event, time_t t)
{
    tf_ensure_tide_table(face, t);
    switch(face->mode)
    {
        case MODE_STATION_NAME:
            /* Show the events if ALARM pressed*/
            if(event==EVENT_ALARM)
            {
                tide_table *table = &(face->current_table);
                face->mode = MODE_STATION_EVENT;
                face->event_day = 1; /* Start at the nearest event to now */
                face->event_number = 0;            
                if(t<table->base_time-DAY_SECONDS || t>=table->base_time+DAY_SECONDS*2-HOUR_SECONDS)
                {
                    /* We're outside the range of the table; just show the first event for today */
                }
                else
                {                
                    for(int i=0;i<3;i++)
                    {
                        for(int j=0;j<MAX_TIDE_EVENTS;j++)
                        {
                            
                            if(table->events[i][j].time>t)
                            {
                                face->event_day = i;
                                face->event_number = j;
                                break;
                            }
                        }
                    }
                }
            }
            else if(event==EVENT_ALARM_LONG)
            {
                /* Enter station select on long press*/
                face->mode = MODE_SELECT_STATION;                
            }
            break;
        /* Event viewer (HW/LW) mode */
        case MODE_STATION_EVENT:
            if(event==EVENT_ALARM)
            {
                int attempts = 0;
                /* Advance to the next non-empty event */
                while(face->current_table.events[face->event_day][face->event_number].type==TIDE_NONE && attempts<(4*MAX_TIDE_EVENTS))
                {
                    face->event_number++;
                    if(face->event_number>=MAX_TIDE_EVENTS)
                    {
                        face->event_number = 0;
                        face->event_day++;
                        if(face->event_day>=3)                        
                            face->event_day = 0;                                                        
                    }
                    attempts++;
                }                
            }
            else if(event==EVENT_ALARM_LONG)
            {
                face->mode = MODE_STATION_NAME;
            }
            break;
        /* Select station mode; cycle through stations. Long press exits. */
        case MODE_SELECT_STATION:
            if(event==EVENT_ALARM)
            {
                face->current_station = tf_cycle_station(face->current_station);
            }
            else if(event==EVENT_ALARM_LONG)
            {
                tf_ensure_tide_table(face, t);
                face->mode = MODE_STATION_NAME;
            }
            break;
    }
}