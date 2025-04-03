from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QRadioButton, QButtonGroup,
                             QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QEvent
from PyQt6.QtGui import QFont
import firebase_admin
from firebase_admin import firestore
import json

class ExamView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Initialize Firebase
        try:
            self.db = firestore.client()
        except Exception as e:
            print(f"Firebase initialization error: {str(e)}")
            self.db = None
            
        # Initialize timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 7200  # 2 hours in seconds
        self.timer.start(1000)  # Update every second
        
    def setup_ui(self):
        """Setup the exam view UI."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Add header
        header = QFrame()
        header.setObjectName("examHeader")
        header_layout = QHBoxLayout(header)
        
        # Add timer
        self.timer_label = QLabel("Time Remaining: 02:00:00")
        self.timer_label.setObjectName("timerLabel")
        header_layout.addWidget(self.timer_label)
        
        # Add submit button
        submit_btn = QPushButton("Submit Exam")
        submit_btn.setObjectName("submitBtn")
        submit_btn.clicked.connect(self.handle_submit)
        header_layout.addWidget(submit_btn)
        
        main_layout.addWidget(header)
        
        # Add scroll area for questions
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("questionScroll")
        
        # Create container for questions
        self.question_container = QWidget()
        self.question_layout = QVBoxLayout(self.question_container)
        self.question_layout.setSpacing(20)
        
        scroll.setWidget(self.question_container)
        main_layout.addWidget(scroll)
        
        # Load questions
        self.load_questions()
        
    def load_questions(self):
        """Load questions from Firebase."""
        try:
            # Get questions from Firebase
            questions_ref = self.db.collection('questions')
            questions = questions_ref.stream()
            
            # Clear existing questions
            while self.question_layout.count():
                item = self.question_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Add questions to layout
            for question in questions:
                data = question.to_dict()
                self.add_question(data)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load questions: {str(e)}")
            
    def add_question(self, data):
        """Add a question to the layout."""
        # Create question frame
        question_frame = QFrame()
        question_frame.setObjectName("questionFrame")
        question_layout = QVBoxLayout(question_frame)
        
        # Add question text
        question_text = QLabel(data.get('question', ''))
        question_text.setObjectName("questionText")
        question_text.setWordWrap(True)
        question_layout.addWidget(question_text)
        
        # Create button group for options
        button_group = QButtonGroup(self)
        
        # Add options
        options = ['A', 'B', 'C', 'D']
        for option in options:
            option_text = data.get(f'option_{option}', '')
            if option_text:
                radio = QRadioButton(option_text)
                radio.setObjectName(f"option_{option}")
                radio.setProperty("option", option)
                button_group.addButton(radio)
                question_layout.addWidget(radio)
        
        # Store question data
        question_frame.setProperty("question_id", data.get('id'))
        question_frame.setProperty("correct_answer", data.get('correct_answer'))
        
        self.question_layout.addWidget(question_frame)
        
    def update_timer(self):
        """Update the timer display."""
        if self.remaining_time > 0:
            hours = self.remaining_time // 3600
            minutes = (self.remaining_time % 3600) // 60
            seconds = self.remaining_time % 60
            
            self.timer_label.setText(f"Time Remaining: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.remaining_time -= 1
        else:
            self.timer.stop()
            self.handle_submit()
            
    def handle_submit(self):
        """Handle exam submission."""
        try:
            # Collect answers
            answers = {}
            for i in range(self.question_layout.count()):
                question_frame = self.question_layout.itemAt(i).widget()
                question_id = question_frame.property("question_id")
                
                # Find selected option
                for radio in question_frame.findChildren(QRadioButton):
                    if radio.isChecked():
                        answers[question_id] = radio.property("option")
                        break
            
            # Store answers in Firebase
            if hasattr(self.parent(), 'session') and 'student_id' in self.parent().session:
                student_id = self.parent().session['student_id']
                submission_ref = self.db.collection('submissions').document(student_id)
                submission_ref.set({
                    'answers': answers,
                    'submission_time': firestore.SERVER_TIMESTAMP,
                    'exam_completed': True
                })
                
                # Show success message
                QMessageBox.information(self, "Success", "Exam submitted successfully!")
                
                # Make window fullscreen and prevent minimizing
                if hasattr(self.parent(), 'window'):
                    window = self.parent().window()
                    window.setWindowState(Qt.WindowState.WindowFullScreen)
                    window.setWindowFlags(
                        Qt.WindowType.Window |
                        Qt.WindowType.WindowStaysOnTopHint |
                        Qt.WindowType.CustomizeWindowHint |
                        Qt.WindowType.WindowTitleHint |
                        Qt.WindowType.WindowCloseButtonHint
                    )
                    window.show()
                    
                    # Disable all keyboard shortcuts
                    window.installEventFilter(self)
                
                # Switch to results view or login view
                if hasattr(self.parent(), 'show_login'):
                    self.parent().show_login()
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to submit exam: {str(e)}")
            
    def eventFilter(self, obj, event):
        """Filter events to block unwanted keyboard shortcuts."""
        if event.type() == QEvent.Type.KeyPress:
            # Block Alt+Tab, Alt+F4, Windows key, etc.
            if event.modifiers() & (Qt.KeyboardModifier.AltModifier | Qt.KeyboardModifier.MetaModifier):
                return True
                
            # Block PrintScreen
            if event.key() == Qt.Key.Key_Print:
                return True
                
            # Block other system keys
            if event.key() in [
                Qt.Key.Key_Launch0,
                Qt.Key.Key_Launch1,
                Qt.Key.Key_LaunchMail,
                Qt.Key.Key_LaunchMedia,
                Qt.Key.Key_Calculator
            ]:
                return True
        
        return super().eventFilter(obj, event)
            
    def adjust_responsive_layout(self):
        """Adjust layout based on screen size."""
        # Get screen size
        screen = self.screen()
        if screen:
            size = screen.size()
            width = size.width()
            
            # Adjust for mobile screens
            if width < 768:
                # Adjust margins
                self.layout().setContentsMargins(10, 10, 10, 10)
                
                # Adjust font sizes
                self.adjust_fonts()
            else:
                # Reset margins
                self.layout().setContentsMargins(20, 20, 20, 20)
                
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
                
            # Adjust radio buttons
            for radio in self.findChildren(QRadioButton):
                font = radio.font()
                font.setPointSize(base_size)
                radio.setFont(font)
                
            # Adjust buttons
            for button in self.findChildren(QPushButton):
                font = button.font()
                font.setPointSize(base_size)
                button.setFont(font) 