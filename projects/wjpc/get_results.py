"""
This script retrieves and parses data from the World Jigsaw Puzzle Championships website.
It allows users to specify the category, year, and round of results to analyze.
The script fetches the competition results from the specified URL and saves them in an sqlite3 database.

NOTE:
- Parsing of names for pairs and teams is not implemented yet 
"""

import logging
import pandas as pd
import requests
import sqlite3

from bs4 import BeautifulSoup
from argparse import ArgumentParser
from pathlib import Path

def _get_country_and_name(row: list) -> tuple:
    # The setup of the table on the website combines country and name
	data, *_ = row[3].split("\n") 
	country, *name = data.split()
	if country == "United":
		country = "UK"
		name.pop(0)

	if country == "Czech":
		country = "Czech Republic"
		name.pop(0)

	name = " ".join(name)

	return country, name


def _parse_row(row: list) -> list:
	parsed = []
	parsed.append(row[1])    # Place
	_, name = _get_country_and_name(row)
	parsed.append(name)
	for i in range(4, len(row)):
		x = row[i].split('\n')
		parsed.append(x[0])
	
	return parsed


def parse_data(df: pd.DataFrame, table):
	column_data = table.find_all('tr')
	for row in column_data[1:]:
		row_data = row.find_all('td')
		this_row_data = [data.text.strip() for data in row_data]
		d = _parse_row(this_row_data)
		df.loc[len(df)] = d
	return df 


def get_table_columns(table):
	titles = table.find_all('th')
	table_columns = [title.text for title in titles if title.text]
	# Manual clean up because some columns are not labeled 
	table_columns.append("From Previous")
	table_columns.append("From First")

	return table_columns


def save_results(df: pd.DataFrame,
    			 database: str,
				 category: str, 
				 logger: logging.Logger,
				 output: str
                ) -> None:
	connection = sqlite3.connect(database)
	cursor = connection.cursor()
	res = cursor.execute(f"SELECT name FROM sqlite_master WHERE name='{category}'").fetchone()
	if res is None:
		logger.info("Saving to the database")
		df.to_sql(name=category, con=connection)
	else:
		logger.info("The table already exists in the database. Saving to csv.")
		df.to_csv(output)


def main(url: str,
    	 category: str,
         year: str = '2024',
         round: str = 'final',
         verbose: bool = False,
         logger: logging.Logger = None,
         output: str | Path = None,
         filename: str = None,
         database: str = 'wjpc2024.db'
        ) -> None:
    # Initiates default logger if logger not given
	if verbose and logger is None:
		logger = logging.getLogger(__name__)
		logging.basicConfig(level=logging.INFO,
						format='%(asctime)s - %(levelname)s: %(message)s')
	# Checks for validating output paths
	if output is not None:		
		output = Path(output)
		if not output.exists(): output.mkdir()
		if filename is None:
			filename = f'wjpc_{year}_{category}_{round}.csv'

	page = requests.get(url)
	soup = BeautifulSoup(page.text, features='lxml')

	# Spanish/English mix because of Spanish website
	table = soup.find_all('table', id='participantes')[0]
	cols = get_table_columns(table)

	# Dropping unneeded columns
	df = pd.DataFrame(columns=cols)
	df = parse_data(df, table)
	df = df.drop(columns=['From Previous', 'From First'])
 
	save_results(df, output/database, category, logger, output/filename)


if __name__ == "__main__":
	logger = logging.getLogger(__name__)
	logging.basicConfig(level=logging.INFO,
						format='%(asctime)s - %(levelname)s: %(message)s')
 
	parser = ArgumentParser()
	# Required Arguments
	parser.add_argument('category', type=str, metavar='category',
                    	choices=['individual', 'pairs', 'teams'],
                     	help='The category of results to analyze.')
 
	# Optional Arguments
	parser.add_argument('--verbose', '-v',
						action='store_true',
						help='To print out status information.')
	parser.add_argument('--year', type=str, default='2024',
						help='The year of the World Jigsaw Puzzle Championships.')
	parser.add_argument('--round', type=str, default='final',
                     	help='The specific round of results to get.')
	parser.add_argument('--url', type=str, 
						default='https://www.worldjigsawpuzzle.org/wjpc',
						help='The url to the competition results.')
	parser.add_argument('--output', '-o', type=str, default='./results',
                     	help='The path to the directory to save the results.')
	
	args = parser.parse_args()

	# WJPC URL structure: COMPETITION/YEAR/CATEGORY/ROUND
	args.url = f'{args.url}/{args.year}/{args.category}/{args.round}'

	# Checks for validating output paths
	args.output = Path(args.output)
	if not args.output.exists(): 
		if args.verbose: logger.info(f'Creating output dir at {args.output.absolute()}')
		args.output.mkdir()
	args.filename = f'wjpc_{args.year}_{args.category}_{args.round}.csv'
	
	if args.verbose:
		logger.info('ARGUMENTS:')
		for arg, val in args.__dict__.items():
			logger.info(f'{arg}: {val}')
   
	main(url=args.url,
		 category=args.category,
         year=args.year,
         round=args.round,
         verbose=args.verbose,
         logger=logger,
         output=args.output,
         filename=args.filename
      )
