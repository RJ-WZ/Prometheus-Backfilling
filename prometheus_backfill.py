import re
import os
import sys
import ctypes
import csv
import time
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class main_window(QMainWindow):
    def __init__(self):
        super().__init__()
        logo_path = r"C:\Users\RJ\docker\openTSDB_push_delete\backfill_status\PYQT_Backfill\logo.png"
        self.setWindowIcon(QIcon(logo_path))
        self.setWindowTitle("Prometheus Backfilling")
        self.setFixedSize(500, 900)
        self.centralWidget = QWidget()

        title_font = QFont("Arial", 16)
        title_font.setBold(True)
        content_font = QFont("Arial", 12)

        self.setCentralWidget(self.centralWidget)
        self.main_layout = QVBoxLayout(self.centralWidget)
        self.centralWidget.setStyleSheet("background-color: #edf2fb;")

        self.title_panel = QWidget()
        self.title_panel.setFixedHeight(70)
        title_layout = QHBoxLayout(self.title_panel)
        self.title_label = QLabel("Prometheus Backfilling")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("background-color: #90abeb; padding: 10px; border-radius: 20px")
        title_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.title_panel)
        
        # Top panel - Richard
        self.top_panel = QWidget()
        self.top_layout = QVBoxLayout(self.top_panel)
        self.top_panel.setStyleSheet("background-color: #d7e3fc; border-radius: 5px")
        self.main_layout.addWidget(self.top_panel)
        self.create_top_panel_gui()

        # Bottom panel - Rahul
        self.bottom_panel = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_panel)
        self.bottom_panel.setStyleSheet("background-color: #d7e3fc; border-radius: 5px")
        self.main_layout.addWidget(self.bottom_panel)
        self.setup_bottom_panel()

        self.set_font(self.top_panel, content_font)
        self.set_font(self.bottom_panel, content_font)

    def set_font(self, widget, font):
        for child in widget.findChildren(QWidget):
            child.setFont(font)

    def create_top_panel_gui(self):
        # Input field
        self.start_time = QDateTimeEdit(self)
        self.end_time = QDateTimeEdit(self)
        current_year = QDate.currentDate().year()
        self.start_time.setDate(QDate(current_year, 1, 1))
        self.end_time.setDate(QDate.currentDate())

        self.top_panel_label = QLabel("Status Uptime Backfilling")
        self.top_panel_label.setStyleSheet("font-weight: bold;")
        self.top_panel_label.setFixedHeight(35)
        self.top_layout.addWidget(self.top_panel_label, alignment=Qt.AlignCenter)
        self.top_panel_label.setAlignment(Qt.AlignCenter)


        self.job_name = QLineEdit(self)
        self.job_name.setStyleSheet("background-color: #7FA1C3;")
        self.metric_name = QLineEdit(self)
        self.metric_type = QComboBox(self)
        self.metric_type.addItems(["gauge", "counter", "histogram", "summary"])

        self.start_time.setStyleSheet("background-color: #C1D3FE; border-radius: 5px")
        self.end_time.setStyleSheet("background-color: #C1D3FE; border-radius: 5px")
        self.job_name.setStyleSheet("background-color: #C1D3FE; border-radius: 5px")
        self.metric_name.setStyleSheet("background-color: #C1D3FE; border-radius: 5px")
        self.metric_type.setStyleSheet("background-color: #C1D3FE; border-radius: 5px")

        self.start_time.setFixedHeight(35)
        self.end_time.setFixedHeight(35)
        self.job_name.setFixedHeight(35)
        self.metric_name.setFixedHeight(35)
        self.metric_type.setFixedHeight(35)

        # Label field
        self.top_layout.addWidget(QLabel("Start Time:"))
        self.top_layout.addWidget(self.start_time)

        self.top_layout.addWidget(QLabel("End Time:"))
        self.top_layout.addWidget(self.end_time)

        self.top_layout.addWidget(QLabel("Job Name:"))
        self.top_layout.addWidget(self.job_name)

        self.top_layout.addWidget(QLabel("Metric Name:"))
        self.top_layout.addWidget(self.metric_name)

        self.top_layout.addWidget(QLabel("Metric Type:"))
        self.top_layout.addWidget(self.metric_type)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setStyleSheet("background-color: #808af1; border-radius: 10px;")
        self.submit_button.setFixedHeight(35)
        submit_icon_path = r"C:\Users\RJ\docker\openTSDB_push_delete\backfill_status\PYQT_Backfill\arrow.png"
        self.submit_button.setIcon(QIcon(submit_icon_path))
        self.submit_button.setIconSize(QSize(24, 24))
        self.top_layout.addWidget(self.submit_button)
        self.submit_button.clicked.connect(self.status_backfill_data_generator)

    def status_backfill_data_generator(self):
        # Initialize data and link to the input field
        start_time = self.start_time.dateTime().toPyDateTime()
        end_time = self.end_time.dateTime().toPyDateTime()
        job_name = self.job_name.text()
        metric_name = self.metric_name.text()
        metric_type = self.metric_type.currentText()

        if start_time >= end_time:
            QMessageBox.critical(self, "Input Error", "Input Error: End time is greater than start time. Please enter again.")
            return
        elif not job_name or not metric_name:
            QMessageBox.critical(self, "Input Error", "Input Error: Missing field. Please enter again.")
        else:
            # Generate timestamps
            timestamps = []
            current_time = start_time
            while current_time <= end_time:
                unix_timestamp = int(current_time.timestamp())
                timestamps.append(str(unix_timestamp))
                current_time += timedelta(minutes=1)

            # Record template generation
            tsdb_layout = f"# HELP {metric_name} System uptime in seconds\n"
            tsdb_layout += f"# TYPE {metric_name} {metric_type}\n"
            tsdb_layout += f"{metric_name}{{instance=\"\",job=\"{job_name}\"}} 0"

            # Generate record
            output = ""
            uptime_status = 1           # 1 - On: 0 - Off
            for line in tsdb_layout.split("\n"):
                if line.startswith("#"):
                    output += line + "\n"
            for timestamp in timestamps:
                metric_line = tsdb_layout.split("\n")[-1]
                combined_line = re.sub(r'}\s*\d+', f'}} {uptime_status}', metric_line)
                output += f"{combined_line} {timestamp}\n"
            
            # Output result
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            output_filename = os.path.join(output_dir, f"{job_name}-backfill.txt")
            with open(output_filename, "w") as f:
                f.write(output)
                f.write("# EOF")

            QMessageBox.information(self, "Success", f"Backfill data has been generated and saved to {output_filename}")

    def setup_bottom_panel(self):
        # CSV selection layout
        self.csv_label = QLabel("Select CSV File:")
        self.csv_input = QLineEdit()
        self.csv_input.setFixedHeight(35)
        self.csv_input.setStyleSheet("background-color: #C1D3FE; border-radius: 5px")
        self.csv_button = QPushButton()
        csv_icon_path = r"C:\Users\RJ\docker\openTSDB_push_delete\backfill_status\PYQT_Backfill\browse.png"
        self.csv_button.setIcon(QIcon(csv_icon_path))
        self.csv_button.setFixedSize(35, 35)

        self.csv_button.setStyleSheet("background-color: #808af1; border-radius: 5px;")
        self.csv_button.setIconSize(QSize(24, 24))
        self.csv_button.clicked.connect(self.browse_csv)

        self.bottom_panel_label = QLabel("Request Total Backfilling")
        self.bottom_panel_label.setStyleSheet("font-weight: bold")
        self.bottom_panel_label.setFixedHeight(35)
        self.bottom_layout.addWidget(self.bottom_panel_label, alignment=Qt.AlignCenter)
        self.bottom_panel_label.setAlignment(Qt.AlignCenter)

        self.bottom_layout.addWidget(self.csv_label)
        self.csv_layout = QHBoxLayout()
        self.csv_layout.addWidget(self.csv_input)
        self.csv_layout.addWidget(self.csv_button)
        self.bottom_layout.addLayout(self.csv_layout)

        # Job Name layout
        self.job_name_label = QLabel("Job Name:")
        self.job_name_input = QLineEdit()
        self.job_name_input.setFixedHeight(35)
        self.job_name_input.setStyleSheet("background-color: #C1D3FE; border-radius: 5px")
        self.bottom_layout.addWidget(self.job_name_label)
        self.bottom_layout.addWidget(self.job_name_input)

        # Metric Name layout
        self.metric_name_label = QLabel("Metric Name:")
        self.metric_name_input = QLineEdit()
        self.metric_name_input.setFixedHeight(35)
        self.metric_name_input.setStyleSheet("background-color: #C1D3FE; border-radius: 5px")
        self.bottom_layout.addWidget(self.metric_name_label)
        self.bottom_layout.addWidget(self.metric_name_input)
    
        # Metric Type layout
        self.type_label = QLabel("Metric Type:")
        self.type_input = QComboBox()
        self.type_input.setFixedHeight(35)
        self.type_input.setStyleSheet("background-color: #C1D3FE; border-radius: 5px")
        self.type_input.addItems(["gauge", "counter", "histogram", "summary"])
        self.bottom_layout.addWidget(self.type_label)
        self.bottom_layout.addWidget(self.type_input)

        # Submit button
        self.submit_button = QPushButton("Submit")
        submit_icon_path = r"C:\Users\RJ\docker\openTSDB_push_delete\backfill_status\PYQT_Backfill\arrow.png"
        self.submit_button.setIcon(QIcon(submit_icon_path))
        self.submit_button.setIconSize(QSize(24, 24))
        self.submit_button.setFixedHeight(35)
        self.submit_button.setStyleSheet("background-color: #808af1; border-radius: 10px;")
        self.submit_button.clicked.connect(self.process_backfill)
        self.bottom_layout.addWidget(self.submit_button)

    def browse_csv(self):
        try:
            self.input_file, _ = QFileDialog.getOpenFileName(self, "Select Input CSV File", "", "CSV Files (*.csv)")
            if self.input_file:
                self.csv_input.setText(self.input_file)
            else:
                raise FileNotFoundError("No CSV file was selected.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while selecting the file: {str(e)}")
    
    def process_backfill(self):
        try:
            job_name = self.job_name_input.text()
            metric_name = self.metric_name_input.text()
            metric_type = self.type_input.currentText()
    
            if not job_name or not metric_name or not metric_type:
                raise ValueError("All fields must be filled.")
    
            if not hasattr(self, 'input_file') or not self.input_file:
                raise FileNotFoundError("No input file selected.")
            
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            output_file = os.path.join(output_dir, f"{job_name}-backfill.txt")
    
            # Generate the reference line and template
            reference_line, template = self.generate_template(job_name, metric_name, metric_type)
    
            # Process the CSV and generate the output
            epoch_timestamps = self.process_csv_to_epoch(self.input_file)

            self.process_epoch_to_metrics(epoch_timestamps, template, reference_line, output_file)
    
            QMessageBox.information(self, "Success", f"Processing complete. Output saved to {output_file}")
        
        except ValueError as ve:
            error_message = f"Input Error: {str(ve)}"
            print(error_message)
            QMessageBox.critical(self, "Input Error", error_message)
        
        except FileNotFoundError as fnf:
            error_message = f"File Error: {str(fnf)}"
            print(error_message)
            QMessageBox.critical(self, "File Error", error_message)
        
        except AttributeError as ae:
            error_message = f"Attribute Error: There might be missing UI elements. Details: {str(ae)}"
            print(error_message)
            QMessageBox.critical(self, "Attribute Error", error_message)
        
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            print(error_message)
            QMessageBox.critical(self, "Unexpected Error", error_message)
            
    def generate_template(self, job_name, metric_name, metric_type):
        try:
            if not job_name or not metric_name or not metric_type:
                raise ValueError("Job name, metric name, and metric type must not be empty")
            reference_line = f"{metric_name}{{instance=\"\",job=\"{job_name}\"}} 1"
            template = f"""# HELP {metric_name} Total number of {metric_name}\n# TYPE {metric_name} {metric_type}"""
            return reference_line, template
        except Exception as e:
            raise ValueError(f"Error generating template: {str(e)}")

    def convert_to_epoch(self, timestamp):
        try:
            dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
            return int(time.mktime(dt.timetuple()))
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format: {timestamp}. Error: {str(e)}")

    def process_csv_to_epoch(self, input_file_path):
        epoch_timestamps = []
        try:
            with open(input_file_path, 'r') as infile:
                reader = csv.reader(infile)
                next(reader)  # Skip the header
            
                for row in reader:
                    if not row:
                        continue  # Skip empty rows
                    created_at = row[0]
                    epoch = self.convert_to_epoch(created_at)
                    epoch_timestamps.append(epoch)
            
            return epoch_timestamps
        except csv.Error as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")
        except IndexError:
            raise ValueError("CSV file is not in the expected format")
        

    def process_epoch_to_metrics(self, epoch_timestamps, template, reference_line, output_file_path):
        try:
            # Convert epoch timestamps to minutes and count occurrences within the same minute
            timestamp_counts = {}
            for epoch in epoch_timestamps:
                minute = datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M')
                timestamp_counts[minute] = timestamp_counts.get(minute, 0) + 1
    
            # Generate a list of tuples with epoch and corresponding count
            epoch_with_counts = [(epoch, timestamp_counts[datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M')]) 
                                 for epoch in epoch_timestamps]
    
            # Set to track unique metric lines
            unique_lines = set()
    
            # Write the output
            with open(output_file_path, 'w') as f:
                # Write the HELP and TYPE lines
                f.write(template + "\n")
    
                # Iterate over each epoch_with_counts and write the corresponding metric line
                for epoch, count in epoch_with_counts:
                    # Replace the existing value with the count
                    new_line = re.sub(r'}\s*\d+', f'}} {count}', reference_line)
                    # Append the epoch timestamp at the end of the line
                    full_line = f"{new_line} {epoch}\n"
    
                    # Check if the line is unique before writing
                    if full_line not in unique_lines:
                        f.write(full_line)
                        unique_lines.add(full_line)
                f.write("# EOF")

        except TypeError as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            print(error_message)
            QMessageBox.critical(self, "Error", error_message)

if sys.platform.startswith('win'):
    myappid = 'neuon.prometheus.backfilling.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    taskbar_icon = r"C:\Users\RJ\docker\openTSDB_push_delete\backfill_status\PYQT_Backfill\logo.png"
    app.setWindowIcon(QIcon(taskbar_icon))
    window = main_window()
    window.show()
    sys.exit(app.exec_())
