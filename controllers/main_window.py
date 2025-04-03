from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import Qt, QTimer, QEvent

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_security()
        
    def setup_ui(self):
        """Setup the main window UI."""
        # Set window properties
        self.setWindowTitle("Dr.B.B. Hegde College Examination System")
        self.setMinimumSize(1200, 800)
        
        # Create stacked widget for views
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create views
        self.login_view = LoginView(self)
        self.exam_view = ExamView(self)
        self.admin_view = AdminView(self)
        
        # Add views to stacked widget
        self.stacked_widget.addWidget(self.login_view)
        self.stacked_widget.addWidget(self.exam_view)
        self.stacked_widget.addWidget(self.admin_view)
        
        # Show login view by default
        self.show_login()
        
        # Setup resize timer for responsive layout
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.handle_resize_timeout)
        
    def setup_security(self):
        """Setup security features to prevent cheating."""
        # Set window flags to prevent minimize/maximize
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Install event filter for keyboard shortcuts
        self.installEventFilter(self)
        
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
        
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        # Start resize timer
        self.resize_timer.start(150)
        
    def handle_resize_timeout(self):
        """Handle resize timer timeout."""
        # Update responsive layout for current view
        current_view = self.stacked_widget.currentWidget()
        if hasattr(current_view, 'adjust_responsive_layout'):
            current_view.adjust_responsive_layout()
            
    def show_login(self):
        """Switch to login view."""
        self.stacked_widget.setCurrentWidget(self.login_view)
        # Reset window state for login view
        self.setWindowState(Qt.WindowState.WindowMaximized)
        
    def show_exam(self):
        """Switch to exam view."""
        self.stacked_widget.setCurrentWidget(self.exam_view)
        # Set fullscreen for exam view
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
    def show_admin(self):
        """Switch to admin view."""
        self.stacked_widget.setCurrentWidget(self.admin_view)
        # Reset window state for admin view
        self.setWindowState(Qt.WindowState.WindowMaximized)
        
    def closeEvent(self, event):
        """Handle window close event."""
        # Block window close attempt
        event.ignore() 