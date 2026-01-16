from __future__ import annotations

from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import BooleanField, DecimalField, FieldList, FormField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError, NumberRange


class BotEntryForm(FlaskForm):
    class Meta:
        csrf = False

    bot_name = StringField("Bot name", validators=[Optional(), Length(max=128)])
    subsidy_amount = DecimalField(
        "Subsidy amount",
        places=2,
        rounding=None,
        validators=[Optional(), NumberRange(min=0, message="Amount must be 0 or greater")],
    )


class PublicSubmissionForm(FlaskForm):
    uid = StringField("UID", validators=[DataRequired(), Length(max=128)])
    s_level = StringField("S Level", validators=[DataRequired(), Length(max=32)])

    missed_salary_amount = DecimalField(
        "Missed Salary Amount",
        places=2,
        rounding=None,
        validators=[Optional(), NumberRange(min=0, message="Amount must be 0 or greater")],
    )

    rented_more_than_2_yy_bots = BooleanField("Did you rent more than 2 YY bots?")

    owed_fortibots_tickets = BooleanField("Are you owed any tickets for renting Fortibots?")
    fortibots_ticket_amount = DecimalField(
        "Ticket amount owed",
        places=2,
        rounding=None,
        validators=[Optional(), NumberRange(min=0, message="Amount must be 0 or greater")],
    )

    subsidy_bots = FieldList(FormField(BotEntryForm), min_entries=1, max_entries=100)

    submit = SubmitField("Submit")

    def validate_fortibots_ticket_amount(self, field):
        if self.owed_fortibots_tickets.data:
            if field.data is None:
                raise ValidationError("Ticket amount is required when Fortibots tickets are owed.")

    def validate_subsidy_bots(self, field):
        any_bot = False
        errors = False

        for entry in field.entries:
            name = (entry.form.bot_name.data or "").strip()
            amt = entry.form.subsidy_amount.data

            if name:
                any_bot = True
                if amt is None:
                    entry.form.subsidy_amount.errors.append("Amount is required when a bot name is entered.")
                    errors = True
            else:
                # if they typed an amount but no name, that's also invalid
                if amt is not None:
                    entry.form.bot_name.errors.append("Bot name is required when an amount is entered.")
                    errors = True

        if not any_bot:
            raise ValidationError("At least one Subsidy Bot is required.")

        if errors:
            raise ValidationError("Please fix the Subsidy Bots section.")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=64)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=256)])
    submit = SubmitField("Sign in")
