#include "tide_base.h"
#include <math.h>
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

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
        float term = amp * cosf(speed * t + phase);
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

/* Search the registry for a given station name and best-matching year. */
tidal *find_tidal_station(char *name, int year) {
    tidal *station = tidal_stations;
    tidal *best_station = NULL;
    int best_year = 0;
    while (station != NULL) {
        if (strcmp(station->name, name) == 0){
            /* Exact match */
            if(station->year == year) {
                return station;
            }
            else
            {
                /* Possible year match */
                if(abs(station->year - year) < abs(best_year - year)) {
                    best_year = station->year;
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

void populate_tide_table(tide_table *table, tidal *station, time_t base_time, int tz_hours, int tz_mins)
{
    int populate_today = 1;
    int populate_yesterday = 1;
    int populate_tomorrow = 1;
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
    if(table->station==station && table->base_time==midnight-86400) 
    {
        /* Shift the table back one day */
        for(int i=0; i<72; i++) table->levels[i] = table->levels[i+24];
        for(int i=0; i<3; i++) for(int j=0; j<6; j++) table->events[i][j] = table->events[i][j+1];
        populate_today = 0;     
        populate_yesterday = 0;   
    }
    /* Have we moved one day backwards? If so, copy what we can from the next day */
    if(table->station==station && table->base_time==midnight+86400) 
    {
        /* Shift the table forward one day */
        for(int i=71; i>=0; i--) table->levels[i+24] = table->levels[i];
        for(int i=2; i>=0; i--) for(int j=5; j>=0; j--) table->events[i][j+1] = table->events[i][j];
        populate_today = 0;     
        populate_tomorrow = 0;   
    }   
    /* Populate the levels table */
    if(populate_yesterday) {
        for(int i=0; i<24; i++) {
            table->levels[i] = predict_tide(midnight - (86400 - (i*3600)), station, 0);
        }
        for(int i=0;i<6;i++)
        {
            find_events(&table->events[0], table->station, table->base_time, 0);
        }
    }
    if(populate_today) {
        for(int i=0; i<24; i++) {
            table->levels[i+24] = predict_tide(midnight + (i*3600), station, 0);
        }
    }
    if(populate_tomorrow) {
        for(int i=0; i<24; i++) {
            table->levels[i+48] = predict_tide(midnight + 86400 + (i*3600), station, 0);
        }
    }
}    
    
    

/* Mean error for Millport, Scotland in 2023 is approximately 0.007m */
char station_millport_scotland_2023_name [] = "Millport, Scotland";
uint32_t station_millport_scotland_2023_speed [] = {0x12AAF606, 0x2555EC0E, 0x24A60275, 0x23F90BFA, 0x35F591F7, 0x47F217F5, 0x6BEB23EF, 0x234C157F, 0x229F1F05, 0x114E15F4, 0x1290DD21, 0x10A11F79, 0x129DE993, 0x253BD327, 0x4A77A64E, 0x252EC6DC, 0x248EDCAC, 0x22B644CD, 0x23633B48, 0x36A40202, 0x354721EE, 0x4745217A, 0x4934DF21, 0x267E9A54, 0x15CE013, 0xD0C72, 0x1A18E7, 0x6B3E2D75, 0x6D2DEB1C, 0x494EF809, 0x22094E53, 0x95D0B2, 0x25E8C9A2, 0x229C2BE6, 0x23DEF313, 0x37E6C92D, 0x2698B33B, 0x46982AFF};
uint16_t station_millport_scotland_2023_amp [] = {0x28D, 0x259, 0x16A, 0x170E, 0x10B, 0x1C2, 0x78, 0x45B, 0x7A, 0x266, 0xD0, 0xCD, 0x3E, 0x63F, 0x47, 0x68, 0xB1, 0xBD, 0x123, 0x6B, 0x48, 0xB7, 0x1C2, 0x7F, 0x93, 0x229, 0x6B, 0x38, 0x86, 0xAD, 0x3A, 0x39, 0x60, 0x7E, 0x3C, 0x66, 0x55, 0x3B};
uint16_t station_millport_scotland_2023_phase [] = {0x7B7F, 0x7055, 0x33B2, 0x7468, 0x512A, 0x9053, 0x6080, 0x4955, 0x202F, 0x455E, 0x73EC, 0x3379, 0x35DD, 0xE705, 0x784F, 0xF179, 0x42C5, 0x7C16, 0x2DDF, 0xD131, 0xA4CC, 0x5971, 0x13D8, 0xDC69, 0x88F8, 0x14AA, 0x18B2, 0x3542, 0xD6FE, 0x9D84, 0x4773, 0xFA24, 0x94B6, 0xCB, 0x734F, 0x3AD9, 0x685A, 0x2D77};

time_t station_millport_scotland_2023_test_times [] = {1688733489, 1698423109, 1698360541, 1687568705, 1693003109, 1679821131, 1684479076, 1699263532, 1699967995, 1687201390, 1689060224, 1692971831, 1700226128, 1701322636, 1700936761, 1701520040, 1692759951, 1674802785, 1682440122, 1690990968, 1681331935, 1677307772, 1673856624, 1690003756, 1681227114, 1677898887, 1675074465, 1686124941, 1683428899, 1683977938, 1684449390, 1690815905};
float station_millport_scotland_2023_test_tides [] = {2.0770579795316513, 0.7289970226823832, 3.3753250049152457, 2.4176665135849063, 1.3864594252890114, 0.5469748026215489, 1.1454070803474532, 2.022780886360471, 3.337170656850065, 0.8103458812880713, 2.9639036520031348, 1.7007211874326578, 3.0408539465248263, 1.4118233304974432, 1.828614256481454, 2.5831328149749293, 3.118014677288809, 2.0415685775758643, 2.855075432241642, 1.7934684811755763, 1.2783678427227467, 1.6329209586002937, 2.480967107516828, 1.9424263909121298, 3.2186606462551857, 1.2691146087107728, 1.6645517139803763, 0.3444190887916047, 2.479623319959078, 0.6441852294043552, 2.9203629896802985, 1.153112261057139};

tidal station_millport_scotland_2023 = {
        .name = station_millport_scotland_2023_name,
        .year = 2023,
        .lat = 55.7496,
        .lon = -4.9058,
        .offset = 1.9962999820709229,
        .speeds = station_millport_scotland_2023_speed,
        .amps = station_millport_scotland_2023_amp,
        .phases = station_millport_scotland_2023_phase,
        .n_constituents = 38,
        .mean_error = 0.00680195486959848
};

int main(int argc, char **argv) {
    test_tides(&station_millport_scotland_2023, station_millport_scotland_2023_test_times, station_millport_scotland_2023_test_tides);
    return 0;
}        