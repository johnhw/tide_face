from parsimonious.grammar import Grammar


station_grammar = Grammar(r"""
    station_specifier = alias / station_name 
    name = ~"[a-zA-Z0-9 ,]+"
    quoted_name = "\"" name "\""
    station_name = quoted_name / name 
    plain_station = station_name        
    offset = ~"[-\+][0-9]+"
    hour_offset = ~"[-\+][0-9]+:[0-9][0-9]"
    time_offset = hour_offset / offset
    offset_station = plain_station time_offset
    time_pair = (four_n / hour_offset) "&" (four_n / hour_offset)
    number = ~"[-\+]?[0-9]+(\.[0-9]+)?"
    time_adjust = time_pair "=" number
    time_adjusts = time_adjust "," time_adjust    
    decimal = ~"\+?-?[0-9]+(\.[0-9]+)?"
    level_adjust = decimal "=" decimal
    level_adjusts = level_adjust "," level_adjust
    secondary_port = station_name ":" time_adjusts level_adjusts                
    simple_clock = "CLOCK" ":" ISO8601
    ISO_TZ = ( ~"[-\+]" hour_offset )/ "Z"
    two_n = ~"[0-9][0-9]"
    four_n = ~"[0-9][0-9][0-9][0-9]"
    ISO8601 = four_n "-" two_n "-" two_n "T" two_n ":" two_n ISO_TZ? 
    level = decimal
    complex_clock = simple_clock "," level "," simple_clock "," level
    station_line = complex_clock / simple_clock / secondary_port / offset_station / plain_station                          
    alias = station_name "=" station_line                                                               
""")

tests = """
Millport
"Millport"
"Millport, Scotland"
Alias=Millport
A=Millport
Test=Millport+6
Test=Millport-0
Test=Millport+61
Set=Millport-05:00
Set=Millport+6:00
Set="Millport"-06:34
Finnart=Millport:0000&0600=-40,1200&1800=-31,4.0=+0.7,2.2=-0.5
Finnart="Millport":0000&0600=-40,1200&1800=-31,4.0=0.7,2.2=-0.5,4.0=0.7,2.2=-0.5
ANewPlace=CLOCK:2023-01-01T12:00
ANewPlace=CLOCK:2023-01-01T12:00Z
ANewPlace=CLOCK:2023-01-01T12:00+01:00
ANewPlace=CLOCK:2023-01-01T12:00-01:00
ANewPlace=CLOCK:2023-01-01T12:00,4.0,2023-01-01T18:00,2.0
"""

if __name__=="__main__":
    # test the grammar
    for test in tests.split("\n"):
        if len(test.strip())==0:
            continue
        print(test)
        print(station_grammar.parse(test))
        print()
    