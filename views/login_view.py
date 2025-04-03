from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QLineEdit, QDateEdit, 
                             QTextEdit, QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

class LoginView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Initialize Firebase
        try:
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            print(f"Firebase initialization error: {str(e)}")
            self.db = None
            
        # Initialize session
        self.session = {}
        
    def setup_ui(self):
        """Setup the login view UI."""
        # Create main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create banner side
        banner_side = QFrame()
        banner_side.setObjectName("bannerSide")
        banner_layout = QVBoxLayout(banner_side)
        
        # Add college logo and info
        college_header = QFrame()
        college_header.setObjectName("collegeHeader")
        header_layout = QHBoxLayout(college_header)
        
        logo_label = QLabel()
        logo_label.setPixmap(QIcon("static/clglogo.png").pixmap(100, 100))
        header_layout.addWidget(logo_label)
        
        college_info = QVBoxLayout()
        college_name = QLabel("Dr.B.B. Hegde College")
        college_name.setObjectName("collegeName")
        society_name = QLabel("Society Name")
        society_name.setObjectName("societyName")
        college_info.addWidget(college_name)
        college_info.addWidget(society_name)
        header_layout.addLayout(college_info)
        
        banner_layout.addWidget(college_header)
        
        # Add exam info
        exam_info = QFrame()
        exam_info.setObjectName("examInfo")
        info_layout = QVBoxLayout(exam_info)
        
        duration_label = QLabel("Duration: 2 hours")
        duration_label.setObjectName("durationLabel")
        pattern_label = QLabel("Question Pattern: Multiple Choice")
        pattern_label.setObjectName("patternLabel")
        
        info_layout.addWidget(duration_label)
        info_layout.addWidget(pattern_label)
        banner_layout.addWidget(exam_info)
        
        # Add credentials
        credentials = QFrame()
        credentials.setObjectName("credentials")
        cred_layout = QVBoxLayout(credentials)
        
        cred_label = QLabel("Credentials")
        cred_label.setObjectName("credLabel")
        cred_layout.addWidget(cred_label)
        
        banner_layout.addWidget(credentials)
        
        # Create login side
        login_side = QFrame()
        login_side.setObjectName("loginSide")
        login_layout = QVBoxLayout(login_side)
        
        # Add form
        form = QFrame()
        form.setObjectName("loginForm")
        form_layout = QVBoxLayout(form)
        
        # Add form fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.pu_college_input = QLineEdit()
        self.pu_college_input.setPlaceholderText("PU College Name")
        self.stream_input = QLineEdit()
        self.stream_input.setPlaceholderText("Stream")
        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("Mobile Number")
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Home Address")
        
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.dob_input)
        form_layout.addWidget(self.pu_college_input)
        form_layout.addWidget(self.stream_input)
        form_layout.addWidget(self.mobile_input)
        form_layout.addWidget(self.address_input)
        
        # Add submit button
        submit_btn = QPushButton("Begin Examination")
        submit_btn.setObjectName("submitBtn")
        submit_btn.clicked.connect(self.handle_submit)
        form_layout.addWidget(submit_btn)
        
        login_layout.addWidget(form)
        
        # Add important notices
        notices = QFrame()
        notices.setObjectName("notices")
        notices_layout = QVBoxLayout(notices)
        
        notice_label = QLabel("Important Notices")
        notice_label.setObjectName("noticeLabel")
        notices_layout.addWidget(notice_label)
        
        login_layout.addWidget(notices)
        
        # Add views to main layout
        main_layout.addWidget(banner_side)
        main_layout.addWidget(login_side)
        
        # Set layout proportions
        main_layout.setStretch(0, 1)  # Banner side
        main_layout.setStretch(1, 1)  # Login side
        
    def handle_submit(self):
        """Handle form submission."""
        try:
            # Get form data
            name = self.name_input.text().strip()
            dob = self.dob_input.date().toString("yyyy-MM-dd")
            pu_college = self.pu_college_input.text().strip()
            stream = self.stream_input.text().strip()
            mobile = self.mobile_input.text().strip()
            address = self.address_input.toPlainText().strip()
            
            # Validate required fields
            if not all([name, dob, pu_college, stream, mobile, address]):
                QMessageBox.warning(self, "Validation Error", "Please fill in all fields")
                return
                
            # Validate mobile number
            if not mobile.isdigit() or len(mobile) != 10:
                QMessageBox.warning(self, "Validation Error", "Please enter a valid 10-digit mobile number")
                return
            
            # Create student data
            student_data = {
                'name': name,
                'dob': dob,
                'puCollege': pu_college,
                'stream': stream,
                'mobile': mobile,
                'address': address,
                'exam_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Store data in Firebase
            try:
                student_ref = self.db.collection('students').document()
                student_id = student_ref.id
                student_ref.set(student_data)
                
                # Store student_id in session
                self.session['student_id'] = student_id
                
                # Switch to exam view
                if hasattr(self.parent(), 'show_exam'):
                    self.parent().show_exam()
                else:
                    QMessageBox.critical(self, "Error", "Failed to navigate to exam view")
                    
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to save student data: {str(e)}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            
    def adjust_responsive_layout(self):
        """Adjust layout based on screen size."""
        # Get screen size
        screen = self.screen()
        if screen:
            size = screen.size()
            width = size.width()
            height = size.height()
            
            # Adjust for mobile screens
            if width < 768:
                # Stack banner and login vertically
                layout = self.layout()
                if layout:
                    layout.setDirection(QVBoxLayout.Direction.TopToBottom)
                    
                # Adjust form field sizes
                for widget in self.findChildren(QLineEdit):
                    widget.setFixedWidth(int(width * 0.8))
                for widget in self.findChildren(QTextEdit):
                    widget.setFixedWidth(int(width * 0.8))
                    
                # Adjust font sizes
                self.adjust_fonts()
            else:
                # Side by side layout
                layout = self.layout()
                if layout:
                    layout.setDirection(QHBoxLayout.Direction.LeftToRight)
                    
    def adjust_fonts(self):
        """Adjust font sizes based on screen size."""
        screen = self.screen()
        if screen:
            width = screen.size().width()
            
            # Base font size
            base_size = 12 if width < 768 else 14
            
            # Adjust labels
            for label in self.findChildren(QLabel):
                font = label.font()
                font.setPointSize(base_size)
                label.setFont(font)
                
            # Adjust input fields
            for input_field in self.findChildren((QLineEdit, QTextEdit)):
                font = input_field.font()
                font.setPointSize(base_size)
                input_field.setFont(font)
                
            # Adjust button
            for button in self.findChildren(QPushButton):
                font = button.font()
                font.setPointSize(base_size)
                button.setFont(font) 