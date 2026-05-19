from datetime import datetime
import os
from collections import defaultdict
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import (Program, Course, Enrollment, PaymentTransaction,
                        Ticket, CourseEvaluation, TimetableEntry)
from app.forms import TicketForm, PasswordForm, EvaluationForm

student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.route("/personal", methods=["GET","POST"])
@login_required
def personal():
    if request.method == "POST" and "photo" in request.files:
        f = request.files["photo"]
        if f and f.filename:
            fname = secure_filename(f"{current_user.student_number}_{f.filename}")
            f.save(os.path.join(current_app.config["UPLOAD_FOLDER"], fname))
            current_user.photo = fname
            db.session.commit()
            flash("Photo updated.", "success")
        return redirect(url_for("student.personal"))

    # Course progression — group enrollments by year_level then semester
    enrolls = Enrollment.query.filter_by(student_id=current_user.id).all()
    progression = defaultdict(lambda: defaultdict(list))
    for e in enrolls:
        progression[e.year_level or 1][e.semester or "—"].append(e)
    progression = {y: dict(sems) for y, sems in sorted(progression.items())}
    return render_template("personal.html", s=current_user, progression=progression)

@student_bp.route("/timetable")
@login_required
def timetable():
    programs = Program.query.all()
    return render_template("timetable.html", programs=programs)

@student_bp.route("/timetable/<int:program_id>/<int:year>")
@login_required
def timetable_view(program_id, year):
    program = Program.query.get_or_404(program_id)
    entries = TimetableEntry.query.filter_by(program_id=program_id, year_level=year)\
              .order_by(TimetableEntry.day, TimetableEntry.start_time).all()
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
    by_day = {d: [e for e in entries if e.day == d] for d in days}
    return render_template("timetable_view.html", program=program, year=year,
                           by_day=by_day, days=days)

@student_bp.route("/payments")
@login_required
def payments():
    txns = PaymentTransaction.query.filter_by(student_id=current_user.id).order_by(PaymentTransaction.date).all()
    total_debit  = sum(t.debit  or 0 for t in txns)
    total_credit = sum(t.credit or 0 for t in txns)
    balance = total_debit - total_credit
    status = "Fully Paid" if balance <= 0 else ("Partially Paid" if total_credit > 0 else "Outstanding")
    return render_template("payments.html", txns=txns, balance=balance,
                           total_debit=total_debit, total_credit=total_credit,
                           status=status)

@student_bp.route("/helpdesk", methods=["GET","POST"])
@login_required
def helpdesk():
    form = TicketForm()
    if form.validate_on_submit():
        t = Ticket(student_id=current_user.id, subject=form.subject.data,
                   category=form.category.data, message=form.message.data)
        db.session.add(t); db.session.commit()
        flash("Ticket submitted.", "success")
        return redirect(url_for("student.helpdesk"))
    pending = Ticket.query.filter_by(student_id=current_user.id, status="Pending").all()
    completed = Ticket.query.filter_by(student_id=current_user.id, status="Completed").all()
    return render_template("helpdesk.html", form=form, pending=pending, completed=completed)

@student_bp.route("/grades")
@login_required
def grades():
    enrolls = Enrollment.query.filter_by(student_id=current_user.id).all()
    if not enrolls:
        return render_template("grades.html", state="none", enrolls=[])
    uploaded = [e for e in enrolls if e.marks_uploaded]
    if not uploaded:
        return render_template("grades.html", state="none", enrolls=enrolls)
    if len(uploaded) < len(enrolls):
        return render_template("grades.html", state="partial", enrolls=uploaded)
    return render_template("grades.html", state="ok", enrolls=uploaded)

@student_bp.route("/evaluation")
@login_required
def evaluation():
    enrolls = Enrollment.query.filter_by(student_id=current_user.id).all()
    done_ids = {e.enrollment_id for e in CourseEvaluation.query.filter_by(student_id=current_user.id).all()}
    return render_template("evaluation.html", enrolls=enrolls, done_ids=done_ids)

@student_bp.route("/evaluation/<int:enrollment_id>", methods=["GET","POST"])
@login_required
def evaluate_course(enrollment_id):
    e = Enrollment.query.get_or_404(enrollment_id)
    if e.student_id != current_user.id:
        abort(403)
    if CourseEvaluation.query.filter_by(student_id=current_user.id, enrollment_id=e.id).first():
        flash("You have already evaluated this course.", "info")
        return redirect(url_for("student.evaluation"))
    form = EvaluationForm()
    if form.validate_on_submit():
        ev = CourseEvaluation(
            student_id=current_user.id, enrollment_id=e.id,
            lecturer_name=form.lecturer_name.data,
            knowledge=form.knowledge.data, preparedness=form.preparedness.data,
            clarity=form.clarity.data, punctuality=form.punctuality.data,
            engagement=form.engagement.data, fairness=form.fairness.data,
            overall=form.overall.data, comments=form.comments.data,
        )
        db.session.add(ev); db.session.commit()
        flash("Thank you — your evaluation has been submitted.", "success")
        return redirect(url_for("student.evaluation"))
    return render_template("evaluate_form.html", form=form, enrollment=e)

@student_bp.route("/registration", methods=["GET","POST"])
@login_required
def registration():
    # Student picks the year level and semester they want to register for.
    sel_year = request.values.get("year_level", type=int)
    sel_sem = request.values.get("semester", type=str)

    if request.method == "POST":
        selected_ids = request.form.getlist("course_ids")
        academic_year = request.form.get("academic_year") or f"{datetime.utcnow().year}/{datetime.utcnow().year+1}"
        if not selected_ids:
            flash("Please select at least one course to register.", "warning")
            return redirect(url_for("student.registration", year_level=sel_year, semester=sel_sem))
        added = 0
        for cid in selected_ids:
            try: cid = int(cid)
            except: continue
            c = Course.query.get(cid)
            if not c:
                continue
            exists = Enrollment.query.filter_by(student_id=current_user.id, course_id=c.id).first()
            if exists:
                continue
            e = Enrollment(
                student_id=current_user.id, course_id=c.id,
                academic_year=academic_year,
                semester=sel_sem or c.semester,
                year_level=sel_year or c.year_level or 1,
                marks_uploaded=False,
            )
            db.session.add(e); added += 1
        db.session.commit()
        if added:
            flash(f"Registered {added} course(s) successfully.", "success")
        else:
            flash("No new courses registered.", "info")
        return redirect(url_for("student.personal"))

    # Filter the available list by the chosen year level and semester (if any)
    q = Course.query
    if sel_year:
        q = q.filter(Course.year_level == sel_year)
    if sel_sem:
        q = q.filter(Course.semester == sel_sem)
    courses = q.order_by(Course.year_level, Course.semester, Course.code).all()

    # Year levels: support up to 4 even if no courses are seeded yet.
    db_years = {c.year_level for c in Course.query.all() if c.year_level}
    year_options = sorted(db_years | {1, 2, 3, 4})

    # Build semester options with the academic year embedded in the label.
    # Year 1 -> Sem1 = 2025/2026, Sem2 = 2026/2027.
    # Each subsequent year level advances by 2 academic years.
    BASE_YEAR = 2025
    sem_options = []
    if sel_year:
        start = BASE_YEAR + (int(sel_year) - 1) * 2
        sem_options = [
            ("Semester 1", f"Semester 1 ({start}/{start+1})",   f"{start}/{start+1}"),
            ("Semester 2", f"Semester 2 ({start+1}/{start+2})", f"{start+1}/{start+2}"),
        ]
    # Academic year derived from the chosen semester
    academic_year = ""
    for value, _label, ay in sem_options:
        if sel_sem == value:
            academic_year = ay
            break

    registered_ids = {e.course_id for e in Enrollment.query.filter_by(student_id=current_user.id).all()}
    return render_template(
        "registration.html",
        courses=courses, registered_ids=registered_ids,
        sel_year=sel_year, sel_sem=sel_sem,
        year_options=year_options, sem_options=sem_options,
        academic_year=academic_year,
    )

@student_bp.route("/accommodation")
@login_required
def accommodation():
    return render_template("accommodation.html")

@student_bp.route("/password", methods=["GET","POST"])
@login_required
def password():
    form = PasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new.data)
            db.session.commit()
            flash("Password updated.", "success")
            return redirect(url_for("main.home"))
    return render_template("password.html", form=form)
