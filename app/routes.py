from __future__ import annotations

import csv
from io import StringIO

from flask import Blueprint, flash, redirect, render_template, request, url_for, Response
from flask_login import current_user, login_required, login_user, logout_user

from . import db
from .forms import PublicSubmissionForm, LoginForm
from .models import Submission, SubsidyBot, User, YyBot


public_bp = Blueprint("public", __name__)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@public_bp.route("/", methods=["GET", "POST"])
def index():
    form = PublicSubmissionForm()

    # Ensure at least one bot row exists when first loading
    if request.method == "GET" and len(form.subsidy_bots) == 0:
        form.subsidy_bots.append_entry()

    if form.validate_on_submit():
        existing_submission = Submission.query.filter_by(uid=form.uid.data.strip()).first()
        if existing_submission:
            form.uid.errors.append("UID already exists. Please use a unique UID.")
            return render_template("public_form.html", form=form)

        submission = Submission(
            uid=form.uid.data.strip(),
            s_level=form.s_level.data,
            missed_salary_amount=form.missed_salary_amount.data,
            owed_yy_bots=bool(form.owed_yy_bots.data),
            rented_more_than_2_yy_bots=False,
            owed_fortibots_tickets=bool(form.owed_fortibots_tickets.data),
            fortibots_ticket_amount=form.fortibots_ticket_amount.data,
            pending_withdraws=bool(form.pending_withdraws.data),
            withdraw_dates=", ".join(
                entry.data.isoformat()
                for entry in form.withdraw_dates.entries
                if entry.data is not None
            )
            or None,
        )

        # Add bots (only rows with bot_name)
        for entry in form.subsidy_bots.entries:
            name = (entry.form.bot_name.data or "").strip()
            amt = entry.form.subsidy_amount.data
            if name:
                submission.subsidy_bots.append(SubsidyBot(bot_name=name, subsidy_amount=amt))

        if form.owed_yy_bots.data:
            for entry in form.yy_bots.entries:
                name = (entry.data or "").strip()
                if name:
                    submission.yy_bots.append(YyBot(bot_name=name))

        db.session.add(submission)
        db.session.commit()

        return redirect(url_for("public.thanks"))

    return render_template("public_form.html", form=form)


@public_bp.route("/thanks")
def thanks():
    return render_template("thanks.html")


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("admin.dashboard"))
        flash("Invalid username or password.", "danger")

    return render_template("admin_login.html", form=form)


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


@admin_bp.route("/", methods=["GET"])
@login_required
def dashboard():
    q = (request.args.get("q") or "").strip()

    query = Submission.query
    if q:
        query = query.filter(Submission.uid.ilike(f"%{q}%"))

    submissions = query.order_by(Submission.created_at.desc()).limit(500).all()
    return render_template("admin_dashboard.html", submissions=submissions, q=q)


@admin_bp.route("/submission/<int:submission_id>")
@login_required
def submission_detail(submission_id: int):
    submission = db.session.get(Submission, submission_id)
    if not submission:
        flash("Submission not found.", "warning")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin_detail.html", submission=submission)


@admin_bp.route("/submission/<int:submission_id>/delete", methods=["POST"])
@login_required
def submission_delete(submission_id: int):
    submission = db.session.get(Submission, submission_id)
    if not submission:
        flash("Submission not found.", "warning")
        return redirect(url_for("admin.dashboard"))

    db.session.delete(submission)
    db.session.commit()
    flash("Submission deleted.", "success")
    return redirect(url_for("admin.dashboard"))


def _csv_response(filename: str, rows: list[dict], fieldnames: list[str]) -> Response:
    sio = StringIO()
    writer = csv.DictWriter(sio, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

    output = sio.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )


@admin_bp.route("/export/submissions.csv")
@login_required
def export_submissions_csv():
    submissions = Submission.query.order_by(Submission.created_at.asc()).all()

    rows = []
    for s in submissions:
        rows.append(
            {
                "submission_id": s.id,
                "created_at": s.created_at.isoformat() if s.created_at else "",
                "uid": s.uid,
                "s_level": s.s_level,
                "missed_salary_amount": str(s.missed_salary_amount) if s.missed_salary_amount is not None else "",
                "owed_yy_bots": "yes" if s.owed_yy_bots else "no",
                "yy_bot_count": len(s.yy_bots),
                "yy_bot_names": ", ".join(bot.bot_name for bot in s.yy_bots),
                "owed_fortibots_tickets": "yes" if s.owed_fortibots_tickets else "no",
                "fortibots_ticket_amount": str(s.fortibots_ticket_amount) if s.fortibots_ticket_amount is not None else "",
                "pending_withdraws": "yes" if s.pending_withdraws else "no",
                "withdraw_dates": ", ".join(s.withdraw_dates_list()),
                "bot_count": len(s.subsidy_bots),
            }
        )

    fieldnames = [
        "submission_id",
        "created_at",
        "uid",
        "s_level",
        "missed_salary_amount",
        "owed_yy_bots",
        "yy_bot_count",
        "yy_bot_names",
        "owed_fortibots_tickets",
        "fortibots_ticket_amount",
        "pending_withdraws",
        "withdraw_dates",
        "bot_count",
    ]
    return _csv_response("submissions.csv", rows, fieldnames)


@admin_bp.route("/export/bots.csv")
@login_required
def export_bots_csv():
    bots = SubsidyBot.query.order_by(SubsidyBot.submission_id.asc(), SubsidyBot.id.asc()).all()
    rows = []
    for b in bots:
        rows.append(
            {
                "submission_id": b.submission_id,
                "bot_name": b.bot_name,
                "subsidy_amount": str(b.subsidy_amount),
            }
        )

    fieldnames = ["submission_id", "bot_name", "subsidy_amount"]
    return _csv_response("subsidy_bots.csv", rows, fieldnames)


@admin_bp.route("/export/flat.csv")
@login_required
def export_flat_csv():
    """One row per (submission, bot) to keep the export analyzable in Excel."""
    submissions = Submission.query.order_by(Submission.created_at.asc()).all()
    rows = []
    for s in submissions:
        if not s.subsidy_bots:
            rows.append(
                {
                    "submission_id": s.id,
                    "created_at": s.created_at.isoformat() if s.created_at else "",
                    "uid": s.uid,
                    "s_level": s.s_level,
                    "missed_salary_amount": str(s.missed_salary_amount) if s.missed_salary_amount is not None else "",
                    "owed_yy_bots": "yes" if s.owed_yy_bots else "no",
                    "owed_fortibots_tickets": "yes" if s.owed_fortibots_tickets else "no",
                    "fortibots_ticket_amount": str(s.fortibots_ticket_amount) if s.fortibots_ticket_amount is not None else "",
                    "pending_withdraws": "yes" if s.pending_withdraws else "no",
                    "withdraw_dates": ", ".join(s.withdraw_dates_list()),
                    "yy_bot_names": ", ".join(bot.bot_name for bot in s.yy_bots),
                    "bot_name": "",
                    "yy_bot_name": "",
                    "subsidy_amount": "",
                }
            )
        else:
            for b in s.subsidy_bots:
                rows.append(
                    {
                        "submission_id": s.id,
                        "created_at": s.created_at.isoformat() if s.created_at else "",
                        "uid": s.uid,
                        "s_level": s.s_level,
                        "missed_salary_amount": str(s.missed_salary_amount) if s.missed_salary_amount is not None else "",
                        "owed_yy_bots": "yes" if s.owed_yy_bots else "no",
                        "owed_fortibots_tickets": "yes" if s.owed_fortibots_tickets else "no",
                        "fortibots_ticket_amount": str(s.fortibots_ticket_amount) if s.fortibots_ticket_amount is not None else "",
                        "pending_withdraws": "yes" if s.pending_withdraws else "no",
                        "withdraw_dates": ", ".join(s.withdraw_dates_list()),
                        "yy_bot_names": ", ".join(bot.bot_name for bot in s.yy_bots),
                        "yy_bot_name": "",
                        "bot_name": b.bot_name,
                        "subsidy_amount": str(b.subsidy_amount),
                    }
                )

    fieldnames = [
        "submission_id",
        "created_at",
        "uid",
        "s_level",
        "missed_salary_amount",
        "owed_yy_bots",
        "owed_fortibots_tickets",
        "fortibots_ticket_amount",
        "pending_withdraws",
        "withdraw_dates",
        "yy_bot_names",
        "yy_bot_name",
        "bot_name",
        "subsidy_amount",
    ]
    return _csv_response("submissions_flat.csv", rows, fieldnames)
