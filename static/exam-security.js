class ExamSecurity {
    constructor() {
        this.warningCount = 0;
        this.maxWarnings = 3;
        this.isExamActive = false;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Fullscreen change detection
        document.addEventListener('fullscreenchange', () => this.handleFullscreenChange());
        document.addEventListener('webkitfullscreenchange', () => this.handleFullscreenChange());
        document.addEventListener('mozfullscreenchange', () => this.handleFullscreenChange());
        document.addEventListener('MSFullscreenChange', () => this.handleFullscreenChange());

        // Tab visibility detection
        document.addEventListener('visibilitychange', () => this.handleVisibilityChange());

        // Window focus detection
        window.addEventListener('blur', () => this.handleWindowBlur());
        window.addEventListener('focus', () => this.handleWindowFocus());

        // Prevent keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeydown(e));

        // Prevent right-click context menu
        document.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            return false;
        });

        // Prevent copy/paste
        document.addEventListener('copy', (e) => e.preventDefault());
        document.addEventListener('paste', (e) => e.preventDefault());
        document.addEventListener('cut', (e) => e.preventDefault());

        // Prevent drag and drop
        document.addEventListener('dragstart', (e) => e.preventDefault());
        document.addEventListener('drop', (e) => e.preventDefault());
    }

    startExam() {
        this.isExamActive = true;
        this.warningCount = 0;
        this.enterFullscreen();
        this.showNotification('Exam started. Please do not exit fullscreen mode.', 'info');
    }

    endExam() {
        this.isExamActive = false;
        this.exitFullscreen();
    }

    enterFullscreen() {
        const element = document.documentElement;
        if (element.requestFullscreen) {
            element.requestFullscreen();
        } else if (element.webkitRequestFullscreen) {
            element.webkitRequestFullscreen();
        } else if (element.mozRequestFullScreen) {
            element.mozRequestFullScreen();
        } else if (element.msRequestFullscreen) {
            element.msRequestFullscreen();
        }
    }

    exitFullscreen() {
        if (!this.isExamActive) {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
        }
    }

    handleFullscreenChange() {
        if (this.isExamActive && !document.fullscreenElement && 
            !document.webkitFullscreenElement && 
            !document.mozFullScreenElement && 
            !document.msFullscreenElement) {
            this.handleSecurityViolation('Fullscreen mode was exited');
            this.enterFullscreen();
        }
    }

    handleVisibilityChange() {
        if (this.isExamActive && document.hidden) {
            this.handleSecurityViolation('Tab change detected');
        }
    }

    handleWindowBlur() {
        if (this.isExamActive) {
            this.handleSecurityViolation('Window focus lost');
        }
    }

    handleWindowFocus() {
        if (this.isExamActive) {
            this.enterFullscreen();
        }
    }

    handleKeydown(e) {
        if (this.isExamActive) {
            // Allow specific keys for exam navigation and form submission
            const allowedKeys = ['Tab', 'Enter', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
            if (!allowedKeys.includes(e.key)) {
                if ((e.ctrlKey || e.metaKey || e.altKey) && e.key !== 'Control' && e.key !== 'Meta' && e.key !== 'Alt') {
                    e.preventDefault();
                    this.handleSecurityViolation('Keyboard shortcut detected');
                    return false;
                }
            }
        }
    }

    handleSecurityViolation(message) {
        this.warningCount++;
        this.showNotification(`Warning ${this.warningCount}/${this.maxWarnings}: ${message}`, 'warning');

        if (this.warningCount >= this.maxWarnings) {
            this.submitExamAutomatically();
        }
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `exam-notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background: ${type === 'warning' ? '#ff4444' : '#4CAF50'};
            color: white;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 10000;
            animation: slideIn 0.5s ease-out;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.5s ease-in';
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }

    submitExamAutomatically() {
        this.showNotification('Maximum warnings reached. Exam will be submitted.', 'warning');
        // Trigger exam submission
        const submitButton = document.querySelector('#submit-exam-btn');
        if (submitButton) {
            submitButton.click();
        }
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    .exam-notification {
        font-family: 'Poppins', sans-serif;
        font-size: 14px;
        line-height: 1.4;
    }
    @media (max-width: 768px) {
        .exam-notification {
            width: 90%;
            left: 5%;
            right: 5%;
            text-align: center;
        }
    }
`;
document.head.appendChild(style);

// Initialize security when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.examSecurity = new ExamSecurity();
}); 