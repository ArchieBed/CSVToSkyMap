#THE IMPORTS GO HERE
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import QUrl, QTimer

#this html s just for the set up for a aladin skyviewer html server. So i can customize the fov and targets and stuff
# THIS HTML SCRIPT WAS WRITTEN WITH THE HELP OF GOOGLES AI (GEMINAI).
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
                fov: 16,  <!-- CHANGE FOV TO WHAT THE TELESCOPE IS!!! -->             
                target: "0, 0",
                showCooGrid: false,  <!-- i dont like it on personally -->    
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

# this class is to project the html page on a QWebEngine viewer
class SkyViewport(QMainWindow):
    def __init__(self, ra_list, dec_list, WIDTH, HEIGHT):
        super().__init__() #QMainWindow init for its class
        #sets up window
        self.setWindowTitle("skymap")
        self.setGeometry(0, 0, WIDTH, HEIGHT) 

        #gets the ra and dec lists from parametres
        self.ra_list = ra_list if ra_list else []
        self.dec_list = dec_list if dec_list else []
        self.current_index = 0 #starts the list at the start. IMPORTANT FOR ANIMATION

        #im gonna be honest idk, this was on the documentation
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0) 

        # there is where it embeds
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl("http://127.0.0.1:8085")) #embeds the url to the server to display the skymap
        layout.addWidget(self.web_view)

        #this is the timer to tick to make the skymap move with the coords
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance_time_step)

        #will start timer when the server connects and finishes loading
        self.web_view.loadFinished.connect(self.start_animation)

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
            js_script = f"if (typeof aladin !== 'undefined') {{ aladin.gotoRaDec({ra}, {dec}); }}"
            self.web_view.page().runJavaScript(js_script)
            
            self.current_index += 1
        else:
            self.timer.stop() #stops the timer when everything is done
