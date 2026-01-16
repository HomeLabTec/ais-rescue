from __future__ import annotations

import getpass

import click
from flask import Flask

from . import db
from .db_migrations import ensure_schema
from .models import User


def register_cli(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db():
        """Create database tables."""
        db.create_all()
        ensure_schema()
        click.echo("Database initialized.")

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True)
    def create_admin(username: str):
        """Create an admin user for logging into /admin."""
        username = username.strip()
        existing = User.query.filter_by(username=username).first()
        if existing:
            raise click.ClickException("That username already exists.")

        pw1 = getpass.getpass("Password: ")
        pw2 = getpass.getpass("Confirm Password: ")
        if pw1 != pw2:
            raise click.ClickException("Passwords do not match.")
        if len(pw1) < 8:
            raise click.ClickException("Password must be at least 8 characters.")

        u = User(username=username)
        u.set_password(pw1)
        db.session.add(u)
        db.session.commit()
        click.echo("Admin user created.")

    @app.cli.command("change-password")
    @click.option("--username", prompt=True)
    def change_password(username: str):
        """Change password for an existing admin user."""
        username = username.strip()
        user = User.query.filter_by(username=username).first()
        if not user:
            raise click.ClickException("User not found.")

        pw1 = getpass.getpass("New Password: ")
        pw2 = getpass.getpass("Confirm New Password: ")
        if pw1 != pw2:
            raise click.ClickException("Passwords do not match.")
        if len(pw1) < 8:
            raise click.ClickException("Password must be at least 8 characters.")

        user.set_password(pw1)
        db.session.commit()
        click.echo("Password updated.")
