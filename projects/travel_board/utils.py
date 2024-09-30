import pandas as pd

from datetime import datetime
from pathlib import Path


def get_stop_dataframe(dir: str) -> pd.DataFrame:
	"""
	Reads stop information from `{dir}/data/stops.csv`, adds simple keys for 
	informal stop names and returns everything in a pd.Dataframe.
  
	Arguments:
		dir (str | Path): the path to the directory which contains the 
  			`data/stops.csv` 
     
	Returns:
		pd.Dataframe: columns = ["name", "id", "key"]

	Example of a row:
								name                   id                 key
	2                    Oslo S, Oslo  NSR:StopPlace:59872              oslo s
	"""
	# TODO: add check for data dir
	if not isinstance(dir, Path): dir = Path(dir)
 
	df = pd.read_csv(f"{dir}/data/stops.csv", index_col=0)
 
	# Add column with just the stop name for easier dict keys
	df["key"] = [name.split(",")[0].lower() for name in df["name"]]
 
	return df
	

def get_query_templates(template_dir: Path) -> dict[str, str]:
	"""
 	Traverses query template directory and maps the name of the query to the 
 	template.
	"""
	res = {}
	for template in template_dir.glob("*"):
		with open(template, "r", encoding="utf-8") as f:
			res[template.stem] = f.read()
 
	return res	
 

def _get_stops_with_checks(stops: pd.DataFrame, key: str) -> pd.DataFrame:
	""" Validates stop keys and results from given Dataframe.
		- Converts string to lowercase
		- Check that the result is not empty or more than 1
	
	Arguments:
		stops (pd.DataFrame): all known stops 
		key (str): informal stop name for identifying the correct stop
  
	Returns:
		_stop (pd.DataFrame): the row of the dataframe containing stop 
  			information about the given key.
		TODO: maybe change this to a Series to make it more lightweight? Not a 
  			problem yet, though
	"""
	key = key.lower()
	_stop = stops[stops["key"] == key]
	assert len(_stop) != 0, f"Stop key, '{key}', not found in stop dataframe"
	assert len(_stop) == 1, f"Something went wrong with getting '{key}'stop."
	
	return _stop


def _format_date_time(gmt: str = "+02:00") -> str:
	"""Convert datetime object to GraphQL compatible datetime string
	
	Arguments:
		gmt (str | Optional): the current timezone. Default is Oslo time.
  
	Returns:
		res (str): datetime string in the following format:
			{YYYY}-{MM}-{DD}T{HH}:{MM}:{SS}+{GMT}
   
	Example:
		August 22, 2024 at 1:28:48.500 pm in Oslo
  						  ↓ 
    		"2024-08-22T13:28:48.500+02:00"
 	"""
	now = datetime.now()

	date = str(now.date())
	time = str(now.time())
	timezone = gmt

	res = f"{date}T{time}{timezone}"

	return res


def get_trip_query_body(start: str,
                        end: str,
                        stops: pd.DataFrame, 
                        template:str,
                        n: int = 3
    ) -> str:
	start = _get_stops_with_checks(stops, start)
	end = _get_stops_with_checks(stops, end)
	time = _format_date_time()
  
	# TODO: There is probably a better way of doing this, but 
	# 	the {} in the query make it so I can't use format
	return template.replace(
     			"{start_id}", start["id"].values[0]
			).replace(
				"{start_name}", start["name"].values[0]
			).replace(
				"{end_id}", end["id"].values[0]
			).replace(
				"{end_name}", end["name"].values[0]
			).replace(
				"{n}", str(n)
    		).replace(
				"{datetime}", time
			)		
	