# Entrance Exam System

A comprehensive web-based entrance examination system built with Flask and Firebase, featuring secure exam delivery, automated scoring, and administrative dashboard.

## Features

- 🔐 Secure login system for students
- 📝 Dynamic exam generation from Excel sheets
- ⏱️ Timed examination system
- 🔒 Anti-cheating measures and full-screen mode
- 📊 Automated scoring and result generation
- 👨‍💼 Administrative dashboard for result analysis
- 📱 Responsive design for multiple devices

## Project Structure

```
.
├── app.py                  # Main Flask application
├── create_excel.py         # Excel file generation utility
├── requirements.txt        # Python dependencies
├── controllers/           
│   └── main_window.py     # Main window controller
├── server/                 # Server-side components
│   ├── requirements.txt    # Server-specific dependencies
│   └── src/
│       ├── app.py         # Server application
│       └── templates/     # Server-side templates
├── static/                # Static assets
│   ├── clglogo.png       # College logo
│   ├── exam-security.js  # Exam security features
│   ├── fullscreen.js     # Full-screen functionality
│   ├── init.js           # Initialization script
│   ├── login-security.js # Login security
│   └── security.js       # General security measures
├── styles/
│   └── stylesheet.qss    # QSS styles
├── templates/            # HTML templates
│   ├── index.html       # Main dashboard template
│   └── login.html       # Login page template
└── views/               # View components
    ├── exam_view.py     # Exam interface
    └── login_view.py    # Login interface
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/swasthiknrao/Entrence_Exam.git
   cd Entrence_Exam
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r server/requirements.txt
   ```

3. Configure Firebase:
   - Create a Firebase project
   - Download your `serviceAccountKey.json` from Firebase Console
   - Place it in the root directory

4. Set up the environment:
   - Create a `.env` file in the root directory
   - Add necessary environment variables

5. Run the application:
   ```bash
   python app.py
   ```

## Excel Configuration

The system uses Excel files for question management:
- Questions are organized by sections
- Each section can have different numbers of questions
- Excel file should follow the prescribed format (see `create_excel.py`)

## Security Features

- Full-screen examination mode
- Anti-tab switching measures
- Copy-paste prevention
- Session management
- Secure authentication

## Admin Dashboard

Access the admin dashboard at `/admin` to:
- View all student results
- Analyze performance metrics
- Export results
- Monitor exam progress

## Development and Contribution

Nithish Achar – nithishachar29@gmail.com
LinkedIn:https://www.linkedin.com/in/nithish-acharya-aa7283290

Raveendra Prabhu -raveendra5656@gmail.com

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please
- Email: nraoswasthik2004@gmail.com
- LinkedIn: www.linkedin.com/in/swasthik-n-rao
-  or open an issue in the GitHub repository. 
