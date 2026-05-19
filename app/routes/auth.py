import random, string
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app import db
from app.models import Student, Program
from app.forms import LoginForm, RegisterForm
from app.utils_notify import send_credentials

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        s = Student.query.filter_by(student_number=form.student_number.data.strip()).first()
        if s and s.check_password(form.password.data):
            login_user(s)
            return redirect(url_for("main.home"))
        flash("Invalid student number or password", "danger")
    return render_template("login.html", form=form)

def _generate_student_number():
    """Format: 2026#### (year + 4 digits). Ensure uniqueness."""
    year = datetime.utcnow().year
    for _ in range(50):
        num = f"{year}{random.randint(1000, 9999)}"
        if not Student.query.filter_by(student_number=num).first():
            return num
    raise RuntimeError("Could not generate unique student number")

def _generate_password():
    """Exactly 5 chars, letters + numbers only."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=5))

@auth_bp.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    form.program_id.choices = [(p.id, f"{p.code} — {p.name}") for p in Program.query.order_by(Program.name).all()]
    if form.validate_on_submit():
        student_no = _generate_student_number()
        plain_pw   = _generate_password()
        s = Student(
            student_number=student_no,
            first_name=form.first_name.data, last_name=form.last_name.data,
            email=form.email.data, phone=form.phone.data,
            gender=form.gender.data, dob=form.dob.data, nrc=form.nrc.data,
            address=form.address.data, program_id=form.program_id.data,
            year_of_study=1, intake_year=datetime.utcnow().year,
        )
        s.set_password(plain_pw)
        db.session.add(s); db.session.commit()
        email_ok, sms_ok = send_credentials(s.email, s.phone, student_no, plain_pw)
        return render_template("register_success.html",
                               student_number=student_no, password=plain_pw,
                               email_ok=email_ok, sms_ok=sms_ok,
                               email_to=s.email, phone_to=s.phone)
    return render_template("register.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
