# Script that create a matrix of emotional valence around a certain point

from point_function import getValence
import math
import time
import pandas as pd
import math

from geographiclib.geodesic import Geodesic

geod = Geodesic.WGS84


point = [48.856613, 2.352222] # Center of Paris

radius = 1 # Radius of the zone to analyse (width & height = 2 * radius) - km

resolution = 0.2 # Size of a matrix cell - km

dlat = abs(point[0] - geod.Direct(point[0], point[1], 180, resolution*1000)["lat2"]) # Approximation of resolution*1000 degree lat
dlon = abs(point[1] - geod.Direct(point[0], point[1], 90, resolution*1000)["lon2"]) # Approximation of resolution*1000 degree long

precision = 50 # number of tweet to gather to calculate emotional valence - the greater you search for, the older tweets you'll get

sub_list = [i for i in range(-int((radius/resolution)), int((radius/resolution)) + 1)] # Coordinates array

points_lat = [point[0] + (s * dlat) for s in sub_list] # Lat array

points_long = [point[1] + (s * dlon) for s in sub_list] # Long array

data = []

for x in points_lat:
    l = []
    print(x) # Indicator of the progression
    for y in points_long:
        print(y) # Indicator of the progression
        try:
            l.append(getValence(x, y, resolution, precision))
            var = False
        except Exception as e:
            print("Erreur - passe") # Happening for 5 - 7 % of positions
            l.append(None)
            
    data.append(l)


columns = [str(i) for i in points_long]
index = [str(i) for i in points_lat]

df = pd.DataFrame(data=data,index=index,columns=columns)

df.to_excel("data.xlsx") # Export to xlsx file
    
    
