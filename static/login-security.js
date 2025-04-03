// Basic functionality without security restrictions
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any necessary functionality
});

// Disable right-click
document.addEventListener('contextmenu', function(event) {
    event.preventDefault();
    return false;
});

// Disable keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Block Control key combinations
    if (event.ctrlKey || event.metaKey || event.altKey) {
        event.preventDefault();
        return false;
    }
    
    // Block specific keys
    const blockedKeys = [
        'Escape', 'Insert', 'PrintScreen', 'Alt', 'AltGraph',
        'Calculator', 'LaunchApp1', 'LaunchApp2', 'LaunchMail',
        'LaunchMediaPlayer', 'LaunchMusicPlayer', 'LaunchScreenSaver',
        'LaunchSpreadsheet', 'LaunchWebBrowser', 'LaunchWebCam',
        'LaunchWordProcessor', 'LaunchApplication1', 'LaunchApplication2',
        'Meta', 'Win', 'Windows', 'Command', 'CommandOrControl'
    ];
    
    // Allow text input characters (letters, numbers, spaces, punctuation)
    if (event.key.length === 1 ||
        event.key === 'Delete' || event.key === 'ArrowLeft' || event.key === 'ArrowRight' ||
        event.key === 'Tab' || event.key === 'Enter') {
        return true;
    }
    
    if (blockedKeys.includes(event.key)) {
        event.preventDefault();
        return false;
    }
});

// Disable text selection
document.addEventListener('selectstart', function(event) {
    event.preventDefault();
    return false;
});

// Disable drag and drop
document.addEventListener('dragstart', function(event) {
    event.preventDefault();
    return false;
});

// Enter fullscreen when page loads
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