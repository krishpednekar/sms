from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# -------------------- DATABASE CONNECTION --------------------
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",        # Default user for XAMPP
            password="",        # Leave blank if not set
            database="student_management"  # Ensure this DB exists in phpMyAdmin
        )
        return connection
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        return None

# -------------------- ROUTES --------------------

@app.route('/')
def index():
    return render_template('index.html')

# ------------------------------------------------------------
# STUDENTS
# ------------------------------------------------------------

@app.route('/students')
def list_students():
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return render_template('students/list.html', students=[])
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('students/list.html', students=students)


@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        data = (
            request.form['student_id'],
            request.form['first_name'],
            request.form['last_name'],
            request.form['email'],
            request.form.get('phone'),
            request.form.get('address'),
            request.form['program'],
            request.form['semester']
        )
        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", "danger")
            return redirect(url_for('list_students'))
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO students (student_id, first_name, last_name, email, phone, address, program, semester)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, data)
            conn.commit()
            flash('✅ Student added successfully!', 'success')
        except Error as e:
            conn.rollback()
            flash(f'❌ Error adding student: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('list_students'))
    return render_template('students/add.html')

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('list_students'))
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
        student = cursor.fetchone()
        if not student:
            flash("Student not found!", "danger")
            return redirect(url_for('list_students'))

        if request.method == 'POST':
            updated = (
                request.form['student_id'],
                request.form['first_name'],
                request.form['last_name'],
                request.form['email'],
                request.form.get('phone'),
                request.form.get('address'),
                request.form['program'],
                request.form['semester'],
                id
            )
            try:
                cursor.execute("""
                    UPDATE students SET student_id=%s, first_name=%s, last_name=%s,
                    email=%s, phone=%s, address=%s, program=%s, semester=%s WHERE id=%s
                """, updated)
                conn.commit()
                flash('✅ Student updated successfully!', 'success')
            except Error as e:
                conn.rollback()
                flash(f'❌ Error updating student: {e}', 'danger')
            return redirect(url_for('list_students'))

    finally:
        cursor.close()
        conn.close()

    return render_template('students/edit.html', student=student)

@app.route('/students/delete/<int:id>', methods=['POST'])
def delete_student(id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('list_students'))
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM marks WHERE student_id=%s", (id,))
        cursor.execute("DELETE FROM attendance WHERE student_id=%s", (id,))
        cursor.execute("DELETE FROM enrollments WHERE student_id=%s", (id,))
        cursor.execute("DELETE FROM students WHERE id=%s", (id,))
        conn.commit()
        flash('✅ Student deleted successfully!', 'success')
    except Error as e:
        conn.rollback()
        flash(f'❌ Error deleting student: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('list_students'))

# ------------------------------------------------------------
# SUBJECTS
# ------------------------------------------------------------

@app.route('/subjects')
def list_subjects():
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return render_template('subjects/list.html', subjects=[])
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('subjects/list.html', subjects=subjects)

@app.route('/subjects/add', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        data = (request.form['code'], request.form['name'], request.form['credits'])
        conn = get_db_connection()
        if not conn:
            flash("Database connection failed", "danger")
            return redirect(url_for('list_subjects'))
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO subjects (code, name, credits) VALUES (%s,%s,%s)", data)
            conn.commit()
            flash('✅ Subject added successfully!', 'success')
        except Error as e:
            conn.rollback()
            flash(f'❌ Error adding subject: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('list_subjects'))
    return render_template('subjects/add.html')

@app.route('/subjects/edit/<int:id>', methods=['GET', 'POST'])
def edit_subject(id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('list_subjects'))
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM subjects WHERE id=%s", (id,))
        subject = cursor.fetchone()
        if not subject:
            flash("Subject not found!", "danger")
            return redirect(url_for('list_subjects'))

        if request.method == 'POST':
            updated = (request.form['code'], request.form['name'], request.form['credits'], id)
            try:
                cursor.execute("UPDATE subjects SET code=%s, name=%s, credits=%s WHERE id=%s", updated)
                conn.commit()
                flash('✅ Subject updated successfully!', 'success')
            except Error as e:
                conn.rollback()
                flash(f'❌ Error updating subject: {e}', 'danger')
            return redirect(url_for('list_subjects'))

    finally:
        cursor.close()
        conn.close()

    return render_template('subjects/edit.html', subject=subject)

@app.route('/subjects/delete/<int:id>', methods=['POST'])
def delete_subject(id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('list_subjects'))
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM subjects WHERE id=%s", (id,))
        conn.commit()
        flash('✅ Subject deleted successfully!', 'success')
    except Error as e:
        conn.rollback()
        flash(f'❌ Error deleting subject: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('list_subjects'))

# ------------------------------------------------------------
# ENROLLMENT
# ------------------------------------------------------------

@app.route('/students/<int:id>/enroll', methods=['GET', 'POST'])
def enroll_student(id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('list_students'))
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
        student = cursor.fetchone()

        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()

        if request.method == 'POST':
            subject_id = request.form['subject']
            try:
                enrollment_date = datetime.utcnow().date()  # date only
                cursor.execute("INSERT INTO enrollments (student_id, subject_id, enrollment_date) VALUES (%s,%s,%s)",
                               (id, subject_id, enrollment_date))
                conn.commit()
                flash('✅ Enrollment successful!', 'success')
            except Error as e:
                conn.rollback()
                flash(f'❌ Error enrolling student: {e}', 'danger')
            return redirect(url_for('view_student', id=id))
    finally:
        cursor.close()
        conn.close()

    return render_template('students/enroll.html', student=student, subjects=subjects)

# ------------------------------------------------------------
# VIEW STUDENT DETAILS (Marks + Attendance)
# ------------------------------------------------------------

@app.route('/students/<int:id>')
def view_student(id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('list_students'))
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
        student = cursor.fetchone()

        cursor.execute("""SELECT e.*, s.name AS subject_name 
                          FROM enrollments e JOIN subjects s ON e.subject_id=s.id 
                          WHERE e.student_id=%s""", (id,))
        enrollments = cursor.fetchall()

        cursor.execute("""SELECT m.*, s.name AS subject_name 
                          FROM marks m LEFT JOIN subjects s ON m.subject_id=s.id 
                          WHERE m.student_id=%s""", (id,))
        marks = cursor.fetchall()

        cursor.execute("""SELECT a.*, s.name AS subject_name 
                          FROM attendance a LEFT JOIN subjects s ON a.subject_id=s.id 
                          WHERE a.student_id=%s""", (id,))
        attendance = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('students/view.html', student=student, enrollments=enrollments, marks=marks, attendance=attendance)

# ------------------------------------------------------------
# MARKS MANAGEMENT (added & fixed)
# ------------------------------------------------------------

@app.route('/students/<int:id>/marks', methods=['GET', 'POST'])
def manage_marks(id):
    """View/add marks for a student. Endpoint name uses 'id' to match templates."""
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('list_students'))
    cursor = conn.cursor(dictionary=True)
    try:
        # get student
        cursor.execute("SELECT * FROM students WHERE id=%s", (id,))
        student = cursor.fetchone()
        if not student:
            flash("Student not found", "danger")
            return redirect(url_for('list_students'))

        # for the form, show subjects (so user can choose subject by id)
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()

        if request.method == 'POST':
            subject_id = request.form['subject_id']
            marks_val = request.form['marks']
            max_marks = request.form.get('max_marks', 100)
            exam_date = request.form.get('exam_date') or datetime.utcnow().date()

            try:
                cursor.execute("""
                    INSERT INTO marks (student_id, subject_id, marks, max_marks, exam_date)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id, subject_id, marks_val, max_marks, exam_date))
                conn.commit()
                flash("✅ Marks added successfully!", "success")
            except Error as e:
                conn.rollback()
                flash(f"❌ Error adding marks: {e}", "danger")
            return redirect(url_for('manage_marks', id=id))

        # fetch marks (with subject name)
        cursor.execute("""
            SELECT m.*, s.name AS subject_name
            FROM marks m LEFT JOIN subjects s ON m.subject_id = s.id
            WHERE m.student_id = %s
            ORDER BY m.exam_date DESC
        """, (id,))
        marks = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template('marks/manage.html', student=student, subjects=subjects, marks=marks)


@app.route('/marks/edit/<int:mark_id>', methods=['GET', 'POST'])
def edit_mark(mark_id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('list_students'))
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM marks WHERE id=%s", (mark_id,))
        mark = cursor.fetchone()
        if not mark:
            flash("Mark not found", "danger")
            return redirect(url_for('list_students'))

        # get subjects for dropdown
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()

        if request.method == 'POST':
            subject_id = request.form['subject_id']
            marks_val = request.form['marks']
            max_marks = request.form.get('max_marks', 100)
            exam_date = request.form.get('exam_date') or datetime.utcnow().date()

            try:
                cursor.execute("""
                    UPDATE marks SET subject_id=%s, marks=%s, max_marks=%s, exam_date=%s
                    WHERE id=%s
                """, (subject_id, marks_val, max_marks, exam_date, mark_id))
                conn.commit()
                flash("✅ Mark updated successfully!", "success")
            except Error as e:
                conn.rollback()
                flash(f"❌ Error updating mark: {e}", "danger")
            return redirect(url_for('manage_marks', id=mark['student_id']))
    finally:
        cursor.close()
        conn.close()

    return render_template('marks/edit.html', mark=mark, subjects=subjects)


@app.route('/marks/delete/<int:mark_id>', methods=['POST'])
def delete_mark(mark_id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "danger")
        return redirect(url_for('list_students'))
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT student_id FROM marks WHERE id=%s", (mark_id,))
        row = cursor.fetchone()
        if not row:
            flash("Mark not found", "danger")
            return redirect(url_for('list_students'))
        student_id = row['student_id']
        cursor.execute("DELETE FROM marks WHERE id=%s", (mark_id,))
        conn.commit()
        flash("✅ Mark deleted successfully!", "success")
    except Error as e:
        conn.rollback()
        flash(f"❌ Error deleting mark: {e}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('manage_marks', id=student_id))

# ------------------------------------------------------------
# REPORTS
# ------------------------------------------------------------

@app.route('/reports')
def view_reports():
    return render_template('reports/index.html')

@app.route('/reports/students')
def student_reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('reports/students.html', students=students)

@app.route('/reports/subjects')
def subject_reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('reports/subjects.html', subjects=subjects)

@app.route('/reports/attendance')
def attendance_reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT s.first_name, s.last_name, sub.name AS subject_name,
            SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present_days,
            COUNT(a.id) AS total_days
            FROM attendance a
            JOIN students s ON s.id=a.student_id
            JOIN subjects sub ON sub.id=a.subject_id
            GROUP BY s.id, sub.id
        """)
        data = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('reports/attendance.html', attendance_data=data)

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
