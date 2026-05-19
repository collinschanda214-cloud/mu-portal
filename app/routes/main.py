from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import NewsNotice

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return redirect(url_for("auth.login"))

@main_bp.route("/home")
@login_required
def home():
    news = NewsNotice.query.order_by(NewsNotice.created_at.desc()).all()
    return render_template("home.html", news=news, user=current_user)
