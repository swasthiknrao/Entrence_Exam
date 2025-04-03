from flask import Flask, render_template, jsonify, session, redirect, url_for, send_from_directory, request
import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize Firebase with correct path to credentials
try:
    cred = credentials.Certificate('serviceAccountKey.json')  # Updated path to look in root directory
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    raise e

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return redirect(url_for('admin_dashboard'))

@app.route('/debug/data')
def debug_data():
    try:
        students_ref = db.collection('students')
        students = students_ref.get()
        data = []
        for student in students:
            student_data = student.to_dict()
            student_data['id'] = student.id
            data.append(student_data)
        return jsonify({
            'success': True,
            'count': len(data),
            'data': data
        })
    except Exception as e:
        print(f"Debug data error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        })

@app.route('/admin')
def admin_dashboard():
    try:
        print("\n=== Starting admin_dashboard route ===")
        
        # Get all student records
        students_ref = db.collection('students')
        students = students_ref.get()
        print(f"Connected to Firebase successfully")
        
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
            
            # Get total score from database or calculate it
            total_score = data.get('total_score', 0)  # Get total score from database
            if total_score == 0:  # If not in database, calculate it
                total_score = sum(section_data.get('marks', 0) for section_data in scores.values() if isinstance(section_data, dict))
            
            # Calculate total questions across all sections
            total_questions = sum(section_data.get('total_questions', 0) for section_data in scores.values() if isinstance(section_data, dict))
            
            # Update statistics
            total_students += 1
            highest_score = max(highest_score, total_score)
            total_score_sum += total_score
            
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
                'total_score': total_score,  # Use the total score directly
                'section_scores': section_scores,
                'question_details': question_details,
                'total_questions': total_questions
            }
            
            students_data.append(formatted_student)
            print(f"\nProcessed student: {formatted_student['name']} with {len(question_details)} sections")
            print(f"Raw score: {total_score}/{total_questions}")
            
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
                'total_questions': total_questions
            }
        }
        
        return render_template('index.html', data=template_data)
        
    except Exception as e:
        print(f"\n!!! Error in admin_dashboard !!!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Full error details: {e}")
        return render_template('index.html', data={'students': [], 'stats': {'total_students': 0, 'highest_score': 0, 'average_score': 0}})

if __name__ == '__main__':
    app.run(debug=True) 