from datetime import datetime

class Leg:
    def __init__(self, args: dict) -> None:
        self.mode = args["mode"]
        self.distance = args["distance"]
        self.line = args["line"]
        
    def __repr__(self) -> str:
        s = f"\n\tMode: {self.mode}"
        if self.line is not None:
            s += f", Line: {self.line['publicCode']}"
        return s 
        
class TripPattern:
    def __init__(self, args: dict) -> None:
        self.expected_start_time = datetime.strptime(args["expectedStartTime"],
                                                     '%Y-%m-%dT%H:%M:%S%z')
        self.duration = args["duration"]
        self.walk_distance = args["walkDistance"]
        self.legs = [Leg(l) for l in args["legs"]]
        
    def __repr__(self) -> str:
        return f"Leave by: {self.expected_start_time}\nDuration: {self.duration}\n"\
            	f"Walking: {self.walk_distance}\nLegs: {self.legs}\n\n"
    
class Trip:
	def __init__(self, res: dict) -> None:
		if not isinstance(res, dict):
			raise TypeError("Res must be of type `dict`")
		
		temp = res.get("trip", None)
		if temp is None:
			raise ValueError("Trip response does not include a 'trip' key.")
		
		temp = temp.get("tripPatterns", None)
		if temp is None:
			raise ValueError("No trip patterns were found")
		
		
		self.trip_patterns = [TripPattern(tp) for tp in temp]
		
	def __repr__(self) -> str:
		s = ""
		for i in range(len(self.trip_patterns)):
			s += f"Trip {i+1}:\n"
			s += str(self.trip_patterns[i])
		return s
    
if __name__ == "__main__":
    test = {'trip': {'tripPatterns': [{'expectedStartTime': '2024-08-27T14:06:00+02:00', 'duration': 1710, 'walkDistance': 352.84, 'legs': [{'mode': 'rail', 'distance': 17476.26, 'line': {'id': 'NSB:Line:L13', 'publicCode': 'R13'}}, {'mode': 'foot', 'distance': 352.84, 'line': None}, {'mode': 'metro', 'distance': 4946.58, 'line': {'id': 'RUT:Line:5', 'publicCode': '5'}}]}, {'expectedStartTime': '2024-08-27T14:16:36+02:00', 'duration': 1644, 'walkDistance': 352.84, 'legs': [{'mode': 'rail', 'distance': 17466.75, 'line': {'id': 'NSB:Line:R10', 'publicCode': 'RE10'}}, {'mode': 'foot', 'distance': 352.84, 'line': None}, {'mode': 'metro', 'distance': 4946.58, 'line': {'id': 'RUT:Line:5', 'publicCode': '5'}}]}, {'expectedStartTime': '2024-08-27T14:26:00+02:00', 'duration': 1680, 'walkDistance': 352.84, 'legs': [{'mode': 'rail', 'distance': 17466.75, 'line': {'id': 'NSB:Line:R11', 'publicCode': 'RE11'}}, {'mode': 'foot', 'distance': 352.84, 'line': None}, {'mode': 'metro', 'distance': 4946.58, 'line': {'id': 'RUT:Line:4', 'publicCode': '4'}}]}]}}
    print(Trip(test))