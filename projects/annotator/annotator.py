"""
Annotator class for annotating text data.
This class provides a graphical user interface (GUI) for annotating text data using checkboxes. It allows the user to select multiple annotations from a predefined list of values.

Class Attributes:
	annotator_font (tuple): The font style for the annotator.
	annotator_width (int): The width of the annotator.
	annotator_wraplength (int): The wrap length of the annotator.
	annotator_side_pad (int): The side padding of the annotator.
Instance Variables:
	df (pd.DataFrame): The input DataFrame containing the text data to be annotated.
	values (list[str]): The list of values to choose from for annotations.
	output (str): The path to save the annotated results.
	title (str): The title of the annotator GUI window.
	display_data (list[str]): The list of columns to display as metadata.
	start_idx (int): The index of the start instance.
	labels (dict[str, Label]): A dictionary mapping feature names to Label objects for displaying metadata.
	selected (list[str]): The list of selected annotations.
	checkboxes (list[Checkbutton]): The list of Checkbutton objects for selecting annotations.
	submit (Button): The Button object for submitting the annotations.
Methods:
	__init__(self, df, values, output, title, display_data, start_idx)
		Initializes the Annotator object.
	_get_input_row(self)
		Creates the input row of checkboxes and submit button.
	_get_labels(self)
		Creates the labels for displaying text and metadata.
	on_checkbox_click(self, val)
		Handles the checkbox click event.
	on_submit(self)
		Handles the submit button click event including saving results, resetting the annotation checkboxes, and updating labels with the next instance.
	update_labels(self)
		Updates the labels with new data.
  
TODOs:
- Make `on_submit` more robust to handle different outputs
- Fix the keybinding for checkboxes in `__init__`, currently set to 5 bindings and done manually 
- TODO: Add save state button and log
"""

import json
import pandas as pd

from argparse import ArgumentParser
from tkinter import *


class Annotator(Tk):
	annotator_font: tuple = ("Helvetica", 18, "")
	annotator_width: int = 50
	annotator_wraplength: int = 500
	annotator_side_pad: int = 10
 
	def __init__(self,
				df: pd.DataFrame, 
				values: list[str],
				output: str,
				title: str = "Annotator",
				display_data: list[str] = None,
				start_idx: int = 0,
			) -> None:
		super().__init__()
		self.title(title)
		
		df["working_index"] = [i for i in range(len(df))]
  
		if display_data is None:
			display_data = df.columns
   
		assert "text" in display_data, "Annotator requires 'text' column"

		self.df = df
		self.output = output
  
		self.display_data = display_data
		self.values = values
		self.start_idx = self.current_idx = start_idx
		self.labels = self._get_labels()
		self.selected = []
		self.checkboxes, self.submit = self._get_input_row()

		# Bind keystrokes 
		self.bind('<Return>', lambda _: self.submit.invoke())
		self.bind('<KP_Enter>', lambda _: self.submit.invoke())
		
		# NOTE: something weird happens when I try to bind in a loop, 
		# so doing this manually for now
		self.bind('1', lambda _: self.checkboxes[0].invoke())
		self.bind('2', lambda _: self.checkboxes[1].invoke())
		self.bind('3', lambda _: self.checkboxes[2].invoke())
		self.bind('4', lambda _: self.checkboxes[3].invoke())
		self.bind('5', lambda _: self.checkboxes[4].invoke())

		self.update_labels()


	def _get_input_row(self) -> tuple[list[Checkbutton], Button]:
		"""
		Instantiates the checkbox `Checkbutton`s and submit `Button` for annotation input row.
  
		Returns:
			tuple[list[Checkbutton], Button]: A tuple containing:
   				- a list of Checkbutton objects, one for each annotation value
       			- a Button object for submitting annotations
		"""
		
		input_row = self.grid_size()[1]
		checkboxes = []
		for i, val in enumerate(self.values):
			var = IntVar()
			checkbox = Checkbutton(self, 
							text=val, 
							variable=var, 
							command=lambda val=val: self.on_checkbox_click(val))
			checkbox.grid(row=input_row, column=i, sticky=W)
			checkboxes.append(checkbox)
		submit = Button(self, 
						text="Submit",
						command=self.on_submit,
						width=self.annotator_width // 5,
						)
		submit.grid(row=input_row, column=len(self.values))
  
		return checkboxes, submit


	def _get_labels(self) -> dict[str: Label]:
		"""
		Generates and returns a dictionary of `Label`s for the text and metadata in the dataset.
		Returns:
			dict[str: Label]: A dictionary containing labels for the annotator class, where each key is the metadata feature and the values are the corresponding `Label` objects.
		"""
		
		labels = {}
		# Remove "text" for special formatting
		features = list(self.display_data.copy())
		features.remove("text")
  
		# Setup Text Label
		main_label = Label(self, text="")
		main_label.grid(row=0, column=0, 
              		   columnspan=len(self.values) + 1)
		main_label.configure(font=self.annotator_font, 
                   			width=self.annotator_width,
                        	wraplength=self.annotator_wraplength, padx=self.annotator_side_pad, 
                        	pady=self.annotator_side_pad,
							background="white"
                         )
		labels["text"] = main_label

		# Setup up remaining metadata labels
		for i, feature in enumerate(features):
			label_key = Label(self, text=feature + ":")
			label_key.grid(row=i+1, column=0) 
			
			label_value = Label(self, text="")
			label_value.grid(row=i+1, column=1, 
              		   columnspan=len(self.values))
			label_value.configure(font=self.annotator_font, 
                   			width=self.annotator_width,
                        	wraplength=self.annotator_wraplength, padx=self.annotator_side_pad, 
                        	pady=self.annotator_side_pad)
			labels[feature] = label_value

		
		return labels
     
     
	def on_checkbox_click(self, val: str) -> None:
		"""
		Handles the click event of a checkbox and updates the selected features for the annotation, `self.selected`.
		Parameters:
			val (str): The value of the checkbox.
		"""
		
		if val in self.selected:
			self.selected.remove(val)
		else:
			self.selected.append(val)
		print(self.selected)
        
        
	def on_submit(self)->None:
		"""
		Handles the submission of the annotator checkboxes.
			- Saves the selected labels, languages, and the original language to a JSON file.
			- Resets the selected list and unchecks the checkboxes.
			- Updates the current index and updates the labels with 
   				information about the next instance.
       
		NOTE: Currently only supports the specific setup for my purpose
		"""
		# Save to res file
		# TODO: Make this more robust to handle different outputs
		res = {"text": self.labels["text"]["text"],
			"languages": self.selected,
			"original": self.df.iloc[self.current_idx]["languages"]}

		with open(self.output, "a") as f:
			json.dump(res, f)
			f.write("\n")
   
		# Reset selected list
		self.selected = []
	
		# Uncheck the check boxes
		for checkbox in self.checkboxes:
			checkbox.deselect()

		# Update labels
		self.current_idx += 1
		self.update_labels()
		
  
	def update_labels(self) -> None:
		"""
		Update the labels with the corresponding values from the dataframe for the instance at the current index.
		"""
		i = self.current_idx
		for feature, label in self.labels.items():
			label["text"] = self.df.iloc[i][feature]
  
  
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