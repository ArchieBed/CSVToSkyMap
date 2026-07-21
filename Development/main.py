#THE IMPORTS GO HERE
from RadioData import RadioData
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter  
import sys
import threading
from Visualisation import MainWindow, run_server
from PyQt6.QtWidgets import QApplication


# LAT AND LON VERY IMPORTANTTTTT
OBSERVER_LAT = -37.8136
OBSERVER_LON = 144.9631

radio_data_file = "17-05-26.csv" #the chosen radio file

#this creates the graph
fig, ax = plt.subplots()

radioData = RadioData(radio_data_file) #creates an object using the file

# power and time list for the points for graph
power_list = radioData.file_to_power_list()
time_list = radioData.file_to_time_list()

# ra list and dec list to move the skymap
ra_list, dec_list = radioData.file_to_coords(OBSERVER_LAT, OBSERVER_LON)

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

threading.Thread(target=run_server, daemon=True).start() # creates a thread to run a local server for the skymap
app = QApplication(sys.argv)

# creates the mainwindow from the class pbject
window = MainWindow(radio_data_file, ra_list, dec_list, indices_x, time_list, power_list, fig, ax, line, 1200, 600)
window.show()


sys.exit(app.exec()) #exit app when the window is closed