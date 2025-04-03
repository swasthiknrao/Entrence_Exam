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
        // Try again after a very short delay
        setTimeout(enterFullscreen, 50);
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

// Force fullscreen immediately
enterFullscreen();

// Force fullscreen when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    enterFullscreen();
});

// Force fullscreen when page loads
window.addEventListener('load', function() {
    enterFullscreen();
});

// Force fullscreen when page becomes visible
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        enterFullscreen();
    }
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

// Force fullscreen periodically to ensure it stays in fullscreen mode
setInterval(function() {
    if (!document.fullscreenElement && !document.webkitFullscreenElement && !document.msFullscreenElement) {
        enterFullscreen();
    }
}, 1000); 