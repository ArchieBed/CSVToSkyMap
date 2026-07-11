from RadioData import RadioData
import matplotlib.pyplot as plt
import numpy as np
import sys
import threading
from Visualisation import AladinServer, SkyViewport, run_server
from PyQt6.QtWidgets import QApplication

fig, ax = plt.subplots()

radio_data_file = "17-05-26.csv"

radioData = RadioData(radio_data_file)

power_list = radioData.file_to_power_list()
time_list = radioData.file_to_time_list()

x = time_list
line, = ax.plot(x, power_list)

threading.Thread(target=run_server, daemon=True).start()

app = QApplication(sys.argv)
window = SkyViewport()
window.show()

plt.show()
sys.exit(app.exec())
