"""
A helper class for easily accessing stats from the results
"""
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class ResultStats:
	def __init__(self, 
              	 results: pd.DataFrame,
                 gradient: tuple[str] = ('#0096C7', '#FFA500')
              ) -> None:
		self.df = results
		self.n_countries = len(self.df["Country"].unique())
		self.dnf = len(self.df[self.df['Time'].str.contains('Pieces')])
		self.finishers = self.df[self.df['Time'].str.contains('Pieces') == False]
		self.gradient = gradient
		self.avg_time = self.get_average_time()
  
  
	def get_average_time(self) -> str:
		times = [datetime.datetime.strptime(t.strip(), "%H:%M:%S").time() 
                             					for t in self.finishers['Time']]

		hour = [x.hour for x in times]
		min = [x.minute for x in times]
		sec = [x.second for x in times]
  
		self.finishers = self.finishers.assign(_time=times,
												hour=hour,
												min=min,
												second=sec
                                        	)
		
		# Calculate the average number of seconds 
		avg_sec = int((sum(hour)* 3600 +  sum(min) * 60 + sum(sec)) / len(times))
		
		# Convert the seconds back to hours:minutes:seconds
		return "0" + str(datetime.timedelta(seconds = avg_sec))


	def get_faster_than_1_hr(self):
		limit = 3600
		return len(self.finishers[self.finishers["hour"] == 0])



	def get_color_gradient(self, n):
		"""
		Given two hex colors, returns a color gradient
		with n colors.

		SOURCE: Gradient functions from https://medium.com/@BrendanArtley/matplotlib-color-gradients-21374910584b 
		"""
		def hex_to_RGB(hex_str):
			""" #FFFFFF -> [255,255,255]"""
			#Pass 16 to the integer function for change of base
			return [int(hex_str[i:i+2], 16) for i in range(1,6,2)]
		assert n > 1
		c1_rgb = np.array(hex_to_RGB(self.gradient[0]))/255
		c2_rgb = np.array(hex_to_RGB(self.gradient[1]))/255
		mix_pcts = [x/(n-1) for x in range(n)]
		rgb_colors = [((1-mix)*c1_rgb + (mix*c2_rgb)) for mix in mix_pcts]
		return ["#" + "".join([format(int(round(val*255)), "02x") for val in item]) for item in rgb_colors]



if __name__ == "__main__":
	df = pd.read_csv("data/wjpc_2024_individual_final.csv", 
				index_col=0
				)
	df = df.rename(columns={"#": "Place"})
	df = df.set_index('Place')
	df = df[['Name', 'Time', 'Country', 'Origin']]
	res = ResultStats(df)
	res.df.info()
	res.finishers.info()

