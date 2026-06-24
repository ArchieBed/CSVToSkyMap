from RadioData import RadioData
import matplotlib.pyplot as plt

radioData = RadioData("17-05-26.csv")

power_list = radioData.file_to_power_list()
time_list = radioData.file_to_time_list()

plt.plot(time_list, power_list)
plt.show()