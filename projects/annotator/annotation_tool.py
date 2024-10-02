"""
Annotator Tool
This script provides an annotator tool for labeling data in a given input file.
Usage:
	python annotation_tool.py <input> [--output <output>] [--values <values>] [--start_idx <start_idx>]
Arguments:
	<input>                 Path to the input file.
Options:
	--output <output>       Path to save the annotated results. Default is 'validation_multi-label.jsonl'.
	--values <values>       List of values to choose from for annotations. Default is ['nb', 'nn', 'da', 'sv', 'other'].
	--start_idx <start_idx> Index of the start instance. Default is 0.
"""

import json
import pandas as pd

from argparse import ArgumentParser
from annotator import Annotator

if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument("input", type=str, 
						help="Path to input file.")
	parser.add_argument("--output", type=str, 
					default="validation_multi-label.jsonl",
					help="Where to save the results.")
	parser.add_argument("--values", type=list, 
					default=["nb", "nn", "da", "sv", "other"],
					help="What to choose from for annotations")
	parser.add_argument("--start_idx", "-i", type=int, default=0, 
					help="Index of the start instance.")

	args = parser.parse_args()
	df = pd.DataFrame([json.loads(line) 
                    for line in open(args.input, 'r')])
 
	a = Annotator(df, args.values, args.output, start_idx=args.start_idx)
	a.mainloop()