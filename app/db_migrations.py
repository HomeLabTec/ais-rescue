from __future__ import annotations

from sqlalchemy import inspect, text

from . import db


def ensure_schema() -> None:
    inspector = inspect(db.engine)
    if "submissions" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("submissions")}
    alterations: list[str] = []

    if "owed_yy_bots" not in columns:
        alterations.append(
            "ALTER TABLE submissions ADD COLUMN owed_yy_bots BOOLEAN NOT NULL DEFAULT 0"
        )
    if "owed_fortibots_tickets" not in columns:
        alterations.append(
            "ALTER TABLE submissions ADD COLUMN owed_fortibots_tickets BOOLEAN NOT NULL DEFAULT 0"
        )
    if "fortibots_ticket_amount" not in columns:
        alterations.append(
            "ALTER TABLE submissions ADD COLUMN fortibots_ticket_amount NUMERIC(12, 2)"
        )

    for statement in alterations:
        db.session.execute(text(statement))

    if alterations:
        db.session.commit()
