import ctypes
import json
import os
import sys 

# Load the libtcd shared library using ctypes
# set the path here to the location of the libtcd.so file
lib_path = "/usr/lib"
libtcd = ctypes.CDLL(f"{lib_path}/libtcd.so")  

# Path where the xtide TCD files are located
# (all tcd files in this directory will be processed)
base_path = "/usr/share/xtide/"


## Define the C structures in Python
ONELINER_LENGTH = 90
MONOLOGUE_LENGTH = 10000
MAX_CONSTITUENTS = 255 

class TIDE_STATION_HEADER(ctypes.Structure):
    _fields_ = [
        ("record_number", ctypes.c_int32),
        ("record_size", ctypes.c_uint32),
        ("record_type", ctypes.c_ubyte),
        ("latitude", ctypes.c_double),
        ("longitude", ctypes.c_double),
        ("reference_station", ctypes.c_int32),
        ("tzfile", ctypes.c_int16),
        ("name", ctypes.c_char * ONELINER_LENGTH)
    ]



# Define the DB_HEADER_PUBLIC structure in Python
class DB_HEADER_PUBLIC(ctypes.Structure):
    _fields_ = [
        ("version", ctypes.c_char * ONELINER_LENGTH), 
        ("major_rev", ctypes.c_uint32),
        ("minor_rev", ctypes.c_uint32),
        ("last_modified", ctypes.c_char * ONELINER_LENGTH),  
        ("number_of_records", ctypes.c_uint32),
        ("start_year", ctypes.c_int32),
        ("number_of_years", ctypes.c_uint32),
        ("constituents", ctypes.c_uint32),
        ("level_unit_types", ctypes.c_uint32),
        ("dir_unit_types", ctypes.c_uint32),
        ("restriction_types", ctypes.c_uint32),
        ("datum_types", ctypes.c_uint32),
        ("countries", ctypes.c_uint32),
        ("tzfiles", ctypes.c_uint32),
        ("legaleses", ctypes.c_uint32),
        ("pedigree_types", ctypes.c_uint32),  # Included for reading V1 files
    ]


# Define the TIDE_RECORD structure in Python
class TIDE_RECORD(ctypes.Structure):
    _fields_ = [
        ("header", TIDE_STATION_HEADER),
        ("country", ctypes.c_int16),
        ("source", ctypes.c_char * ONELINER_LENGTH),
        ("restriction", ctypes.c_ubyte),
        ("comments", ctypes.c_char * MONOLOGUE_LENGTH),
        ("notes", ctypes.c_char * MONOLOGUE_LENGTH),
        ("legalese", ctypes.c_ubyte),
        ("station_id_context", ctypes.c_char * ONELINER_LENGTH),
        ("station_id", ctypes.c_char * ONELINER_LENGTH),
        ("date_imported", ctypes.c_uint32),
        ("xfields", ctypes.c_char * MONOLOGUE_LENGTH),
        ("direction_units", ctypes.c_ubyte),
        ("min_direction", ctypes.c_int32),
        ("max_direction", ctypes.c_int32),
        ("level_units", ctypes.c_ubyte),
        ("datum_offset", ctypes.c_float),
        ("datum", ctypes.c_int16),
        ("zone_offset", ctypes.c_int32),
        ("expiration_date", ctypes.c_uint32),
        ("months_on_station", ctypes.c_uint16),
        ("last_date_on_station", ctypes.c_uint32),
        ("confidence", ctypes.c_ubyte),
        ("amplitude", ctypes.c_float * MAX_CONSTITUENTS),
        ("epoch", ctypes.c_float * MAX_CONSTITUENTS),
        ("min_time_add", ctypes.c_int32),
        ("min_level_add", ctypes.c_float),
        ("min_level_multiply", ctypes.c_float),
        ("max_time_add", ctypes.c_int32),
        ("max_level_add", ctypes.c_float),
        ("max_level_multiply", ctypes.c_float),
        ("flood_begins", ctypes.c_int32),
        ("ebb_begins", ctypes.c_int32),
    ]

## Define the C function prototypes in Python
libtcd.dump_tide_record.argtypes = [ctypes.POINTER(TIDE_RECORD)]
libtcd.dump_tide_record.restype = None

libtcd.get_country.argtypes = [ctypes.c_int32]
libtcd.get_country.restype = ctypes.c_char_p

libtcd.get_tzfile.argtypes = [ctypes.c_int32]
libtcd.get_tzfile.restype = ctypes.c_char_p

libtcd.get_level_units.argtypes = [ctypes.c_int32]
libtcd.get_level_units.restype = ctypes.c_char_p

libtcd.get_dir_units.argtypes = [ctypes.c_int32]
libtcd.get_dir_units.restype = ctypes.c_char_p

libtcd.get_restriction.argtypes = [ctypes.c_int32]
libtcd.get_restriction.restype = ctypes.c_char_p

libtcd.get_datum.argtypes = [ctypes.c_int32]
libtcd.get_datum.restype = ctypes.c_char_p

libtcd.get_legalese.argtypes = [ctypes.c_int32]
libtcd.get_legalese.restype = ctypes.c_char_p

libtcd.get_constituent.argtypes = [ctypes.c_int32]
libtcd.get_constituent.restype = ctypes.c_char_p

libtcd.get_station.argtypes = [ctypes.c_int32]
libtcd.get_station.restype = ctypes.c_char_p

libtcd.get_speed.argtypes = [ctypes.c_int32]
libtcd.get_speed.restype = ctypes.c_double

libtcd.get_equilibrium.argtypes = [ctypes.c_int32, ctypes.c_int32]
libtcd.get_equilibrium.restype = ctypes.c_float

libtcd.get_node_factor.argtypes = [ctypes.c_int32, ctypes.c_int32]
libtcd.get_node_factor.restype = ctypes.c_float

libtcd.get_equilibriums.argtypes = [ctypes.c_int32]
libtcd.get_equilibriums.restype = ctypes.POINTER(ctypes.c_float)

libtcd.get_node_factors.argtypes = [ctypes.c_int32]
libtcd.get_node_factors.restype = ctypes.POINTER(ctypes.c_float)

libtcd.get_time.argtypes = [ctypes.c_char_p]
libtcd.get_time.restype = ctypes.c_int32

libtcd.ret_time.argtypes = [ctypes.c_int32]
libtcd.ret_time.restype = ctypes.c_char_p

libtcd.ret_time_neat.argtypes = [ctypes.c_int32]
libtcd.ret_time_neat.restype = ctypes.c_char_p

libtcd.ret_date.argtypes = [ctypes.c_uint32]
libtcd.ret_date.restype = ctypes.c_char_p

libtcd.search_station.argtypes = [ctypes.c_char_p]
libtcd.search_station.restype = ctypes.c_int32

libtcd.find_station.argtypes = [ctypes.c_char_p]
libtcd.find_station.restype = ctypes.c_int32

libtcd.find_tzfile.argtypes = [ctypes.c_char_p]
libtcd.find_tzfile.restype = ctypes.c_int32

libtcd.find_country.argtypes = [ctypes.c_char_p]
libtcd.find_country.restype = ctypes.c_int32

libtcd.find_level_units.argtypes = [ctypes.c_char_p]
libtcd.find_level_units.restype = ctypes.c_int32

libtcd.find_dir_units.argtypes = [ctypes.c_char_p]
libtcd.find_dir_units.restype = ctypes.c_int32

libtcd.find_restriction.argtypes = [ctypes.c_char_p]
libtcd.find_restriction.restype = ctypes.c_int32

libtcd.find_datum.argtypes = [ctypes.c_char_p]
libtcd.find_datum.restype = ctypes.c_int32

libtcd.find_constituent.argtypes = [ctypes.c_char_p]
libtcd.find_constituent.restype = ctypes.c_int32

libtcd.find_legalese.argtypes = [ctypes.c_char_p]
libtcd.find_legalese.restype = ctypes.c_int32

libtcd.add_restriction.argtypes = [ctypes.c_char_p, ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.add_restriction.restype = ctypes.c_int32

libtcd.add_tzfile.argtypes = [ctypes.c_char_p, ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.add_tzfile.restype = ctypes.c_int32

libtcd.add_country.argtypes = [ctypes.c_char_p, ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.add_country.restype = ctypes.c_int32

libtcd.add_datum.argtypes = [ctypes.c_char_p, ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.add_datum.restype = ctypes.c_int32

libtcd.add_legalese.argtypes = [ctypes.c_char_p, ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.add_legalese.restype = ctypes.c_int32

libtcd.find_or_add_restriction.argtypes = [ctypes.c_char_p, ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.find_or_add_restriction.restype = ctypes.c_int32

libtcd.find_or_add_tzfile.argtypes = [ctypes.c_char_p, ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.find_or_add_tzfile.restype = ctypes.c_int32

libtcd.find_or_add_country.argtypes = [ctypes.c_char_p, ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.find_or_add_country.restype = ctypes.c_int32

libtcd.find_or_add_datum.argtypes = [ctypes.c_char_p, ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.find_or_add_datum.restype = ctypes.c_int32

libtcd.find_or_add_legalese.argtypes = [ctypes.c_char_p, ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.find_or_add_legalese.restype = ctypes.c_int32

libtcd.set_speed.argtypes = [ctypes.c_int32, ctypes.c_double]
libtcd.set_speed.restype = None

libtcd.set_equilibrium.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_float]
libtcd.set_equilibrium.restype = None

libtcd.set_node_factor.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_float]
libtcd.set_node_factor.restype = None

libtcd.open_tide_db.argtypes = [ctypes.c_char_p]
libtcd.open_tide_db.restype = ctypes.c_bool

libtcd.close_tide_db.argtypes = []
libtcd.close_tide_db.restype = None

libtcd.create_tide_db.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_char_p),
                                  ctypes.POINTER(ctypes.c_double), ctypes.c_int32, ctypes.c_uint32,
                                  ctypes.POINTER(ctypes.POINTER(ctypes.c_float)),
                                  ctypes.POINTER(ctypes.POINTER(ctypes.c_float))]
libtcd.create_tide_db.restype = ctypes.c_bool

libtcd.get_tide_db_header.argtypes = []
libtcd.get_tide_db_header.restype = DB_HEADER_PUBLIC

libtcd.get_partial_tide_record.argtypes = [ctypes.c_int32, ctypes.POINTER(TIDE_STATION_HEADER)]
libtcd.get_partial_tide_record.restype = ctypes.c_bool

libtcd.get_next_partial_tide_record.argtypes = [ctypes.POINTER(TIDE_STATION_HEADER)]
libtcd.get_next_partial_tide_record.restype = ctypes.c_int32

libtcd.get_nearest_partial_tide_record.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.POINTER(TIDE_STATION_HEADER)]
libtcd.get_nearest_partial_tide_record.restype = ctypes.c_int32

libtcd.read_tide_record.argtypes = [ctypes.c_int32, ctypes.POINTER(TIDE_RECORD)]
libtcd.read_tide_record.restype = ctypes.c_int32

libtcd.read_next_tide_record.argtypes = [ctypes.POINTER(TIDE_RECORD)]
libtcd.read_next_tide_record.restype = ctypes.c_int32

libtcd.add_tide_record.argtypes = [ctypes.POINTER(TIDE_RECORD), ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.add_tide_record.restype = ctypes.c_bool

libtcd.update_tide_record.argtypes = [ctypes.c_int32, ctypes.POINTER(TIDE_RECORD), ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.update_tide_record.restype = ctypes.c_bool

libtcd.delete_tide_record.argtypes = [ctypes.c_int32, ctypes.POINTER(DB_HEADER_PUBLIC)]
libtcd.delete_tide_record.restype = ctypes.c_bool

libtcd.infer_constituents.argtypes = [ctypes.POINTER(TIDE_RECORD)]
libtcd.infer_constituents.restype = ctypes.c_bool

def decode(by):
    try:
        return by.decode()
    except:
        return by.decode('latin-1')

def open_and_generate_json(database_file, output_file):
    if not libtcd.open_tide_db(database_file.encode()):
        print(f"Failed to open the database: {database_file}")
        return
    try:
        # Get the database header    
        db_header = libtcd.get_tide_db_header()
        assert db_header is not None
    except:
        print("Failed to get the database header")
        return
    data = {
        "database_header": {
            "version": decode(db_header.version),
            "major_revision": db_header.major_rev,
            "minor_revision": db_header.minor_rev,
            "last_modified": decode(db_header.last_modified),
            "number_of_records": db_header.number_of_records,
            "start_year": db_header.start_year,
            "number_of_years": db_header.number_of_years,
            "constituents": db_header.constituents,
            "level_unit_types": db_header.level_unit_types,
            "dir_unit_types": db_header.dir_unit_types,
            "restriction_types": db_header.restriction_types,
            "datum_types": db_header.datum_types,
            "countries": db_header.countries,
            "tzfiles": db_header.tzfiles,
            "legaleses": db_header.legaleses,
            "pedigree_types": db_header.pedigree_types
        },
        "constituents": [],
        "tide_records": []
    }

    for i in range(db_header.constituents):
        year_constituent_info = {
            "constituent_number": i ,
            "constituent_name": decode(libtcd.get_constituent(i)),
            "speed": libtcd.get_speed(i),
            "years":{}         
        }
        
        # extract constituents for each year in valid range        
        for year in range(data["database_header"]["number_of_years"]):            
            year_constituent_info["years"][year + data["database_header"]["start_year"]] = {
                "equilibrium": libtcd.get_equilibrium(i, year),
                "node_factor": libtcd.get_node_factor(i, year)
            }            
        data["constituents"].append(year_constituent_info)

    record_number = 0
    tide_record = TIDE_RECORD()

    while libtcd.read_next_tide_record(ctypes.byref(tide_record)) != -1:
        record_info = {
            "record_number": tide_record.header.record_number,
            "record_size": tide_record.header.record_size,
            "record_type": tide_record.header.record_type,
            "latitude": tide_record.header.latitude,
            "longitude": tide_record.header.longitude,
            "reference_station": tide_record.header.reference_station,
            "tzfile": decode(libtcd.get_tzfile(tide_record.header.tzfile)),
            "name": decode(tide_record.header.name),
            "country": decode(libtcd.get_country(tide_record.country)),
            "source": decode(tide_record.source),
            "restriction": decode(libtcd.get_restriction(tide_record.restriction)),
            "comments": decode(tide_record.comments),
            "notes": decode(tide_record.notes),
            "legalese": decode(libtcd.get_legalese(tide_record.legalese)),
            "station_id_context": decode(tide_record.station_id_context),
            "station_id": decode(tide_record.station_id),
            "date_imported": decode(libtcd.ret_date(tide_record.date_imported)),
            "xfields": decode(tide_record.xfields),
            "direction_units": decode(libtcd.get_dir_units(tide_record.direction_units)),
            "min_direction": tide_record.min_direction,
            "max_direction": tide_record.max_direction,
            "level_units": decode(libtcd.get_level_units(tide_record.level_units))
        }

        if tide_record.header.record_type == 1:
            record_info.update({
                "datum_offset": tide_record.datum_offset,
                "datum": decode(libtcd.get_datum(tide_record.datum)),
                "zone_offset": tide_record.zone_offset,
                "expiration_date": decode(libtcd.ret_date(tide_record.expiration_date)),
                "months_on_station": tide_record.months_on_station,
                "last_date_on_station": decode(libtcd.ret_date(tide_record.last_date_on_station)),
                "confidence": tide_record.confidence,
                "amplitude": [float(value) for value in tide_record.amplitude[:db_header.constituents]],
                "epoch": [float(value) for value in tide_record.epoch[:db_header.constituents]]
            })
        elif tide_record.header.record_type == 2:
            record_info.update({
                "min_time_add": tide_record.min_time_add,
                "min_level_add": tide_record.min_level_add,
                "min_level_multiply": tide_record.min_level_multiply,
                "max_time_add": tide_record.max_time_add,
                "max_level_add": tide_record.max_level_add,
                "max_level_multiply": tide_record.max_level_multiply,
                "flood_begins": decode(libtcd.ret_time(tide_record.flood_begins)),
                "ebb_begins": decode(libtcd.ret_time(tide_record.ebb_begins))
            })
            
        data["tide_records"].append(record_info)
        record_number += 1

    # Serialize the dictionary to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=2)


if __name__=="__main__":
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    # Example usage
    os.listdir(base_path)
    for file in os.listdir(base_path):
        if file.endswith(".tcd"):
            print(f"Converting {file} to {file}.json")            
            open_and_generate_json(f"{base_path}/{file}", f"{file}.json")            