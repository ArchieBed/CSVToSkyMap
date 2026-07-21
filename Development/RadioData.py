#THE IMPORTS GO HERE
import pandas as pd
import datetime

#the big radio data class, this will be a big help for the logging system and reading he csv file
class RadioData():
    def __init__(self, radio_data_file):
        self.radio_data_file = pd.read_csv(radio_data_file) #i love pandas for csv files

    # i was checking if it can read the file. it can. ill leave it here
    def read_file(self):
        head = self.radio_data_file.head(10)
        print(head)

    # takes the power coloum and returns a list
    def file_to_power_list(self):
        power_level = self.radio_data_file['Power (dBFS)'].values.tolist()
        return power_level
    
    # takes the time coloum and returns a list
    def file_to_time_list(self):
        #self.radio_data_file['Time'] = pd.to_datetime(self.radio_data_file['Time'])
        time_list = self.radio_data_file['Time'].values.tolist()
        return time_list
    
    # REALLY ONLY IMPORTANT IF NO RA AND DEC COORDS!!!
    # THIS METHOD OF CONVERSION WAS HELPED WITH GOOGLES AI (GEMINAI), THE CODE ITSELF WAS NOT AI!!!!!
    def file_to_coords(self, lat, lon):
        #checking to see if the csv already has the ra and dec lists
        if 'RA' in self.radio_data_file.columns and 'Dec' in self.radio_data_file.columns:
            if not self.radio_data_file['RA'].dropna().empty:
                ra_list = self.radio_data_file['RA'].values.tolist()
                dec_list = self.radio_data_file['Dec'].values.tolist()
                return ra_list, dec_list
            
        #if it doesn't have then we can take the UTC time in the csv file and create the ra and dec in respect to the lon and lat given by the user.
        ra_list = []
        dec_list = []

        #this is a UTC to ra and dec converter with the lon and lat values
        # it takes each utc value and converts it into the ra and dec, thats why its looping
        for utc_str in self.radio_data_file['UTC'].values:
            dt = datetime.datetime.strptime(utc_str.replace('Z', ''), "%Y-%m-%dT%H:%M:%S.%f") #this is the UTC example: 2026-05-17T00:55:10.934Z

            #extracts the year, month day from the UTC
            year, month = dt.year, dt.month
            day = dt.day + dt.hour/24.0 + dt.minute/1440.0 + dt.second/86400.0 + dt.microsecond/86400000000.0 #how many of that unit are in a day

            #this ajusts for the julian calender, which we use for the algorithm
            if month <= 2:
                year -= 1
                month += 12

            #calculationing for leap year and century corrections
            A = int(year / 100)
            B = 2 - A + int(A / 4)

            #this finds the julian date
            jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
            
            #calculating the amount of days since J2000.0
            D = jd - 2451545.0

            #calculating greenwich mean sidereal time (GMST)
            gmst = (280.46061837 + 360.98564736629 * D) % 360
            
            #HERE CONVERTS IT!!!!
            ra = (gmst + lon) % 360
            
            # puts the ra and dec in their respective lists
            ra_list.append(ra)
            dec_list.append(lat)
        
        # returns the lists when all UTC values have been converted
        return ra_list, dec_list