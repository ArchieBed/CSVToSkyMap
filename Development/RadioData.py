import pandas as pd

class RadioData():
    def __init__(self, radio_data_file):
        self.radio_data_file = pd.read_csv(radio_data_file)
        self.timestamps = []
        self.custom_filters = []

    def read_file(self):
        head = self.radio_data_file.head(10)
        print(head)

    def file_to_power_list(self):
        power_level = self.radio_data_file['Power (dBFS)'].values.tolist()
        return power_level
    
    def file_to_time_list(self):
        time_list = self.radio_data_file['Time'].values.tolist()
        return time_list