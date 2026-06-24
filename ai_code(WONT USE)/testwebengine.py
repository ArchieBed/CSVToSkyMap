import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer

# Matplotlib Qt integration modules
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates

# Astronomy calculation modules
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord
import astropy.units as u

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

        function navigateToCoords(ra, dec) {
            if (aladin) {
                aladin.gotoRaDec(ra, dec);
            }
        }
    </script>
</body>
</html>
"""

class TinyAladinServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(ALADIN_HTML.encode("utf-8"))
    def log_message(self, format, *args): pass

def run_server():
    HTTPServer(('127.0.0.1', 8085), TinyAladinServer).serve_forever()

class AutomatedZenithApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Melbourne Real-Time Sky & Live Telemetry Deck")
        self.setGeometry(100, 100, 1400, 750) 

        # 1. Load telemetry base data arrays
        self.csv_file = '17-05-26.csv'
        try:
            self.df = pd.read_csv(self.csv_file)
            self.df["Datetime"] = pd.to_datetime(self.df["Date"] + " " + self.df["Time"], errors="coerce")
            self.df = self.df.dropna(subset=["Datetime", "Power (dBFS)"])
            
            window_size = 110
            self.df["Average"] = self.df["Power (dBFS)"].rolling(window=window_size, center=True).mean()
            self.time_playlist = self.df['UTC'].str.replace('Z', '', regex=False).tolist()
            print(f"Data parsed successfully. {len(self.time_playlist)} frames available.")
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            self.time_playlist = []
            self.df = pd.DataFrame()
            
        self.current_index = 0

        # 2. Build Canvas structures ready for incremental stream accumulation
        self.fig = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        
        # Define line objects
        self.line_raw, = self.ax.plot([], [], label="Raw Data", linewidth=1, alpha=0.5)
        self.line_avg, = self.ax.plot([], [], label="Rolling Avg (window=110)", linewidth=2, color="red")
        
        # Live tracking cursor line placeholder
        self.current_time_line = self.ax.axvline(x=pd.Timestamp.now(), color='gold', linestyle='--', linewidth=2, label='Current Point')
        
        self.ax.set_title("Real-Time Power (dBFS) Stream Engine")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Power (dBFS)")
        self.ax.legend(loc='upper left')
        self.ax.grid(True)
        
        # Auto-configure time formatting styles on horizontal coordinate axis tracks
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        # Pre-set vertical limits using computed minimums and maximums from data source parameters
        if not self.df.empty:
            self.ax.set_ylim(self.df["Power (dBFS)"].min(), self.df["Power (dBFS)"].max())
            # Pre-set horizontal bounds to capture your whole file timeline bounds securely
            self.ax.set_xlim(self.df["Datetime"].min(), self.df["Datetime"].max())

        self.fig.autofmt_xdate()

        # 3. Structural UI Components Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Controls Row
        control_layout = QHBoxLayout()
        self.status_label = QLabel(f"Current Target Time: {self.time_playlist[self.current_index] if self.time_playlist else 'None'} UTC")
        control_layout.addWidget(self.status_label)

        self.play_btn = QPushButton("Start Live Update", self)
        self.play_btn.setCheckable(True)
        self.play_btn.clicked.connect(self.toggle_playback)
        control_layout.addWidget(self.play_btn)
        
        self.show_raw_cb = QCheckBox("Show Raw", self)
        self.show_raw_cb.setChecked(True)
        self.show_raw_cb.clicked.connect(self.update_plot_visibility)
        control_layout.addWidget(self.show_raw_cb)
        
        self.show_avg_cb = QCheckBox("Show Average", self)
        self.show_avg_cb.setChecked(True)
        self.show_avg_cb.clicked.connect(self.update_plot_visibility)
        control_layout.addWidget(self.show_avg_cb)
        
        layout.addLayout(control_layout)

        # Horizontal Viewport Splitting Grid
        viewport_layout = QHBoxLayout()
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl("http://127.0.0.1:8085"))
        viewport_layout.addWidget(self.web_view, stretch=1)
        viewport_layout.addWidget(self.canvas, stretch=1)
        layout.addLayout(viewport_layout)

        # Automation Loop Engine
        self.loop_timer = QTimer(self)
        self.loop_timer.timeout.connect(self.update_to_next_time)

    def update_plot_visibility(self):
        self.line_raw.set_visible(self.show_raw_cb.isChecked())
        self.line_avg.set_visible(self.show_avg_cb.isChecked())
        self.canvas.draw_idle()

    def toggle_playback(self):
        if self.play_btn.isChecked():
            self.play_btn.setText("Pause Live Update")
            self.update_to_next_time()
            self.loop_timer.start(100) 
        else:
            self.play_btn.setText("Start Live Update")
            self.loop_timer.stop()

    def update_to_next_time(self):
        if not self.time_playlist or self.df.empty:
            return

        timestamp_str = self.time_playlist[self.current_index]
        self.status_label.setText(f"Current Target Time: {timestamp_str} UTC")

        try:
            # 1. Update Celestial Telescope Coordinates (Left Viewport Screen)
            target_time = Time(timestamp_str, format='isot', scale='utc')
            melbourne_loc = EarthLocation(lat=-37.8136*u.deg, lon=144.9631*u.deg, height=0*u.m)
            straight_up = SkyCoord(az=0*u.deg, alt=90*u.deg, frame='altaz', obstime=target_time, location=melbourne_loc)
            space_coords = straight_up.transform_to('icrs')

            self.web_view.page().runJavaScript(f"navigateToCoords({space_coords.ra.deg}, {space_coords.dec.deg});")

            # 2. Slice Data Stream Up To The Current Index Frame Pointer
            current_history_df = self.df.iloc[:self.current_index + 1]
            
            x_data = current_history_df["Datetime"]
            y_raw = current_history_df["Power (dBFS)"]
            y_avg = current_history_df["Average"]

            # Push arrays into line structures
            self.line_raw.set_data(x_data, y_raw)
            self.line_avg.set_data(x_data, y_avg)

            # Draw the line indicator on top of the moving timeline
            current_dt = pd.to_datetime(timestamp_str)
            self.current_time_line.set_xdata([current_dt, current_dt])

            # Re-render changes instantly
            self.canvas.draw_idle()

        except Exception as e:
            print(f"Real-Time Stream Error: {e}")

        # Cycle index pointer elements
        self.current_index = (self.current_index + 1) % len(self.time_playlist)


if __name__ == '__main__':
    threading.Thread(target=run_server, daemon=True).start()
    app = QApplication(sys.argv)
    window = AutomatedZenithApp()
    window.show()
    sys.exit(app.exec())