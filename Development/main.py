#THE IMPORTS GO HERE
from RadioData import RadioData
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter  
import sys
import threading
from Visualisation import MainWindow, run_server
from PyQt6.QtWidgets import QApplication
from ImportWindow import ImportWindow


threading.Thread(target=run_server, daemon=True).start() # starts a thread to run the surver
app = QApplication(sys.argv) # creates an app instance

import_window = ImportWindow() # starts the import csv window
if not getattr(import_window, "csv_path", ""):
    sys.exit()

#the radio file becomes what ever the user set
radio_data_file = import_window.csv_path
try:
    OBSERVER_LAT = float(import_window.lat) #lat
    OBSERVER_LON = float(import_window.lon) #lon
except ValueError:
    sys.exit()

xml_path = import_window.xml_path #xml path or creates one if there is no path selected

# then use radio_data_file, OBSERVER_LAT, OBSERVER_LON
radioData = RadioData(radio_data_file)
power_list = radioData.file_to_power_list()
time_list = radioData.file_to_time_list()
ra_list, dec_list = radioData.file_to_coords(OBSERVER_LAT, OBSERVER_LON)

#this creates the graph
fig, ax = plt.subplots()

# takes the length of the time_list and makes a list of like 0,1,2,3 and so on till the length of the time_list
indices_x = list(range(len(time_list)))

# boundries otherwise it puts all the times whoch looks terrible and the sizing for the y makes the graph look like a straight line
ax.set_xlim(0, len(time_list))
ax.set_ylim(min(power_list), max(power_list)) 

# put emtpy lists to add the list of values for x and y
line, = ax.plot([], [], color='red') 

# formats the time to show some of the times on the graph otherwise it looks like a big block of black box
tick_positions = [int(i * (len(time_list) - 1) / 9) for i in range(10)]
tick_labels = [time_list[pos] for pos in tick_positions]
ax.xaxis.set_major_locator(FixedLocator(tick_positions))
ax.xaxis.set_major_formatter(FixedFormatter(tick_labels))

# changes the labale size of both axies to fit the size of the graph
ax.tick_params(axis='both', labelsize=3)
fig.tight_layout()
window = MainWindow(radio_data_file, ra_list, dec_list, indices_x, time_list, power_list, fig, ax, line, 1200, 600)
window.show()

sys.exit(app.exec()) #exit app when the window is closed