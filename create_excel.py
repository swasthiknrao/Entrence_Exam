import pandas as pd
import os

def get_next_course_number(existing_sheets):
    # Find the highest course number from existing sheets
    highest_num = 0
    for sheet in existing_sheets:
        if sheet.startswith('Course '):
            try:
                num = int(sheet.split(' ')[1])
                highest_num = max(highest_num, num)
            except:
                continue
    return highest_num + 1

def create_exam_excel():
    if os.path.exists('exam_questions.xlsx'):
        # If file exists, read existing sheets
        with pd.ExcelFile('exam_questions.xlsx') as xls:
            existing_sheets = xls.sheet_names
            next_course_num = get_next_course_number(existing_sheets)
            new_course = f'Course {next_course_num}'
        
        # Create Excel writer object with existing file
        with pd.ExcelWriter('exam_questions.xlsx', engine='openpyxl', mode='a') as writer:
            # Create empty DataFrame with required columns
            # Calculate number of questions based on course number
            if next_course_num == 1:  # First course (basics) - more questions
                num_questions = 50
            elif next_course_num == 2:  # Second course (core concepts) - most questions
                num_questions = 60
            else:  # Advanced courses - fewer but more complex questions
                num_questions = 30
                
            df = pd.DataFrame({
                'Question': [''] * num_questions,
                'Option A': [''] * num_questions,
                'Option B': [''] * num_questions,
                'Option C': [''] * num_questions,
                'Option D': [''] * num_questions,
                'Correct Answer': [''] * num_questions,
           
            })
            
            # Add Duration column only if this is Course 1
            if next_course_num == 1:
                df.insert(0, 'Duration', [''] + [''] * (num_questions - 1))
            
            # Write to Excel sheet
            df.to_excel(writer, sheet_name=new_course, index=False)
            
            # Get the worksheet
            worksheet = writer.sheets[new_course]
            
            # Format the worksheet
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
            print(f"\nCreated {new_course} with {num_questions} questions")
            if next_course_num == 1:
                print("\nNOTE: Please enter the total exam duration (in minutes) in the 'Duration' column of Course 1")
            print(f"Each question carries {2 if next_course_num > 2 else 1} mark(s)")
            print("\nFor 'Correct Answer' column, please enter A, B, C, or D (the option letter)")
            
    else:
        # If file doesn't exist, create new file with Course 1
        with pd.ExcelWriter('exam_questions.xlsx', engine='openpyxl') as writer:
            # First course has 50 questions
            num_questions = 50
            
            columns = {
                'Question': [''] * num_questions,
                'Option A': [''] * num_questions,
                'Option B': [''] * num_questions,
                'Option C': [''] * num_questions,
                'Option D': [''] * num_questions,
                'Correct Answer': [''] * num_questions,
               
            }
            
            # Add Duration column to Course 1
            columns['Duration'] = [''] + [''] * (num_questions - 1)
            
            df = pd.DataFrame(columns)
            
            # Write to Excel sheet
            df.to_excel(writer, sheet_name='Course 1', index=False)
            
            # Get the worksheet
            worksheet = writer.sheets['Course 1']
            
            # Format the worksheet
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
            print("\nCreated Course 1 with 50 questions")
            print("\nNOTE: Please enter the total exam duration (in minutes) in the 'Duration' column of Course 1")
            print("Each question carries 1 mark")
            print("\nFor 'Correct Answer' column, please enter A, B, C, or D (the option letter)")

if __name__ == "__main__":
    create_exam_excel()
    print("\nExcel file 'exam_questions.xlsx' has been created/updated successfully!") 
