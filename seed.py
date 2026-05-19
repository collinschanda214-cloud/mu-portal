from datetime import date
from app import create_app, db
from app.models import (Student, Program, Course, Enrollment, PaymentTransaction,
                        NewsNotice, Semester, TimetableEntry)

app = create_app()
with app.app_context():
    db.drop_all(); db.create_all()

    progs = [
        Program(code="BCS",    name="Bachelor of Computer Science",       mode="Fulltime",     school="School of Science, Engineering & Technology", duration_years=4),
        Program(code="BIT",    name="Bachelor of Information Technology", mode="Fulltime",     school="School of Science, Engineering & Technology", duration_years=4),
        Program(code="BBA",    name="Bachelor of Business Administration",mode="Fulltime",     school="School of Business Studies",                  duration_years=4),
        Program(code="BED",    name="Bachelor of Education (Distance)",   mode="Distance",     school="School of Education",                         duration_years=4),
        Program(code="MSC-CS", name="MSc in Computer Science",            mode="Postgraduate", school="School of Postgraduate Studies",              duration_years=2),
    ]
    db.session.add_all(progs); db.session.commit()
    bcs = Program.query.filter_by(code="BCS").first()

    s = Student(
        student_number="20262020",
        first_name="Collins", last_name="Chanda",
        email="collins.chanda@stu.mu.ac.zm", phone="+260 977 123456",
        gender="Male", dob=date(2002,5,14), nationality="Zambian",
        nrc="123456/78/1", address="Plot 22, Kabwe, Zambia",
        program_id=bcs.id, year_of_study=3, intake_year=2024, sponsor="Self",
    )
    s.set_password("pa55w")  # exactly 5 chars
    db.session.add(s); db.session.commit()

    # Courses across years/semesters for BCS
    # (code, title, credits, semester, year_level)
    # Year level inferred from 2nd char of code number; semester from 3rd char (odd=S1, even=S2)
    _raw_courses = [
        ("BIO111","Bio-molecules and Cells"),
        ("PHY101","Fundamentals of Physics"),
        ("MSM111","Mathematical Methods I"),
        ("CHE111","Introductory Chemistry"),
        ("CHE112","Introductory Chemistry II"),
        ("PHY102","Introductory Physics II"),
        ("MSM112","Mathematical Methods II"),
        ("BIO112","Molecular Biology and Genetics"),
        ("BMG101","Ethics and Sustainable Behaviour in Society"),
        ("ICT261","Introduction to Object Oriented Programming and JAVA"),
        ("ICT221","Computer Architecture"),
        ("ICT241","Digital Design"),
        ("ICT201","Discrete Mathematics"),
        ("ICT402","Statistics and Empirical Methods for Computing"),
        ("ICT242","Networking and Communication"),
        ("ICT262","Intermediate Java Programming"),
        ("ICT271","Databases"),
        ("ICT222","Operating Systems"),
        ("ICT341","Computer Security"),
        ("ICT361","Mobile Application programming"),
        ("ICT351","Theory of Computation"),
        ("ICT381","Modelling and System Design"),
        ("ICT372","Advanced Databases"),
        ("ICT202","Data Structures and Algorithms"),
        ("ICT281","Statistics and Empirical Methods for Computing"),
        ("ICT312","Fundamentals of Compilers"),
        ("ICT382","Software Engineering"),
        ("ICT332","Generative AI & Large Language Models"),
        ("ICS372","Network Security and Firewalls"),
        ("ICD322","Visualization and Data Analytics"),
    ]
    _yl_to_ay = {1:"2022-", 2:"2023-", 3:"2024-", 4:"2025-"}
    courses_data = []
    for code, title in _raw_courses:
        yl = int(code[3])
        sem = "S2" if int(code[5]) % 2 == 0 else "S1"
        courses_data.append((code, title, 3, f"{_yl_to_ay[yl][:-1]}-{sem}", yl))
    courses = []
    for code,title,cr,sem,yl in courses_data:
        c = Course(code=code, title=title, credits=cr, semester=sem,
                   year_level=yl, program_id=bcs.id)
        courses.append(c)
    db.session.add_all(courses); db.session.commit()

    # NOTE: Do NOT auto-enroll the student. Enrollments are created only
    # when the student selects and submits courses on the Course Registration
    # page. Personal Information and Course Evaluation will then display
    # only those self-registered courses.

    txns = [
        PaymentTransaction(student_id=s.id, date=date(2024,1,15), description="Tuition Fees - Semester 1", debit=12500, reference="INV-2024-001"),
        PaymentTransaction(student_id=s.id, date=date(2024,2,10), description="Payment Received - Zanaco", credit=8000,  reference="ZNB-998877"),
        PaymentTransaction(student_id=s.id, date=date(2024,3,5),  description="Library Fee",               debit=250,   reference="LIB-24"),
        PaymentTransaction(student_id=s.id, date=date(2024,7,1),  description="Tuition Fees - Semester 2", debit=12500, reference="INV-2024-002"),
        PaymentTransaction(student_id=s.id, date=date(2024,8,20), description="Payment Received - FNB",    credit=10000,reference="FNB-554433"),
    ]
    db.session.add_all(txns)

    news = [
        NewsNotice(title="Examination Timetable Released", body="The end of semester examination timetable is now available.", level="success"),
        NewsNotice(title="Outstanding Balance Reminder",   body="Students with outstanding balances will not be allowed to sit for examinations.", level="danger"),
        NewsNotice(title="Course Evaluation Open",         body="Please complete the course evaluation for all registered courses before the deadline.", level="info"),
    ]
    db.session.add_all(news)
    db.session.add(Semester(name="2024 Semester 2", active=True))

    # Sample timetable for BCS Year 3, Semester 1
    tt = [
        ("Monday",   "08:00","10:00","CSC3010","Software Engineering","LT1","Dr. Mwansa"),
        ("Monday",   "11:00","13:00","CSC3020","Database Systems",    "LAB2","Mrs. Phiri"),
        ("Tuesday",  "08:00","10:00","CSC3030","Operating Systems",   "LT3","Mr. Banda"),
        ("Wednesday","10:00","12:00","CSC3010","Software Engineering","LT1","Dr. Mwansa"),
        ("Thursday", "14:00","16:00","CSC3020","Database Systems",    "LAB2","Mrs. Phiri"),
        ("Friday",   "08:00","10:00","CSC3030","Operating Systems",   "LT3","Mr. Banda"),
    ]
    for d,st,et,cc,ct,rm,lec in tt:
        db.session.add(TimetableEntry(program_id=bcs.id, year_level=3,
            day=d, start_time=st, end_time=et,
            course_code=cc, course_title=ct, room=rm, lecturer=lec))

    # Year 1 BCS sample timetable
    tt1 = [
        ("Monday",   "08:00","10:00","CSC1010","Intro to Computing","LT2","Mr. Tembo"),
        ("Tuesday",  "10:00","12:00","MAT1010","Calculus I",        "LT4","Dr. Sakala"),
        ("Wednesday","08:00","10:00","CSC1020","Programming Fundamentals","LAB1","Ms. Zulu"),
        ("Thursday", "11:00","13:00","MAT1020","Discrete Mathematics","LT4","Dr. Sakala"),
    ]
    for d,st,et,cc,ct,rm,lec in tt1:
        db.session.add(TimetableEntry(program_id=bcs.id, year_level=1,
            day=d, start_time=st, end_time=et,
            course_code=cc, course_title=ct, room=rm, lecturer=lec))

    db.session.commit()
    print("Seeded. Login -> 20262020 / pa55w")
