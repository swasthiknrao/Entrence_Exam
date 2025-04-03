// Function to enter fullscreen
function enterFullscreen() {
    const element = document.documentElement;
    try {
        if (element.requestFullscreen) {
            element.requestFullscreen();
        } else if (element.webkitRequestFullscreen) {
            element.webkitRequestFullscreen();
        } else if (element.msRequestFullscreen) {
            element.msRequestFullscreen();
        }
    } catch (err) {
        console.log('Error entering fullscreen:', err);
        // Try again after a short delay
        setTimeout(enterFullscreen, 100);
    }
}

// Function to exit fullscreen
function exitFullscreen() {
    if (document.exitFullscreen) {
        document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
    }
}

// Enter fullscreen immediately when script loads
enterFullscreen();

// Also enter fullscreen when page loads
window.addEventListener('load', function() {
    enterFullscreen();
});

// Handle fullscreen change events
document.addEventListener('fullscreenchange', function() {
    if (!document.fullscreenElement) {
        enterFullscreen();
    }
});

document.addEventListener('webkitfullscreenchange', function() {
    if (!document.webkitFullscreenElement) {
        enterFullscreen();
    }
});

document.addEventListener('msfullscreenchange', function() {
    if (!document.msFullscreenElement) {
        enterFullscreen();
    }
});

// Additional event listeners to ensure fullscreen persists
window.addEventListener('focus', function() {
    if (!document.fullscreenElement && !document.webkitFullscreenElement && !document.msFullscreenElement) {
        enterFullscreen();
    }
});

// Prevent exiting fullscreen with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        event.preventDefault();
        enterFullscreen();
    }
}); 