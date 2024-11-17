import sys
import os
import time
import logging
from dotenv import load_dotenv
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox,
                            QProgressBar)
from PyQt6.QtCore import Qt, QTimer
import openai
import requests.exceptions
from ratelimiter import RateLimiter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rate_limiter = RateLimiter(requests_per_minute=3, burst_limit=5)
        self.setWindowTitle("OpenAI API Interface")
        self.setGeometry(100, 100, 600, 400)
        
        # Initialize rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum time between requests in seconds
        
        # Load environment variables
        load_dotenv(override=True)  # Force reload of .env file
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("No API key found in .env file")
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Status label
        self.status_label = QLabel("Status: Not Connected")
        
        # API Key section
        self.api_key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        if self.api_key:
            self.api_key_input.setText(self.api_key)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        
        # Save API Key button
        self.save_key_button = QPushButton("Save API Key")
        self.save_key_button.clicked.connect(self.save_api_key)
        
        # Prompt input
        self.prompt_label = QLabel("Enter your prompt:")
        self.prompt_input = QTextEdit()
        
        # Submit button
        self.submit_button = QPushButton("Submit to OpenAI")
        self.submit_button.clicked.connect(self.submit_prompt)
        
        # Response area
        self.response_label = QLabel("Response:")
        self.response_area = QTextEdit()
        self.response_area.setReadOnly(True)
        
        # Add widgets to layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_input)
        layout.addWidget(self.progress)
        layout.addWidget(self.save_key_button)
        layout.addWidget(self.prompt_label)
        layout.addWidget(self.prompt_input)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.response_label)
        layout.addWidget(self.response_area)

    def check_rate_limit(self):
        self.rate_limiter.wait_if_needed()
    
    def save_api_key(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Error", "Please enter an API key.")
            return
        
        try:
            # Write to .env file
            with open('.env', 'w') as f:
                f.write(f'OPENAI_API_KEY={api_key}\n')
            
            self.api_key = api_key
            # Reload environment variables
            load_dotenv(override=True)
            
            QMessageBox.information(self, "Success", "API key saved successfully!")
            logger.info("API key saved successfully")
            self.status_label.setText("Status: API Key Saved")
            
            # Verify the key was saved
            if os.getenv('OPENAI_API_KEY') != api_key:
                raise Exception("API key not properly saved to environment")
                
        except Exception as e:
            logger.error(f"Error saving API key: {str(e)}")
            QMessageBox.critical(self, "Error", f"Could not save API key: {str(e)}")
    
    def handle_quota_error(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText("OpenAI API Quota Exceeded")
        msg.setInformativeText("Please check your OpenAI account billing status at:\n"
                              "https://platform.openai.com/account/billing")
        msg.setWindowTitle("Quota Error")
        msg.setDetailedText("This error occurs when:\n"
                           "1. You've exceeded your API usage limit\n"
                           "2. You haven't set up billing\n"
                           "3. Your free trial credits are exhausted\n\n"
                           "Please visit the OpenAI billing page to resolve this issue.")
        msg.exec()
    
    def submit_prompt(self):
        # Verify API key
        current_key = os.getenv('OPENAI_API_KEY')
        if not current_key:
            QMessageBox.warning(self, "Error", "No API key found. Please save your API key first.")
            return
        
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Error", "Please enter a prompt.")
            return
        
        try:
            self.status_label.setText("Status: Connecting...")
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)  # Indeterminate progress
            QApplication.processEvents()
            
            # Check rate limiting
            self.check_rate_limit()
            
            # Configure OpenAI client
            client = openai.OpenAI(api_key=current_key)
            
            # Show "Processing" message in response area
            self.response_area.setText("Processing request...")
            QApplication.processEvents()
            
            # Make API call
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Display response
            self.response_area.setText(response.choices[0].message.content)
            self.status_label.setText("Status: Request Completed")
            logger.info("Successfully received response from OpenAI")
            
        except openai.APIStatusError as e:
            if "429" in str(e):
                logger.error("Quota exceeded error")
                self.handle_quota_error()
            else:
                logger.error(f"API Status Error: {str(e)}")
                QMessageBox.critical(self, "Status Error", f"API Status Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
        finally:
            self.progress.setVisible(False)
            QApplication.processEvents()

def main():
    try:
        app = QApplication(sys.argv)
        window = OpenAIGUI()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == '__main__':
    main()