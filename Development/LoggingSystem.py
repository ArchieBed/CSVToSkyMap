#THE IMPORTS GO HERE
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

# class for storing xml logger features
class XmlLogger:
    def __init__(self, filename):
        self.filename = filename + "_saved_points.xml"
        self._ensure_xml_file()

    # makes sure that the xml file exist. If it doesn't then it creates one
    def _ensure_xml_file(self):
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
            root = ET.Element("UserSelectedPoints")
            tree = ET.ElementTree(root)
            self._write_pretty_xml(tree)

    # this can write into the xml file what ever you want
    def _write_pretty_xml(self, tree):
        raw_string = ET.tostring(tree.getroot(), encoding="utf-8")
        parsed_string = minidom.parseString(raw_string)
        pretty_xml = parsed_string.toprettyxml(indent="    ")
        
        cleaned_xml = "\n".join([line for line in pretty_xml.splitlines() if line.strip()])
        
        with open(self.filename, "w", encoding="utf-8") as f: # remember this on the sac, i used it again. booya
            f.write(cleaned_xml)

    # logs the selected point givin by the graph infomation and writes it into the xml file
    def log_selected_point(self, time_str, power_val, ra_val, dec_val):
        try:
            tree = ET.parse(self.filename)
            root = tree.getroot()
        except Exception:
            root = ET.Element("UserSelectedPoints")
            tree = ET.ElementTree(root)

        log_date = datetime.now().strftime("%Y-%m-%d")

        entry = ET.SubElement(root, "SavedPoint")
        ET.SubElement(entry, "LogDate").text = log_date
        ET.SubElement(entry, "DataTime").text = str(time_str)
        ET.SubElement(entry, "PowerDBFS").text = f"{power_val}"
        ET.SubElement(entry, "RightAscension").text = f"{ra_val:.4f}"
        ET.SubElement(entry, "Declination").text = f"{dec_val:.4f}"

        self._write_pretty_xml(tree)

    #retreives all log points from each of the user selected points and appends that to a dic
    def get_all_logged_points(self):
        points = []
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
            return points
        try:
            tree = ET.parse(self.filename)
            root = tree.getroot()
            for entry in root.findall("SavedPoint"):
                points.append({
                    "date": entry.find("LogDate").text if entry.find("LogDate") is not None else "",
                    "time": entry.find("DataTime").text if entry.find("DataTime") is not None else "",
                    "power": entry.find("PowerDBFS").text if entry.find("PowerDBFS") is not None else "",
                    "ra": entry.find("RightAscension").text if entry.find("RightAscension") is not None else "",
                    "dec": entry.find("Declination").text if entry.find("Declination") is not None else ""
                })
        except Exception as e:
            print(f"Error reading XML logs: {e}")
        return points