import sqlite3
from flask import jsonify


# Function to get the database connection
def get_db_connection():
    try:
        conn = sqlite3.connect('database/database.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {str(e)}")
        return None


# Get Application Date
def get_application_date():
    conn = get_db_connection()
    application_date = conn.execute('SELECT application_date FROM Application').fetchall()
    conn.close()
    return application_date


# Get the Jobs applied by the user
def get_application(date):
    conn = get_db_connection()
    application = conn.execute('SELECT Application.application_id, Application.application_date, Company.company_name, '
                               'Title.title_name, COUNT(Interview.interview_id) AS interview_numbers, Application.offer '
                               'FROM Application LEFT JOIN Company ON Application.fk_company_id = Company.company_id '
                               'LEFT JOIN Title ON Application.fk_title_id = Title.title_id '
                               'LEFT JOIN Interview ON Application.application_id = Interview.fk_application_id '
                               'WHERE Application.application_date = ? '
                               'GROUP BY Application.application_id, Application.application_date, Company.company_name, '
                               'Title.title_name, Application.offer; ', (date, )).fetchall()
    conn.close()
    return application


# Get application info
def get_application_info():
    conn = get_db_connection()
    application_info = conn.execute('SELECT Application.application_id, COUNT(Interview.interview_id) AS interview_numbers, Application.offer '
                                      'FROM Application LEFT JOIN Interview ON Application.application_id = Interview.fk_application_id '
                                        'GROUP BY Application.application_id').fetchall()
    conn.close()
    return application_info


# Get the company names
def get_company_names():
    conn = get_db_connection()
    company_names = conn.execute('SELECT company_name FROM Company').fetchall()
    conn.close()
    sorted_company_names = sorted([name['company_name'] for name in company_names])
    return sorted_company_names

# Get the title names
def get_title_names(company_name):
    conn = get_db_connection()
    title_names = conn.execute('SELECT Title.title_name '
                               'FROM Application LEFT JOIN Company ON Application.fk_company_id = Company.company_id '
                               'LEFT JOIN Title ON Application.fk_title_id = Title.title_id '
                               'WHERE Company.company_name = ?', (company_name, )).fetchall()
    conn.close()
    return title_names


# Search for the application by company name and title name
def search_application(company_name, title_name):
    conn = get_db_connection()
    applications = conn.execute('SELECT Application.application_id, Application.application_date, Company.company_name, '
                               'Title.title_name, COUNT(Interview.interview_id) AS interview_numbers, Application.offer '
                               'FROM Application LEFT JOIN Company ON Application.fk_company_id = Company.company_id '
                               'LEFT JOIN Title ON Application.fk_title_id = Title.title_id '
                               'LEFT JOIN Interview ON Application.application_id = Interview.fk_application_id '
                               'WHERE Company.company_name = ? AND Title.title_name = ?', (company_name, title_name)).fetchall()
    conn.close()
    return applications


# Insert a new job application
def insert_application(application_date, company_name, title_name, offer=0):
    conn = get_db_connection()
    conn.execute('INSERT INTO Application (application_date, fk_company_id, fk_title_id, offer) VALUES (?, ?, ?, ?)',
                 (application_date, company_name, title_name, offer))
    conn.commit()
    conn.close()
    return 'Application added successfully'


# Update the job application
def update_interview_offer(application_id, value):
    conn = get_db_connection()
    try:
        conn.execute(f'UPDATE Application SET offer = ? WHERE application_id = ?', (value, application_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})


# Delete the job application
def delete_job_application(application_id):
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM Application WHERE application_id = ?', (application_id, ))
        conn.commit()
        conn.close()
        response = jsonify({'success': True, 'message': 'Application deleted successfully'})
        return response
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})


def insert_application(data):
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed", None

    try:
        cursor = conn.cursor()

        # Start transaction
        conn.execute('BEGIN TRANSACTION')

        # Check if company exists
        cursor.execute(
            "SELECT company_id FROM Company WHERE company_name = ?",
            (data['company_name'],)
        )
        company_result = cursor.fetchone()

        if company_result:
            company_id = company_result['company_id']
        else:
            # Insert new company
            cursor.execute(
                "INSERT INTO Company (company_name) VALUES (?)",
                (data['company_name'],)
            )
            company_id = cursor.lastrowid

        # Check if title exists
        cursor.execute(
            "SELECT title_id FROM Title WHERE title_name = ?",
            (data['title_name'],)
        )
        title_result = cursor.fetchone()

        if title_result:
            title_id = title_result['title_id']
        else:
            # Insert new title
            cursor.execute(
                "INSERT INTO Title (title_name) VALUES (?)",
                (data['title_name'],)
            )
            title_id = cursor.lastrowid

        # Insert new application
        cursor.execute("""
                INSERT INTO Application 
                (application_date, offer, fk_company_id, fk_title_id)
                VALUES (?, ?, ?, ?)
            """, (
            data['application_date'],
            data.get('offer', 0),  # Default to 0 if not provided
            company_id,
            title_id
        ))

        new_application_id = cursor.lastrowid

        # Commit transaction
        conn.commit()

        return True, "Application added successfully", new_application_id

    except sqlite3.Error as e:
        conn.rollback()
        error_msg = f"Database error: {str(e)}"
        print(error_msg)
        return False, error_msg, None

    except Exception as e:
        conn.rollback()
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        return False, error_msg, None

    finally:
        conn.close()


def update_interview_stage(application_id, delta):
    conn = get_db_connection()
    if conn is None:
        return {'success': False, 'message': 'Failed to connect to the database'}

    try:
        cursor = conn.cursor()

        # Get the current stage (count of interviews for the application)
        cursor.execute("""
                SELECT COUNT(*) AS stage_count
                FROM Interview
                WHERE fk_application_id = ?
            """, (application_id,))
        result = cursor.fetchone()
        current_stage = result['stage_count'] if result else 0

        # Calculate the new stage
        new_stage = max(0, current_stage + delta)

        # Update the Interview table
        if delta > 0:
            # Add rows to increase the stage
            for _ in range(delta):
                cursor.execute("""
                        INSERT INTO Interview (fk_application_id)
                        VALUES (?)
                    """, (application_id,))
        elif delta < 0:
            # Remove rows to decrease the stage
            cursor.execute("""
                    DELETE FROM Interview
                    WHERE fk_application_id = ?
                    AND interview_id IN (
                        SELECT interview_id FROM Interview
                        WHERE fk_application_id = ?
                        LIMIT ?
                    )
                """, (application_id, application_id, abs(delta)))

        conn.commit()
        return {'success': True, 'new_stage': new_stage}
    except Exception as e:
        print(f"Error updating interview stage: {str(e)}")
        return {'success': False, 'message': 'Internal server error'}
    finally:
        conn.close()




