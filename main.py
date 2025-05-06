import sys
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QCheckBox, QTextEdit, QFileDialog, 
                             QLabel, QGroupBox, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont
from threading import Thread
import ctypes
from gmail_search import run_search

# Configure logging for debugging
logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class LogSignal(QObject):
    log_message = pyqtSignal(str)

class GmailSearchGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gmail Search Tool")
        self.setGeometry(100, 100, 900, 700)

        # Set window icon
        icon_path = self.get_icon_path('ProgmeleonTool.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            logging.debug(f"Window icon set to: {icon_path}")
        else:
            logging.error(f"Icon file not found: {icon_path}")

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                font-size: 14px;
                background-color: #fff;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 5px;
                background-color: #007bff;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #b0c4de;
                color: #666;
            }
            QCheckBox {
                font-size: 14px;
                color: #333;
            }
            QTextEdit {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                background-color: #fff;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 5px;
            }
            QGroupBox {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                margin-top: 10px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }
            QProgressBar {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                text-align: center;
                font-size: 12px;
                background-color: #e9ecef;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 3px;
            }
        """)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)

        # Title label
        title_label = QLabel("Gmail Search Tool")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)

        # Status label
        self.status_label = QLabel("Status: Idle")
        self.status_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.status_label)

        # Credentials group
        cred_group = QGroupBox("Credentials")
        cred_layout = QHBoxLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email or select emails.txt")
        self.email_input.setToolTip("Enter a single email or select a file with email:password pairs")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.email_input.setToolTip("Enter the password for the email")
        self.browse_button = QPushButton("Browse")
        self.browse_button.setIcon(QIcon.fromTheme("folder-open"))
        self.browse_button.clicked.connect(self.browse_credentials)
        self.browse_button.setToolTip("Select a text file containing email:password pairs")
        cred_layout.addWidget(QLabel("Email:"))
        cred_layout.addWidget(self.email_input)
        cred_layout.addWidget(QLabel("Password:"))
        cred_layout.addWidget(self.password_input)
        cred_layout.addWidget(self.browse_button)
        cred_group.setLayout(cred_layout)
        self.layout.addWidget(cred_group)

        # Options group
        options_group = QGroupBox("Options")
        options_layout = QHBoxLayout()
        self.headless_checkbox = QCheckBox("Run in Headless Mode")
        self.headless_checkbox.setChecked(True)
        self.headless_checkbox.setToolTip("Run the browser in headless mode (no visible window)")
        options_layout.addWidget(self.headless_checkbox)
        options_layout.addStretch()
        options_group.setLayout(options_layout)
        self.layout.addWidget(options_group)

        # Keywords group
        keyword_group = QGroupBox("Keywords")
        keyword_layout = QHBoxLayout()
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter keywords (comma-separated, e.g., google,invoice)")
        self.keyword_input.setToolTip("Enter search keywords, separated by commas")
        keyword_layout.addWidget(QLabel("Keywords:"))
        keyword_layout.addWidget(self.keyword_input)
        keyword_group.setLayout(keyword_layout)
        self.layout.addWidget(keyword_group)

        # Output directory group
        output_group = QGroupBox("Output Directory")
        output_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("Select output directory")
        self.output_dir_input.setToolTip("Select a directory to save results.txt")
        self.output_dir_button = QPushButton("Browse")
        self.output_dir_button.setIcon(QIcon.fromTheme("folder-open"))
        self.output_dir_button.clicked.connect(self.browse_output_dir)
        self.output_dir_button.setToolTip("Select a directory for saving results")
        output_layout.addWidget(QLabel("Output Directory:"))
        output_layout.addWidget(self.output_dir_input)
        output_layout.addWidget(self.output_dir_button)
        output_group.setLayout(output_layout)
        self.layout.addWidget(output_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setToolTip("Progress of credential processing")
        self.layout.addWidget(self.progress_bar)

        # Control buttons
        button_group = QGroupBox("Controls")
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Search")
        self.start_button.setIcon(QIcon.fromTheme("media-playback-start"))
        self.start_button.clicked.connect(self.start_search)
        self.start_button.setToolTip("Start the Gmail search process")
        self.stop_button = QPushButton("Stop Search")
        self.stop_button.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.stop_button.clicked.connect(self.stop_search)
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip("Attempt to stop the search process")
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        button_group.setLayout(button_layout)
        self.layout.addWidget(button_group)

        # Log output
        log_group = QGroupBox("Log Output")
        log_layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setToolTip("Logs of the search process")
        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)
        self.layout.addWidget(log_group)

        # Thread control
        self.search_thread = None
        self.is_running = False
        self.total_credentials = 0

        # Log signal
        self.log_signal = LogSignal()
        self.log_signal.log_message.connect(self._append_log)

    def get_icon_path(self, icon_name):
        """Get the path to the icon file, handling PyInstaller bundled environment."""
        if hasattr(sys, '_MEIPASS'):
            path = os.path.join(sys._MEIPASS, icon_name)
        else:
            path = os.path.join(os.path.dirname(__file__), icon_name)
        logging.debug(f"Resolved icon path: {path}")
        return path

    def _append_log(self, message):
        """Append log message to QTextEdit safely."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")

    def log_to_output(self, message):
        """Emit log message via signal for thread-safe GUI updates."""
        self.log_signal.log_message.emit(message)

    def browse_credentials(self):
        """Open file dialog to select emails.txt."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select emails.txt", "", "Text Files (*.txt)")
        if file_path:
            self.email_input.setText(file_path)
            self.password_input.clear()

    def browse_output_dir(self):
        """Open directory dialog to select output directory."""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir_input.setText(dir_path)

    def start_search(self):
        """Start the search process in a separate thread."""
        if self.is_running:
            self.log_to_output("[INFO] Search is already running")
            return

        self.is_running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.email_input.setEnabled(False)
        self.password_input.setEnabled(False)
        self.keyword_input.setEnabled(False)
        self.output_dir_input.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.output_dir_button.setEnabled(False)
        self.status_label.setText("Status: Running...")
        self.log_output.clear()
        self.progress_bar.setValue(0)

        # Get credentials
        credentials = []
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if email and os.path.isfile(email):
            try:
                with open(email, "r") as f:
                    credentials = [line.strip().split(":", 1) for line in f if ":" in line]
                    valid_credentials = [(e, p) for e, p in credentials if e.strip() and p.strip()]
                    if not valid_credentials:
                        self.log_to_output("[ERROR] No valid credentials found in emails.txt")
                        self.reset_ui()
                        return
                    credentials = valid_credentials
                self.log_to_output(f"[INFO] Loaded {len(credentials)} valid credentials from {email}")
            except Exception as e:
                self.log_to_output(f"[ERROR] Failed to load credentials: {e}")
                self.reset_ui()
                return
        elif email and password:
            credentials = [(email, password)]
        else:
            self.log_to_output("[ERROR] Please provide valid credentials or select emails.txt")
            self.reset_ui()
            return

        # Store total credentials for progress
        self.total_credentials = len(credentials)
        self.progress_bar.setMaximum(self.total_credentials)

        # Get keywords
        keywords = [k.strip() for k in self.keyword_input.text().split(",") if k.strip()]
        if not keywords:
            self.log_to_output("[ERROR] Please provide at least one keyword")
            self.reset_ui()
            return

        # Get output directory
        output_dir = self.output_dir_input.text().strip()
        if not output_dir or not os.path.isdir(output_dir):
            self.log_to_output("[ERROR] Please select a valid output directory")
            self.reset_ui()
            return

        # Get headless mode
        headless = self.headless_checkbox.isChecked()

        # Run search in a separate thread
        def search_thread():
            processed = 0
            try:
                for email, password in credentials:
                    if not self.is_running:
                        break
                    run_search([(email, password)], keywords, output_dir, headless, self.log_to_output)
                    processed += 1
                    self.progress_bar.setValue(processed)
                self.log_to_output("[INFO] Search completed successfully")
                self.status_label.setText("Status: Completed")
            except Exception as e:
                self.log_to_output(f"[ERROR] Search failed: {e}")
                self.status_label.setText("Status: Failed")
            finally:
                self.reset_ui()
                self.search_thread = None

        self.search_thread = Thread(target=search_thread)
        self.search_thread.start()

    def stop_search(self):
        """Attempt to stop the search process."""
        if not self.is_running:
            self.log_to_output("[INFO] No search is running")
            return

        self.log_to_output("[INFO] Stopping search (note: some operations may complete)")
        self.is_running = False
        self.status_label.setText("Status: Stopping...")

    def reset_ui(self):
        """Reset the UI after search completes or fails."""
        self.is_running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.email_input.setEnabled(True)
        self.password_input.setEnabled(True)
        self.keyword_input.setEnabled(True)
        self.output_dir_input.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.output_dir_button.setEnabled(True)
        if not self.status_label.text().startswith("Status: Completed") and not self.status_label.text().startswith("Status: Failed"):
            self.status_label.setText("Status: Idle")
        self.progress_bar.setValue(0)

    def closeEvent(self, event):
        """Handle window close to ensure clean shutdown."""
        if self.is_running:
            self.stop_search()
            if self.search_thread:
                self.search_thread.join(timeout=2.0)
        event.accept()

if __name__ == "__main__":
    # Set Windows taskbar icon explicitly
    if sys.platform == "win32":
        app_id = 'GmailSearchGUI'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        logging.debug(f"Set Windows AppUserModelID: {app_id}")

    app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(__file__), 'ProgmeleonTool.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        logging.debug(f"Application icon set to: {icon_path}")
    else:
        logging.error(f"Application icon file not found: {icon_path}")
    
    window = GmailSearchGUI()
    window.show()
    sys.exit(app.exec_())