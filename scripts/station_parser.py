from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
import time, datetime
from dateutil import tz
from collections import namedtuple

OffsetStation = namedtuple("OffsetStation", ["base_station", "seconds_offset", "level_offset", "level_scale"])
Alias = namedtuple("Alias", ["alias", "station"])


station_grammar = Grammar(r"""    
    stations = station_specifier (space_station)*
    space_station = ~"\s+" station_specifier    
    station_specifier = alias / no_alias
    no_alias = ~" ?" station_name 
    unquoted_name = ~"[a-zA-Z0-9,]+"
    name = ~"[a-zA-Z0-9 ,]+"
    quoted_name = "\"" name "\""
    station_name = quoted_name / unquoted_name 
    plain_station = station_name        
    offset = ~"[-\+][0-9]+"
    hour_offset = ~"[-\+][0-9]+:[0-9][0-9]"
    time_offset = hour_offset / offset
    offset_station = plain_station time_offset
    time_pair = (four_n / hour_offset) "&" (four_n / hour_offset)
    number = ~"[-\+]?[0-9]+(\.[0-9]+)?"
    simple_clock = "CLOCK" ":" ISO8601
    decimal = ~"[-\+]?[0-9]+(\.[0-9]+)?"
    ISO_TZ =  hour_offset  / "Z"
    two_n = ~"[0-9][0-9]"
    four_n = ~"[0-9][0-9][0-9][0-9]"
    ISO8601 = four_n "-" two_n "-" two_n "T" two_n ":" two_n ISO_TZ? 
    level = decimal
    complex_clock = "CLOCK" ":" ISO8601 "," level "," level
    station_line = complex_clock / simple_clock / offset_station / plain_station                          
    alias = station_name "=" station_line                                                               
""")

def since_epoch(dt):
    """Convert a datetime to seconds since epoch"""
    return (dt - datetime.datetime(1970,1,1,tzinfo=datetime.timezone.utc)).total_seconds()

def hour_format_to_seconds(hour_offset):
    """Convert a time offset of the form +MM or +(H)H:MM to seconds"""
    if ":" in hour_offset:
        hours, minutes = hour_offset.split(":")
        return int(hours)*3600 + int(minutes)*60
    else:
        return int(hour_offset)*3600

class StationVisitor(NodeVisitor):

    def visit_alias(self, node, visited_children):
        return Alias(visited_children[0], visited_children[2])
    def visit_no_alias(self, node, visited_children):
        return Alias(visited_children[1], OffsetStation(visited_children[1], 0.0, 0.0, 1.0))
    def visit_quoted_name(self, node, visited_children):
        return visited_children[1]
    def visit_station_name(self, node, visited_children):
        return node.text
    def visit_plain_station(self, node, visited_children):
        return OffsetStation(visited_children[1], 0.0, 0.0, 1.0)
    def visit_offset_station(self, node, visited_children):
        return OffsetStation(visited_children[0], visited_children[1], 0.0, 1.0)
    def visit_time_offset(self, node, visited_children):
        return hour_format_to_seconds(node.text)
    def visit_hour_offset(self, node, visited_children):
        return node.text
    def visit_offset(self, node, visited_children):
        return node.text
    def visit_time_pair(self, node, visited_children):
        return node.text
    def visit_number(self, node, visited_children):
        return float(node.text)
    def visit_simple_clock(self, node, visited_children):
        # convert timestamp to seconds since epoch
  
        
        return OffsetStation("CLOCK", since_epoch(visited_children[2]), 0.0, 1.0)
    def visit_decimal(self, node, visited_children):
        return float(node.text)
    def visit_ISO_TZ(self, node, visited_children):
        return node.text
    def visit_two_n(self, node, visited_children):
        return node.text
    def visit_four_n(self, node, visited_children):
        return node.text
    def visit_ISO8601(self, node, visited_children):
        # parse the date using datetime
        time_str = node.text
        if len(node.text)>0 and node.text[-1] == "Z":
            time_str = time_str[:-1]+"+00:00"
        # if no explicit timezone, assume local time on this machine
        dt = datetime.datetime.fromisoformat(time_str)
        if dt.tzinfo is None:
            # local time
            dt = dt.replace(tzinfo=tz.tzlocal())
        return dt
    def visit_level(self, node, visited_children):
        return float(node.text)
    def visit_complex_clock(self, node, visited_children):
        # clock with a hw time and two levels (hw and lw)
        offset = (float(visited_children[4]) + float(visited_children[6])) / 2
        scale = (float(visited_children[6]) - float(visited_children[4])) / 2
        return OffsetStation("CLOCK", since_epoch(visited_children[2]), offset, scale)
    def visit_station_line(self, node, visited_children):
        return visited_children[0]
    def visit_station_specifier(self, node, visited_children):
        return visited_children[0]
    def visit_name(self, node, visited_children):
        return node.text
    def generic_visit(self, node, visited_children):        
        return visited_children or node
    def visit_space_station(self, node, visited_children):        
        return visited_children[1]
    def visit_unquoted_name(self, node, visited_children):
        return node.text
    def visit_stations(self, node, visited_children):
        if len(visited_children)==1:
            return visited_children[0]
        elif type(visited_children[1]) == list:
            return [visited_children[0]] + visited_children[1]
        return visited_children

    
def parse_station(station_specifier):
    """Parse a station specifier"""
    visitor = StationVisitor()
    nodes = visitor.visit(station_grammar.parse(station_specifier))    
    return [node for node in nodes if isinstance(node, Alias)]

tests = """Millport
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
ANewPlace=CLOCK:2023-01-01T12:00
ANewPlace=CLOCK:2023-01-01T12:00Z
ANewPlace=CLOCK:2023-01-01T12:00+01:00
ANewPlace=CLOCK:2023-01-01T12:00-01:00
ANewPlace=CLOCK:2023-01-01T12:00,4.0,2.0
ANewPlace=CLOCK:2023-01-01T12:00,+4.0,-2.0"""


if __name__=="__main__":
    # test the grammar
    for test in tests.split("\n"):
        if len(test.strip())==0:
            continue
        print(test)
        print(station_grammar.parse(test))
        visitor = StationVisitor()
        print(visitor.visit(station_grammar.parse(test)))
        print()
    print(parse_station("Millport"))
    print(parse_station('Millport Arran=Millport-01:02 "Belfast" Bangor=Belfast-31'))