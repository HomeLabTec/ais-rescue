from __future__ import annotations

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager


@login_manager.user_loader
def load_user(user_id: str):
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)

    uid = db.Column(db.String(128), nullable=False, index=True)
    s_level = db.Column(db.String(32), nullable=False, index=True)

    missed_salary_amount = db.Column(db.Numeric(12, 2), nullable=True)

    rented_more_than_2_yy_bots = db.Column(db.Boolean, nullable=False, default=False)

    owed_fortibots_tickets = db.Column(db.Boolean, nullable=False, default=False)
    fortibots_ticket_amount = db.Column(db.Numeric(12, 2), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    subsidy_bots = db.relationship(
        "SubsidyBot",
        back_populates="submission",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SubsidyBot(db.Model):
    __tablename__ = "subsidy_bots"

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True)

    bot_name = db.Column(db.String(128), nullable=False)
    subsidy_amount = db.Column(db.Numeric(12, 2), nullable=False)

    submission = db.relationship("Submission", back_populates="subsidy_bots")
