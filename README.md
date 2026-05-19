# Mulungushi University — MU Portal (Flask)

A Flask-based student portal modeled on the MU Portal.

## Features
- Login (existing students) and **Registration** (auto-generates `YYYY####` student number + 5-character alphanumeric password)
- **Personal Information** with photo upload and **Course Progression** grouped by year and semester
- **CA / Grades** — shows a yellow "missing results, contact lecturer" alert or a red "no results uploaded yet" alert until a lecturer uploads marks
- **Payments** — full financial statement with charges, payments, real-time balance, and status badge (Outstanding / Partially Paid / Fully Paid)
- **Course Evaluation** — students click *Evaluate* and fill in a rating + comments form for the lecturer
- **Timetable** — programs grouped by mode (Fulltime / Distance / Postgraduate), each row has a *SHOW TIMETABLE* button that opens a per-program / per-year weekly schedule
- Helpdesk tickets, accommodation, change password

## Quick start (SQLite, easiest)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export USE_SQLITE=1
python seed.py
python run.py
```
Open http://localhost:5000

Default seeded login: **20262020 / pa55w**

## Using MySQL
Create a database `mu_sis`, then copy `.env.example` to `.env` and set DB_USER / DB_PASS / DB_HOST.
```bash
pip install -r requirements.txt
python seed.py
python run.py
```

## Registration rules
- Student number format: `YYYY` (current year) + 4 random digits, e.g. `20262020`
- Password: exactly 5 characters, letters and numbers only, generated automatically
- The new student number and password are shown ONCE on the success page — save them.
