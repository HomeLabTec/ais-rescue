# Data Collector + Admin (Flask + SQLite)

This is a Flask app you can run on Linux that collects form submissions into a SQLite database and provides an admin interface to review and export the data.

## Data collected

- **UID** (required)
- **S Level** (required)
- Missed Salary Amount (optional)
- Did you rent more than 2 YY bots? (yes/no)
- Are you owed any tickets for renting Fortibots? (yes/no)
  - If yes, a Ticket Amount field appears and becomes required
- **Subsidy Bots ONLY** (required: at least 1)
  - Bot name + Subsidy amount per row
  - Add up to 100 total rows (1 initial + up to 99 more)

## Quickstart

```bash
cd data-collector-admin
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# optional but recommended
cp .env.example .env

# initialize database
flask --app run.py init-db

# create an admin user
flask --app run.py create-admin --username admin

# run
flask --app run.py run --host 0.0.0.0 --port 5000
```

Open:
- Public form: `http://SERVER:5000/`
- Admin: `http://SERVER:5000/admin/`

## Production (example)

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 wsgi:app
```

## CSV exports (admin only)

- `/admin/export/submissions.csv` – one row per submission
- `/admin/export/bots.csv` – one row per bot (submission_id + bot + amount)
- `/admin/export/flat.csv` – one row per bot with the submission columns repeated (easy for pivot tables)
