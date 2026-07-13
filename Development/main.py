#THE IMPORTS GO HERE
from RadioData import RadioData
import matplotlib.pyplot as plt
import sys
import threading
from Visualisation import SkyViewport, run_server
from PyQt6.QtWidgets import QApplication

#this creates the graph
fig, ax = plt.subplots()

radio_data_file = "17-05-26.csv" #the chosen radio file

radioData = RadioData(radio_data_file) #creates an object using the file

# LAT AND LON VERY IMPORTANTTTTT
OBSERVER_LAT = -37.8136
OBSERVER_LON = 144.9631

# power and time list for the points for graph
power_list = radioData.file_to_power_list()
time_list = radioData.file_to_time_list()

# ra list and dec list to move the skymap
ra_list, dec_list = radioData.file_to_coords(OBSERVER_LAT, OBSERVER_LON)


x = time_list
line, = ax.plot(x, power_list) #plottingggg

threading.Thread(target=run_server, daemon=True).start() # creates a thread to run a local server for the skymap

#here is the creation of the window to show the skymap
app = QApplication(sys.argv)
window = SkyViewport(ra_list, dec_list, 600, 600)
window.show()


plt.show() #show graph
sys.exit(app.exec()) #exit app when the skymap window is closed
