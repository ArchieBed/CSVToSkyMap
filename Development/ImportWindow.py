#i saw this in a stackoverflow quetion thing i thought it looked good
from PyQt6.QtWidgets import (
    QDialog,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QFormLayout,
)

# this is the import window infomation stuff
class ImportDialog(QDialog):
    def __init__(self):
        super().__init__()

        #creates line eidts to change characters. like box typing stuff
        self.csv_path_edit = QLineEdit()
        self.lat_edit = QLineEdit()
        self.lon_edit = QLineEdit()
        self.xml_path_edit = QLineEdit()

        #button to browse for the csv file
        csv_browse = QPushButton("Browse...")
        csv_browse.clicked.connect(self.browse_csv)

        #button to browse for the xml file
        xml_browse = QPushButton("Browse...")
        xml_browse.clicked.connect(self.browse_xml)

        #makes it formatted to button
        csv_layout = QHBoxLayout()
        csv_layout.addWidget(self.csv_path_edit)
        csv_layout.addWidget(csv_browse)

        xml_layout = QHBoxLayout()
        xml_layout.addWidget(self.xml_path_edit)
        xml_layout.addWidget(xml_browse)

        #actully adds it to the main pop up window
        form_layout = QFormLayout()
        form_layout.addRow("CSV file:", csv_layout)
        form_layout.addRow("Latitude:", self.lat_edit)
        form_layout.addRow("Longitude:", self.lon_edit)
        form_layout.addRow("Save XML to:", xml_layout)

        # added a ok and cancel button just to give the user some options
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        #this slaps everythiung together into the one window
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    # function to browse for the csv file using trees
    def browse_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV file", "", "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            self.csv_path_edit.setText(path)

    # function to browse for the xml file using trees
    def browse_xml(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save XML file as", "", "XML Files (*.xml);;All Files (*)"
        )
        if path:
            self.xml_path_edit.setText(path)

#The main window creation
class ImportWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 400, 400)
        dialog = ImportDialog() # creates a instance of the class of all the mini pop up features
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.csv_path = dialog.csv_path_edit.text()
            self.lat = dialog.lat_edit.text()
            self.lon = dialog.lon_edit.text()
            self.xml_path = dialog.xml_path_edit.text()
        else:
            self.close()
