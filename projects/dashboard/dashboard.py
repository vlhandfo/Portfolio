import json
import requests

from pathlib import Path

from utils import (
	get_query_templates,
	get_stop_dataframe,
	get_trip_query_body,
)
from trip import Trip

V = False    # For testing

def main(args) -> None:
	if V:
		print("Arguments\n---------")
		for k, v in args.__dict__.items():
			print(f"{k}: {v}")

	# 1. Setup stop dataframe and templates
	args.STOPS = get_stop_dataframe(args.DIR)	
	if V: print("\nStops:\n", args.STOPS)

	args.TEMPLATES = get_query_templates(args.TEMPLATE_DIR)
	if V: print("\nTrip Template:\n",
				args.TEMPLATES["trip"])

	# 2. Set up Query
	# NOTE: Temporarily only doing Lillestrøm stasjon to Forskningsparken
	query_body = get_trip_query_body(
					start="Lillestrøm stasjon", 
					end="Forskningsparken",
					stops=args.STOPS,
					template=args.TEMPLATES["trip"] #TODO: make robust
				)

	# 3. Parse Response
	response = requests.post(url=args.URL, json={"query": query_body})
	if V: print(response.status_code)
	response = json.loads(response.content.decode())["data"]

	if response is not None:
		trip = Trip(response)
  
	print("From Lillestrøm stasjon to Forskningsparken:")
	print("============================================")
	print("QUERY:")
	print(query_body, "\n")
	print("RESULT:")
	print(trip)
	
if __name__ == "__main__":
	args = lambda: None
	#args.DIR = Path(os.getcwd())
	args.DIR = Path(__file__).parent
	args.TEMPLATE_DIR = args.DIR / Path("query_templates/")
	args.URL = "https://api.entur.io/journey-planner/v3/graphql"


	assert args.TEMPLATE_DIR.exists(), "No template directory found"

	main(args)