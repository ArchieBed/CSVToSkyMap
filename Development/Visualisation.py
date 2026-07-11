import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

#this html s just for the set up for a aladin skyviewer html server. So i can customize the fov and targets and stuff
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
                target: "0, -37",
                showCooGrid: false,    
                showReticle: false     
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
        self.wfile.write(ALADIN_HTML.encode("utf-8"))

def run_server(): # this command will start it up
    HTTPServer(('127.0.0.1', 8085), AladinServer).serve_forever()

# this class is to project the html page on a QWebEngine viewer
class SkyViewport(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("skymap")
        self.setGeometry(100, 100, 1000, 700) 

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0) 

        # there is where it embeds
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl("http://127.0.0.1:8085"))
        layout.addWidget(self.web_view)
