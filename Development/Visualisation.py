#THE IMPORTS GO HERE
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer, Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import mplcursors
import matplotlib as mpl
from LoggingSystem import XmlLogger

#this html script just for the set up for a aladin skyviewer html server. So i can customize the fov and targets and stuff
ALADIN_HTML = """
<!doctype html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <script type="text/javascript" src="https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js" charset="utf-8"></script>
    <style>
        html, body, #aladin-lite-div { margin: 0; padding: 0; width: 100%; height: 100%; background-color: #000; overflow: hidden; }
    </style>
</head>
<body>
    <div id="aladin-lite-div"></div>
    <script type="text/javascript">
        var aladin;
        A.init.then(() => {
            aladin = A.aladin('#aladin-lite-div', {
                survey: "https://alasky.cds.unistra.fr/DSS/DSSColor/",
                fov: 16,  
                target: "0, 0",
                showCooGrid: false,  
                showReticle: true     
            });
        });
    </script>
</body>
</html>
"""
# this just creates up a little server to run the html page
class AladinServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(ALADIN_HTML.encode("utf-8")) #sends the html code to the server to make the skymap

def run_server(): # this command will start it up
    HTTPServer(('127.0.0.1', 8085), AladinServer).serve_forever()

# this is the main window to the application that runs the entire program
class MainWindow(QMainWindow):
    def __init__(self, radio_file, ra_list, dec_list, numeric_timestamps, actual_time_list, power_list, fig, ax, line, WIDTH, HEIGHT):
        super().__init__() # this is for Qmainwindow
        self.setWindowTitle("The Multitool Radio Astronomy Analysis Application")
        self.setGeometry(100, 100, WIDTH, HEIGHT) 

        # sets the ra and dec list if their is a valid one, otherwise it sets as empty
        self.ra_list = ra_list if ra_list else [] 
        self.dec_list = dec_list if dec_list else []
        
        self.numeric_timestamps = numeric_timestamps # this is the numeric times
        self.actual_time_list = actual_time_list # this is the string times (just for the graph stuff)
        self.power_list = power_list            
        self.ax = ax                             
        self.line = line                         
        
        self.current_index = 0                   # useful later when figuring out the clock time step

        # creates a object of the logger class for our logger window
        self.logger = XmlLogger(radio_file)

        #creates the window widget
        main_widget = QWidget()                  
        self.setCentralWidget(main_widget)       
        
        # splits the application window for the sky map on the left and the graph and logging system on the right
        base_layout = QHBoxLayout(main_widget)        
        base_layout.setContentsMargins(10, 10, 10, 10)    
        base_layout.setSpacing(10)                    

        # this embeds the skymap and creates it in the software window
        self.web_view = QWebEngineView()         
        self.web_view.load(QUrl("http://127.0.0.1:8085")) 
        self.web_view.setFixedSize(600, 800)
        base_layout.addWidget(self.web_view)

        # this sets the right side layout to stack the graph ontop of the logging system
        right_stack_layout = QVBoxLayout()
        right_stack_layout.setSpacing(15)

        # this embeds the graph ontop of the stack
        self.canvas = FigureCanvas(fig)
        self.canvas.setMinimumWidth(700)
        self.canvas.setFixedHeight(450)          
        right_stack_layout.addWidget(self.canvas) 

        # this creates the logging system table with colums of each of the things it saves
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["Log Date", "Data Time", "Power (dBFS)", "RA (°)", "Dec (°)"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.setMinimumWidth(600)
        self.log_table.setFixedHeight(280)
        right_stack_layout.addWidget(self.log_table)

        # adds the stacked layout to the global layout so it can be shown
        base_layout.addLayout(right_stack_layout, stretch=1)

        # loads the tabel from the file that is associcated with the filename
        self.refresh_log_table()

        # this sets up the clock timer
        self.timer = QTimer(self)                
        self.timer.timeout.connect(self.advance_time_step) 
        self.web_view.loadFinished.connect(self.start_animation) 

        # i wanted the applcation to show fullscreen but not completely full screen
        self.showMaximized()

        # enables the clicking intercation on the graph
        self.line.set_picker(5)
        
        # this sets up the hover cursor set up. Had a lot of issue with the conversion of the times becuase my times were strings which is why the indecies stuff was impotant
        self.cursor = mplcursors.cursor(self.line, hover=True)
        @self.cursor.connect("add")
        def _(sel):
            idx = int(round(sel.target[0]))
            if 0 <= idx < len(self.numeric_timestamps):
                timestamp = self.actual_time_list[idx]
                power_val = sel.target[1]
                sel.annotation.set_text(f"Time: {timestamp}\nPower: {power_val} dBFS")

        # connects the click event to what we want happen
        self.canvas.mpl_connect('pick_event', self.on_graph_click)

    # here is the function of what we want happen when apart of the graph is clicked
    def on_graph_click(self, event):
        if event.artist == self.line:
            click_index = event.ind[0]
            
            # this saves the infomation
            if 0 <= click_index < len(self.numeric_timestamps):
                time_str = self.actual_time_list[click_index]
                power_val = self.power_list[click_index]
                ra_val = self.ra_list[click_index]
                dec_val = self.dec_list[click_index]

                # passes off the info to the xml log handler
                self.logger.log_selected_point(time_str, power_val, ra_val, dec_val)
                
                # refreaes the table to display the new infomation
                self.refresh_log_table()

    def on_cell_click(self, ra, dec):
        js_script = f"if (typeof aladin !== 'undefined') {{ aladin.gotoRaDec({ra}, {dec}); }}" #
        self.web_view.page().runJavaScript(js_script) 

    # here is the function to refresh the table and query the xml reader
    def refresh_log_table(self):
        logged_items = self.logger.get_all_logged_points()
        self.log_table.setRowCount(len(logged_items))
        
        # sets the item from the list
        for row_idx, item in enumerate(logged_items):
            self.log_table.setItem(row_idx, 0, QTableWidgetItem(item["date"]))
            self.log_table.setItem(row_idx, 1, QTableWidgetItem(item["time"]))
            self.log_table.setItem(row_idx, 2, QTableWidgetItem(item["power"]))
            self.log_table.setItem(row_idx, 3, QTableWidgetItem(item["ra"]))
            self.log_table.setItem(row_idx, 4, QTableWidgetItem(item["dec"]))
            
        # an auto scroll when a new item is added
        self.log_table.scrollToBottom()

    #this function makes the timer start
    def start_animation(self, success):
        if success and self.ra_list:
            self.timer.start(100)
    
    #this function updates the ra and dec on the skymap each step in the timer
    def advance_time_step(self):
        if self.current_index < len(self.ra_list): 
            ra = self.ra_list[self.current_index] 
            dec = self.dec_list[self.current_index] 
            #just a command to move the ra and dec to their new values according to the current index its on
            js_script = f"if (typeof aladin !== 'undefined') {{ aladin.gotoRaDec({ra}, {dec}); }}" #
            self.web_view.page().runJavaScript(js_script) 

            #this adds the graph to draw a new point on the graph in conjunction with my clock system
            current_x = self.numeric_timestamps[:self.current_index + 1] 
            current_y = self.power_list[:self.current_index + 1] 
            
            self.line.set_data(current_x, current_y) 
            self.canvas.draw_idle()              
            
            self.current_index += 1              
        else:
            self.timer.stop() #stops the timer when everything is done