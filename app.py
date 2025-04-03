from flask import Flask, render_template, jsonify, session, redirect, url_for, send_from_directory, request
import pandas as pd
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session

# Initialize Firebase
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Add route to serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    try:
        print("\n=== Starting admin_dashboard route ===")
        
        # Get all student records
        students_ref = db.collection('students')
        students = students_ref.get()
        print(f"Connected to Firebase successfully")
        
        # Get total questions from Excel
        excel_data = read_excel_data()
        total_questions_from_excel = excel_data['total_questions']
        print(f"Total questions from Excel: {total_questions_from_excel}")
        
        students_data = []
        total_students = 0
        highest_score = 0
        total_score_sum = 0
        
        print("\n=== Processing all students ===")
        for student in students:
            data = student.to_dict()
            student_id = student.id
            print(f"\n--- Student ID: {student_id} ---")
            
            # Get scores and section data from Firebase
            scores = data.get('scores', {})
            
            section_scores = {}
            total_score = 0
            question_details = {}
            section_totals = {}
            
            # Process each section's scores and questions
            for section, section_data in scores.items():
                if isinstance(section_data, dict):
                    # Get section total questions and marks
                    section_total = section_data.get('total_questions', 0)
                    section_score = section_data.get('marks', 0)
                    section_totals[section] = section_total
                    
                    if isinstance(section_score, (int, float)):
                        # Calculate normalized section score (out of 100)
                        normalized_section_score = round((section_score / section_total * 100) if section_total > 0 else 0)
                        section_scores[section] = {
                            'raw_score': section_score,
                            'total': section_total,
                            'normalized_score': normalized_section_score
                        }
                        total_score += section_score
                        
                        # Process question details
                        if 'debug' in section_data:
                            questions = []
                            for q in section_data['debug']:
                                question_info = {
                                    'question': q.get('question', ''),
                                    'student_answer': q.get('student', ''),
                                    'correct_answer': q.get('correct', ''),
                                    'is_correct': q.get('match', False)
                                }
                                questions.append(question_info)
                            question_details[section] = {
                                'questions': questions,
                                'total': section_total
                            }
            
            # Use total questions from Excel if available, otherwise sum from sections
            total_questions = total_questions_from_excel if total_questions_from_excel > 0 else sum(section_totals.values())
            
            # Calculate normalized total score (out of 100)
            normalized_total_score = round((total_score / total_questions * 100) if total_questions > 0 else 0)
            
            # Update statistics
            total_students += 1
            highest_score = max(highest_score, normalized_total_score)
            total_score_sum += normalized_total_score
            
            # Format student data for template
            formatted_student = {
                'name': data.get('name', 'Unknown'),
                'dob': data.get('dob', ''),
                'address': data.get('address', ''),
                'pu_college': data.get('puCollege', ''),
                'stream': data.get('stream', ''),
                'phone': data.get('mobile', ''),
                'exam_date': data.get('exam_date', ''),
                'completion_time': data.get('completion_time', ''),
                'raw_score': total_score,
                'total_score': normalized_total_score,
                'section_scores': section_scores,
                'question_details': question_details,
                'total_questions': total_questions
            }
            
            students_data.append(formatted_student)
            print(f"\nProcessed student: {formatted_student['name']} with {len(question_details)} sections")
            print(f"Raw score: {total_score}/{total_questions}")
            print(f"Normalized score: {normalized_total_score}/100")
            
            # Print section-wise scores for debugging
            for section, score_data in section_scores.items():
                print(f"{section}: {score_data['raw_score']}/{score_data['total']} (Normalized: {score_data['normalized_score']}/100)")
        
        # Calculate average score
        average_score = round(total_score_sum / total_students) if total_students > 0 else 0
        
        template_data = {
            'students': students_data,
            'stats': {
                'total_students': total_students,
                'highest_score': highest_score,
                'average_score': average_score,
                'total_questions': total_questions_from_excel  # Add total questions to stats
            }
        }
        
        return render_template('index.html', data=template_data)
        
    except Exception as e:
        print(f"\n!!! Error in admin_dashboard !!!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Full error details: {e}")
        return render_template('index.html', data={'students': [], 'stats': {'total_students': 0, 'highest_score': 0, 'average_score': 0, 'total_questions': 0}})

@app.route('/login')
def login():
    excel_data = read_excel_data()
    return render_template('login.html', 
                         sections=excel_data['sections'],
                         duration=excel_data['duration'],
                         year=2025)

# Add new route to handle login form submission
@app.route('/submit-login', methods=['POST'])
def submit_login():
    try:
        # Get sections from Excel
        excel_data = read_excel_data()
        sections = excel_data['sections']
        
        # Calculate total sum of all questions
        total_sum = sum(sections.values())
        
        # Initialize scores structure with correct total questions from Excel
        initial_scores = {}
        for section_name, total_questions in sections.items():
            initial_scores[section_name] = {
                'correct_answers': 0,
                'total_questions': total_questions,  # Use the actual count from Excel
                'marks': 0
            }

        student_data = {
            'name': request.form.get('name'),
            'dob': request.form.get('dob'),
            'puCollege': request.form.get('puCollege'),
            'stream': request.form.get('stream'),
            'mobile': request.form.get('mobile'),
            'address': request.form.get('address'),
            'exam_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'scores': initial_scores,  # Initialize with correct totals from Excel
            'total_questions': total_sum  # Add total sum of all questions
        }
        
        # Store in Firebase
        student_ref = db.collection('students').document()
        student_id = student_ref.id
        student_ref.set(student_data)
        
        # Store student_id in session
        session['student_id'] = student_id
        
        # Redirect to exam page
        return redirect(url_for('exam'))
    except Exception as e:
        print(f"Error in submit_login: {str(e)}")
        # If there's an error, still redirect to exam
        # The client-side has already saved data in sessionStorage
        return redirect(url_for('exam'))

def truncate_text(text, max_length=50):
    if pd.isna(text) or not isinstance(text, str):
        return ''
    return (text[:max_length] + '...') if len(text) > max_length else text

def load_questions():
    questions = {}
    if os.path.exists('exam_questions.xlsx'):
        excel_file = pd.ExcelFile('exam_questions.xlsx')
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # Remove any empty rows
            df = df.dropna(how='all')
            # Only truncate options, not questions
            if not df.empty:
                for col in ['Option A', 'Option B', 'Option C', 'Option D']:
                    if col in df.columns:
                        df[col] = df[col].apply(lambda x: truncate_text(x, 100))
                
                # Reset the index before shuffling to capture original order
                df = df.reset_index(drop=True)
                df['original_id'] = df.index.astype(str)  # use the original row index as a stable id
                
                # Shuffle the dataframe rows
                df = df.sample(frac=1).reset_index(drop=True)
                
                # Add question numbers after shuffling for display purposes
                questions_list = df.fillna('').to_dict('records')
                for i, q in enumerate(questions_list, 1):
                    q['question_number'] = i
                
                questions[sheet_name] = questions_list
    return questions

def read_excel_data():
    try:
        if not os.path.exists('exam_questions.xlsx'):
            print("Excel file not found")
            return {
                'sections': {},
                'duration': None,
                'total_questions': 0
            }
            
        # Read the Excel file
        xls = pd.ExcelFile('exam_questions.xlsx')
        sections = {}
        duration = None
        total_questions = 0
        
        # First try to get total questions from TotalQuestions sheet
        if 'TotalQuestions' in xls.sheet_names:
            try:
                total_df = pd.read_excel(xls, sheet_name='TotalQuestions')
                if 'Total' in total_df.columns:
                    total_questions = int(total_df['Total'].iloc[0])
                    print(f"Found total questions: {total_questions} from TotalQuestions sheet")
            except Exception as e:
                print(f"Error reading TotalQuestions sheet: {str(e)}")
        
        # Process each sheet
        for sheet_name in xls.sheet_names:
            if sheet_name == 'TotalQuestions':  # Skip the TotalQuestions sheet
                continue
                
            df = pd.read_excel(xls, sheet_name=sheet_name)
            print(f"Reading sheet: {sheet_name}")
            
            # Clean column names - strip whitespace and handle case
            df.columns = [str(col).strip() for col in df.columns]
            print(f"Columns found: {list(df.columns)}")
            
            # Count questions in this sheet - only if Question column exists
            if 'Question' in df.columns:
                valid_rows = df[df['Question'].notna()]
                question_count = len(valid_rows)
                
                if question_count > 0:
                    sections[sheet_name] = question_count
                    print(f"Found {question_count} questions in {sheet_name}")
                    
                    # Look for duration in any column
                    for col in df.columns:
                        if col == 'Duration':  # Exact match only
                            try:
                                # Look for numeric values in this column
                                duration_values = df[col].apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna()
                                if not duration_values.empty:
                                    first_value = duration_values.iloc[0]
                                    if pd.notnull(first_value) and 0 < first_value <= 180:
                                        duration = int(first_value)
                                        print(f"Found duration: {duration} in column {col}")
                                        break
                            except Exception as e:
                                print(f"Error reading duration from column {col}: {str(e)}")
                                continue
        
        print(f"Final duration: {duration}")
        print(f"Final sections: {sections}")
        print(f"Total questions: {total_questions}")
        
        return {
            'sections': sections,
            'duration': duration,
            'total_questions': total_questions
        }
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        return {
            'sections': {},
            'duration': None,
            'total_questions': 0
        }

@app.route('/exam')
def exam():
    current_date = datetime.now().strftime("%B %d, %Y")
    questions = load_questions()
    if not questions:
        questions = {}
    
    excel_data = read_excel_data()
    
    return render_template('index.html', 
                         questions=questions,
                         current_date=current_date,
                         duration=excel_data['duration'])

@app.route('/api/questions')
def get_questions():
    questions = load_questions()
    return jsonify(questions)

@app.route('/submit-exam', methods=['POST'])
def submit_exam():
    try:
        data = request.json
        student_id = session.get('student_id')
        
        if not student_id:
            return jsonify({'error': 'No student session found'}), 400

        # Get student answers and completion time
        answers = data.get('answers', {})
        completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get the questions for scoring and section counts from Excel
        questions = load_questions()
        excel_data = read_excel_data()
        section_counts = excel_data['sections']
        
        # Calculate total sum of all questions
        total_sum = sum(section_counts.values())
        
        # Initialize scores structure
        scores = {}
        question_details = {}

        # Process each section
        for section_name, section_answers in answers.items():
            section_questions = questions.get(section_name, [])
            
            # Get total questions from Excel data
            total_questions = section_counts.get(section_name, 0)
            
            # Initialize section scores with correct total from Excel
            scores[section_name] = {
                'correct_answers': 0,
                'total_questions': total_questions,  # Use the count from Excel
                'marks': 0,
                'debug': []
            }

            # Process each question in the section
            for q in section_questions:
                q_num = str(q.get('original_id', ''))
                student_answer = section_answers.get(q_num)
                correct_answer = q.get('Correct Answer')
                
                # Create debug entry
                debug_entry = {
                    'q_num': q_num,
                    'question': q.get('Question', ''),
                    'correct': correct_answer,
                    'student': student_answer,
                    'match': False
                }

                # Check if answer is correct
                if student_answer and correct_answer and student_answer.upper() == correct_answer.upper():
                    scores[section_name]['correct_answers'] += 1
                    scores[section_name]['marks'] += 1
                    debug_entry['match'] = True

                scores[section_name]['debug'].append(debug_entry)

        # Update student document in Firebase
        student_ref = db.collection('students').document(student_id)
        student_ref.update({
            'completion_time': completion_time,
            'scores': scores,
            'question_details': question_details,
            'total_questions': total_sum  # Add total sum of all questions
        })

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error submitting exam: {str(e)}")
        return jsonify({'error': 'Failed to submit exam'}), 500

@app.route('/admin/results')
def view_results():
    try:
        # Get all student records
        students = db.collection('students').stream()
        results = []
        
        for student in students:
            data = student.to_dict()
            results.append({
                'name': data.get('name'),
                'puCollege': data.get('puCollege'),
                'exam_date': data.get('exam_date'),
                'scores': data.get('scores', {})
            })
            
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add a debug route to test score calculation
@app.route('/debug/test-scoring')
def debug_test_scoring():
    # Create a test set of answers
    test_answers = {
        "Java": {
            "1": "A",
            "2": "A",
            "3": "A",
            "4": "A",
            "5": "A"
        }
    }
    
    # Get questions and correct answers
    questions = load_questions()
    
    # Debug information
    debug_info = {
        "test_answers": test_answers,
        "comparison": []
    }
    
    # For each section, compare answers
    for section, section_questions in questions.items():
        if section in test_answers:
            section_debug = {
                "section": section,
                "questions": []
            }
            
            for q in section_questions:
                question_num = q['question_number']
                q_num_str = str(question_num)
                student_answer = test_answers.get(section, {}).get(q_num_str)
                correct_answer = q.get('Correct Answer')
                
                # Match check
                is_match = False
                if student_answer and correct_answer:
                    is_match = student_answer.upper() == correct_answer.upper()
                
                section_debug["questions"].append({
                    "question_number": question_num,
                    "student_answer": student_answer,
                    "correct_answer": correct_answer,
                    "is_match": is_match,
                    "student_answer_upper": student_answer.upper() if student_answer else None,
                    "correct_answer_upper": correct_answer.upper() if correct_answer else None
                })
            
            debug_info["comparison"].append(section_debug)
    
    # Calculate scores
    scores = calculate_scores(test_answers)
    debug_info["calculated_scores"] = scores
    
    return jsonify(debug_info)

if __name__ == '__main__':
    app.run(port=5000) 