// Advanced security measures to prevent developer tools access
(function() {
    // Store the original console methods
    const originalConsole = { ...console };
    
    // Override console methods
    Object.keys(console).forEach(key => {
        console[key] = () => {};
    });

    // Detect DevTools opening through console
    const devtools = {
        isOpen: false,
        orientation: undefined
    };

    // Detect through console.log timing
    setInterval(() => {
        const widthThreshold = window.outerWidth - window.innerWidth > 160;
        const heightThreshold = window.outerHeight - window.innerHeight > 160;
        
        if (widthThreshold || heightThreshold) {
            document.body.innerHTML = '<h1 style="text-align:center;margin-top:40px;">Developer Tools are not allowed!</h1>';
            document.body.style.background = '#fff';
        }
    }, 1000);

    // Detect F12 and common dev tool shortcuts
    document.addEventListener('keydown', function(event) {
        // Prevent F12
        if (event.keyCode === 123) {
            event.preventDefault();
            return false;
        }

        // Prevent Ctrl+Shift+I/J/C/K
        if (event.ctrlKey && event.shiftKey && (
            event.keyCode === 73 || // I
            event.keyCode === 74 || // J
            event.keyCode === 67 || // C
            event.keyCode === 75    // K
        )) {
            event.preventDefault();
            return false;
        }

        // Prevent Ctrl+Shift+C
        if (event.ctrlKey && event.shiftKey && event.code === 'KeyC') {
            event.preventDefault();
            return false;
        }
    });

    // Prevent right-click
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        return false;
    });

    // Prevent text selection
    document.addEventListener('selectstart', function(e) {
        e.preventDefault();
        return false;
    });

    // Prevent copy/paste
    document.addEventListener('copy', function(e) {
        e.preventDefault();
        return false;
    });

    document.addEventListener('paste', function(e) {
        e.preventDefault();
        return false;
    });

    // Detect through debugger
    function detectDevTools() {
        if (window.Firebug && window.Firebug.chrome && window.Firebug.chrome.isInitialized) {
            document.body.innerHTML = '<h1 style="text-align:center;margin-top:40px;">Developer Tools are not allowed!</h1>';
            return true;
        }
        
        const element = new Image();
        Object.defineProperty(element, 'id', {
            get: function() {
                document.body.innerHTML = '<h1 style="text-align:center;margin-top:40px;">Developer Tools are not allowed!</h1>';
                return true;
            }
        });
        
        console.debug(element);
        return false;
    }

    // Run detection periodically
    setInterval(detectDevTools, 1000);

    // Additional protection against view source
    document.onkeypress = function(event) {
        if (event.ctrlKey && (event.keyCode === 10 || event.keyCode === 13)) {
            event.preventDefault();
            return false;
        }
    };
})(); 