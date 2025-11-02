from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

print(f"Database path: {app.config['SQLALCHEMY_DATABASE_URI']}")
# Models
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    program = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    marks = db.relationship('Mark', backref='student', lazy=True)
    attendances = db.relationship('Attendance', backref='student', lazy=True)
    @property
    def available_subjects(self):
        """Returns all subjects the student can potentially be marked on"""
        enrolled = {e.subject_id for e in self.enrollments}
        return Subject.query.filter(
            (Subject.id.in_(enrolled)) | 
            (Subject.id.notin_(enrolled))
        ).all()

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    enrollment_date = db.Column(db.Date, default=datetime.utcnow)
    
    # Relationships
    subject = db.relationship('Subject', backref='enrollments')

class Mark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    marks = db.Column(db.Float, nullable=False)
    max_marks = db.Column(db.Float, nullable=False, default=100)
    exam_date = db.Column(db.Date, default=datetime.utcnow)
    
    # Relationship
    subject = db.relationship('Subject', backref='marks')

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    status = db.Column(db.String(10), nullable=False)  # Present/Absent
    subject = db.relationship('Subject')

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students')
def list_students():
    students = Student.query.all()
    return render_template('students/list.html', students=students)

# ... (keep all your existing student CRUD routes)

# New routes for enhanced features
@app.route('/students/<int:id>/enroll', methods=['GET', 'POST'])
def enroll_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        subject_id = request.form['subject']
        enrollment = Enrollment(student_id=id, subject_id=subject_id)
        db.session.add(enrollment)
        db.session.commit()
        flash('Enrollment successful!', 'success')
        return redirect(url_for('view_student', id=id))
    
    subjects = Subject.query.all()
    enrolled = [e.subject_id for e in student.enrollments]
    return render_template('students/enroll.html', 
                         student=student,
                         subjects=subjects,
                         enrolled=enrolled)

@app.route('/students/<int:id>')
def view_student(id):
    student = Student.query.get_or_404(id)
    enrollments = Enrollment.query.filter_by(student_id=id).all()
    marks = Mark.query.filter_by(student_id=id).all()
    attendance = Attendance.query.filter_by(student_id=id).all()
    
    # Calculate attendance percentage per subject
    attendance_stats = {}
    for enrollment in enrollments:
        total = Attendance.query.filter_by(
            student_id=id,
            subject_id=enrollment.subject_id
        ).count()
        present = Attendance.query.filter_by(
            student_id=id,
            subject_id=enrollment.subject_id,
            status='Present'
        ).count()
        attendance_stats[enrollment.subject_id] = {
            'name': enrollment.subject.name,
            'percentage': (present/total)*100 if total > 0 else 0
        }
    
    return render_template('students/view.html',
                         student=student,
                         enrollments=enrollments,
                         marks=marks,
                         attendance=attendance,
                         attendance_stats=attendance_stats,
                         datetime=datetime) 

@app.route('/students/<int:id>/attendance', methods=['GET', 'POST'])
def manage_attendance(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        subject_id = request.form['subject']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        status = request.form['status']
        
        attendance = Attendance(
            student_id=id,
            subject_id=subject_id,
            date=date,
            status=status
        )
        db.session.add(attendance)
        db.session.commit()
        flash('Attendance recorded!', 'success')
        return redirect(url_for('view_student', id=id))
    
    subjects = [e.subject for e in student.enrollments]
    return render_template('students/attendance.html',
                         student=student,
                         subjects=subjects)

# Add this route with your other student routes
@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student_data = {
            'student_id': request.form['student_id'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'program': request.form['program'],
            'semester': request.form['semester']
        }
        
        student = Student(**student_data)
        db.session.add(student)
        try:
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('list_students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding student: {str(e)}', 'danger')
    
    return render_template('students/add.html')

# Add these new routes to your existing app.py

@app.route('/students/<int:student_id>/marks/<int:mark_id>/edit', methods=['GET', 'POST'])
def edit_mark(student_id, mark_id):
    student = Student.query.get_or_404(student_id)
    mark = Mark.query.get_or_404(mark_id)
    
    if request.method == 'POST':
        mark.subject_id = request.form['subject']
        mark.marks = float(request.form['marks'])
        mark.max_marks = float(request.form.get('max_marks', 100))
        mark.exam_date = datetime.strptime(request.form['exam_date'], '%Y-%m-%d')
        
        db.session.commit()
        flash('Mark updated successfully!', 'success')
        return redirect(url_for('view_student', id=student_id))
    
    subjects = [e.subject for e in student.enrollments]
    return render_template('students/edit_mark.html',
                         student=student,
                         mark=mark,
                         subjects=subjects)

@app.route('/students/<int:student_id>/marks/<int:mark_id>/delete', methods=['POST'])
def delete_mark(student_id, mark_id):
    mark = Mark.query.get_or_404(mark_id)
    db.session.delete(mark)
    db.session.commit()
    flash('Mark deleted successfully!', 'success')
    return redirect(url_for('view_student', id=student_id))


@app.route('/students/<int:id>/marks', methods=['GET', 'POST'])
@app.route('/students/<int:id>/marks', methods=['GET', 'POST'])
def manage_marks(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        subject_id = request.form['subject']
        marks = float(request.form['marks'])
        max_marks = float(request.form.get('max_marks', 100))
        exam_date = datetime.strptime(request.form['exam_date'], '%Y-%m-%d')
        
        mark = Mark(
            student_id=id,
            subject_id=subject_id,
            marks=marks,
            max_marks=max_marks,
            exam_date=exam_date
        )
        db.session.add(mark)
        db.session.commit()
        flash('Marks added successfully!', 'success')
        return redirect(url_for('view_student', id=id))
    
    # Use the available_subjects property
    subjects = student.available_subjects
    
    return render_template('students/marks.html',
                         student=student,
                         subjects=subjects,
                         datetime=datetime)

#------------------------------------------------

# Subject Management Routes
@app.route('/subjects')
def list_subjects():
    subjects = Subject.query.all()
    return render_template('subjects/list.html', subjects=subjects)

@app.route('/subjects/add', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        subject = Subject(
            code=request.form['code'],
            name=request.form['name'],
            credits=int(request.form['credits'])
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('list_subjects'))
    return render_template('subjects/add.html')

@app.route('/subjects/edit/<int:id>', methods=['GET', 'POST'])
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    if request.method == 'POST':
        subject.code = request.form['code']
        subject.name = request.form['name']
        subject.credits = int(request.form['credits'])
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('list_subjects'))
    return render_template('subjects/edit.html', subject=subject)

@app.route('/subjects/delete/<int:id>', methods=['POST'])
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('list_subjects'))

# Report Generation Routes
@app.route('/reports')
def view_reports():
    return render_template('reports/index.html')

@app.route('/reports/students')
def student_reports():
    students = Student.query.all()
    return render_template('reports/students.html', students=students)

@app.route('/reports/subjects')
def subject_reports():
    subjects = Subject.query.all()
    return render_template('reports/subjects.html', subjects=subjects)

@app.route('/reports/attendance')
def attendance_reports():
    # Get attendance summary for all students
    attendance_data = []
    students = Student.query.all()
    
    for student in students:
        enrollments = Enrollment.query.filter_by(student_id=student.id).all()
        student_data = {
            'student': student,
            'subjects': []
        }
        
        for enrollment in enrollments:
            total = Attendance.query.filter_by(
                student_id=student.id,
                subject_id=enrollment.subject_id
            ).count()
            
            present = Attendance.query.filter_by(
                student_id=student.id,
                subject_id=enrollment.subject_id,
                status='Present'
            ).count()
            
            percentage = (present / total * 100) if total > 0 else 0
            
            student_data['subjects'].append({
                'name': enrollment.subject.name,
                'percentage': percentage
            })
        
        attendance_data.append(student_data)
    
    return render_template('reports/attendance.html', attendance_data=attendance_data)

#------------------------------------------------
@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        # Update student data
        student.student_id = request.form['student_id']
        student.first_name = request.form['first_name']
        student.last_name = request.form['last_name']
        student.email = request.form['email']
        student.phone = request.form.get('phone')
        student.address = request.form.get('address')
        student.program = request.form['program']
        student.semester = request.form['semester']
        
        try:
            db.session.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('list_students'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'danger')

    return render_template('students/edit.html', student=student)

@app.route('/students/<int:id>/report')
def student_report(id):
    student = Student.query.get_or_404(id)
    enrollments = Enrollment.query.filter_by(student_id=id).all()
    marks = Mark.query.filter_by(student_id=id).all()
    attendance = Attendance.query.filter_by(student_id=id).all()
    
    # Calculate attendance percentage per subject
    attendance_stats = {}
    for subj in [e.subject for e in enrollments]:
        total = Attendance.query.filter_by(student_id=id, subject_id=subj.id).count()
        present = Attendance.query.filter_by(student_id=id, subject_id=subj.id, status='Present').count()
        attendance_stats[subj.id] = {
            'name': subj.name,
            'percentage': (present/total)*100 if total > 0 else 0
        }
    
    return render_template('students/report.html',
                         student=student,
                         enrollments=enrollments,
                         marks=marks,
                         attendance=attendance,
                         attendance_stats=attendance_stats)

@app.route('/students/delete/<int:id>', methods=['POST'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    try:
        # First delete all related records (marks, attendance, enrollments)
        Mark.query.filter_by(student_id=id).delete()
        Attendance.query.filter_by(student_id=id).delete()
        Enrollment.query.filter_by(student_id=id).delete()
        
        # Then delete the student
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting student: {str(e)}', 'danger')
    return redirect(url_for('list_students'))

if __name__ == '__main__':
    app.run(debug=True)