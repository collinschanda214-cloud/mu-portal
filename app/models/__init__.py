from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(200), nullable=False)
    mode = db.Column(db.String(30), default="Fulltime")
    school = db.Column(db.String(200))
    duration_years = db.Column(db.Integer, default=4)

class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    gender = db.Column(db.String(10))
    dob = db.Column(db.Date)
    nationality = db.Column(db.String(60), default="Zambian")
    nrc = db.Column(db.String(30))
    address = db.Column(db.String(255))
    photo = db.Column(db.String(255), default="default.png")
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"))
    year_of_study = db.Column(db.Integer, default=1)
    intake_year = db.Column(db.Integer, default=2026)
    sponsor = db.Column(db.String(120), default="Self")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    program = db.relationship("Program")

    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)
    @property
    def full_name(self): return f"{self.first_name} {self.last_name}"

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(200))
    credits = db.Column(db.Integer, default=3)
    semester = db.Column(db.String(20))
    year_level = db.Column(db.Integer, default=1)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"))
    program = db.relationship("Program")

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))
    ca_mark = db.Column(db.Float)
    exam_mark = db.Column(db.Float)
    grade = db.Column(db.String(5))
    marks_uploaded = db.Column(db.Boolean, default=False)
    academic_year = db.Column(db.String(20))
    semester = db.Column(db.String(20))
    year_level = db.Column(db.Integer, default=1)
    course = db.relationship("Course")

class PaymentTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    date = db.Column(db.Date, default=datetime.utcnow)
    description = db.Column(db.String(200))
    debit = db.Column(db.Float, default=0)
    credit = db.Column(db.Float, default=0)
    reference = db.Column(db.String(80))

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    subject = db.Column(db.String(200))
    category = db.Column(db.String(80))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default="Pending")
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NewsNotice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.Text)
    level = db.Column(db.String(20), default="info")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    active = db.Column(db.Boolean, default=False)

class CourseEvaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    enrollment_id = db.Column(db.Integer, db.ForeignKey("enrollment.id"))
    lecturer_name = db.Column(db.String(120))
    knowledge = db.Column(db.Integer)        # 1-5
    preparedness = db.Column(db.Integer)
    clarity = db.Column(db.Integer)
    punctuality = db.Column(db.Integer)
    engagement = db.Column(db.Integer)
    fairness = db.Column(db.Integer)
    overall = db.Column(db.Integer)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TimetableEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"))
    year_level = db.Column(db.Integer, default=1)
    day = db.Column(db.String(15))      # Monday..Friday
    start_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
    course_code = db.Column(db.String(20))
    course_title = db.Column(db.String(200))
    room = db.Column(db.String(40))
    lecturer = db.Column(db.String(120))
    program = db.relationship("Program")
