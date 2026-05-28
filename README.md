# LifeOS — A Calm Productivity & Life-Tracking App

LifeOS is a mobile-first productivity application built with **Django + PostgreSQL**.
It brings your daily routine, expenses, and health tracking into one calm, intentional
dashboard. The design uses a soft sage-green, beige, and cream palette with rounded
cards and a fixed bottom navigation — optimised for phones first.

> Built with Django 5, Bootstrap 5 (utilities only), vanilla JavaScript, Chart.js,
> Lucide icons, and a custom CSS design system.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Quick Start (5 minutes, SQLite)](#quick-start-5-minutes-sqlite)
5. [Full Setup with PostgreSQL](#full-setup-with-postgresql)
6. [Environment Variables](#environment-variables)
7. [Migrations Guide](#migrations-guide)
8. [Running & Testing Each Module](#running--testing-each-module)
9. [Deploying to Render](#deploying-to-render)
10. [Pushing to GitHub](#pushing-to-github)
11. [Troubleshooting](#troubleshooting)

---

## Features

**Dashboard** — the central life-overview page: greeting, daily intention, quick-add
buttons, today's routine progress ring, study time, spending, integrated health widgets
(sleep, meals, hydration with live quick-add, and a weight summary), a weekly-focus bar
chart, and an upcoming list.

**Daily Routine Tracker** — a vertical timeline with add / edit / delete, categories
(Work, Study, Coding, Reading, Household, Personal, Health), completion toggling
(live, no reload), priority flags, notes, plus mood and energy logging.

**Expense Tracker** — income and expenses, total balance, monthly net, per-category
spending summaries with budget bars, and recent transaction history (including who sent money).

**Profile** — personal goals (monthly budget, sleep, water, routine %, health), live
stats (routine %, monthly expenses, streak, consistency), a dark-mode toggle, reminder
settings, and an editable goals form.

> **Note:** Health data (water, sleep, meals, weight) is tracked through quick-log forms
> and surfaced directly on the Dashboard — there is no separate Health Tracker or
> Analytics page in this build.

**Profile** — personal goals (budget, sleep, water, routine %, health), live stats
(routine %, monthly expenses, streak, consistency), a dark-mode toggle, and an editable
goals form.

**Accounts** — registration, login, logout, and a custom user model that stores all
per-user goals and preferences.

---

## Tech Stack

| Layer        | Technology                                  |
|--------------|---------------------------------------------|
| Backend      | Django 5.0                                  |
| Database     | PostgreSQL (SQLite fallback for quick start)|
| Styling      | Custom CSS design system + Bootstrap 5 grid |
| Charts       | Chart.js 4                                  |
| Icons        | Lucide                                      |
| Fonts        | Lora (display) + Manrope (body)             |
| Static files | WhiteNoise (compressed, hashed)             |
| Server       | Gunicorn                                    |
| Config       | python-decouple + dj-database-url           |

---

## Project Structure

```
lifeos/
├── manage.py
├── requirements.txt
├── runtime.txt              # Python version for Render
├── build.sh                 # Render build step
├── render.yaml              # Render Blueprint (web + database)
├── .env.example             # Copy to .env and edit
├── .gitignore
│
├── lifeos/                  # Project config
│   ├── settings.py          # Reads env vars; SQLite fallback
│   ├── urls.py
│   ├── wsgi.py / asgi.py
│
├── accounts/                # Custom User, auth, profile, preferences
│   ├── models.py            # User (holds all goals + prefs)
│   ├── forms.py             # Register / Login / Profile forms
│   ├── views.py
│   ├── context_processors.py# Exposes profile, dark_mode, display_name
│   └── management/commands/seed_data.py
│
├── dashboard/               # Aggregated home screen
├── routines/                # RoutineTask, Category, MoodLog
├── expenses/                # Transaction, ExpenseCategory
├── health/                  # BodyMeasurement, WaterLog, Meal, SleepLog, Workout
│
├── templates/
│   ├── base.html
│   ├── partials/            # bottom_nav, app_header, form_page
│   ├── accounts/            # login, register, profile
│   ├── dashboard/           # home
│   ├── routines/            # list, form, delete, categories
│   ├── expenses/            # tracker, form, list, delete, categories
│   └── health/              # tracker, analytics, 5 log forms
│
└── static/
    ├── css/lifeos.css       # The full design system
    └── js/lifeos.js         # AJAX toggles, dark mode, water add
```

---

## Quick Start (5 minutes, SQLite)

If you just want to see it run, you can skip PostgreSQL entirely. When `DATABASE_URL`
is not set, the app automatically uses a local SQLite file.

```bash
# 1. Clone and enter the project
git clone https://github.com/<your-username>/lifeos.git
cd lifeos

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a minimal .env (SQLite mode — no DATABASE_URL line)
cp .env.example .env
# then open .env and either delete the DATABASE_URL line or comment it out

# 5. Set up the database
python manage.py migrate
python manage.py seed_data --demo   # optional: demo user + sample data

# 6. Run the server
python manage.py runserver
```

Visit **http://127.0.0.1:8000**. If you seeded demo data, log in with:

```
username: alex
password: lifeos123
```

Otherwise click **Create an account** to register.

---

## Full Setup with PostgreSQL

### 1. Install PostgreSQL

- **macOS:** `brew install postgresql@16 && brew services start postgresql@16`
- **Ubuntu/Debian:** `sudo apt update && sudo apt install postgresql postgresql-contrib`
- **Windows:** download the installer from postgresql.org.

### 2. Create the database and user

Open the Postgres shell:

```bash
sudo -u postgres psql      # Linux
# or just: psql postgres   # macOS (Homebrew)
```

Then run:

```sql
CREATE DATABASE lifeos_db;
CREATE USER lifeos_user WITH PASSWORD 'lifeos_pass';

-- Recommended settings for Django
ALTER ROLE lifeos_user SET client_encoding TO 'utf8';
ALTER ROLE lifeos_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE lifeos_user SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE lifeos_db TO lifeos_user;

-- On PostgreSQL 15+, also grant schema rights:
\c lifeos_db
GRANT ALL ON SCHEMA public TO lifeos_user;
\q
```

### 3. Point the app at Postgres

In your `.env` file, set:

```
DATABASE_URL=postgres://lifeos_user:lifeos_pass@localhost:5432/lifeos_db
```

### 4. Migrate, seed, and run

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data --demo
python manage.py createsuperuser     # optional: for /admin
python manage.py runserver
```

---

## Environment Variables

Copy `.env.example` to `.env`. All variables are read by `python-decouple`.

| Variable               | Required | Example                                             | Notes |
|------------------------|----------|-----------------------------------------------------|-------|
| `SECRET_KEY`           | Yes      | `a-long-random-string`                              | See below to generate. |
| `DEBUG`                | Yes      | `True` (dev) / `False` (prod)                       | Never `True` in production. |
| `ALLOWED_HOSTS`        | Yes      | `localhost,127.0.0.1,.onrender.com`                 | Comma-separated. |
| `CSRF_TRUSTED_ORIGINS` | Prod     | `https://*.onrender.com`                            | Needed for HTTPS form posts. |
| `DATABASE_URL`         | No*      | `postgres://user:pass@host:5432/db`                 | Omit to use SQLite. |
| `TIME_ZONE`            | No       | `Asia/Kolkata`                                      | Defaults to `Asia/Kolkata`. |

\* Optional locally (SQLite fallback), **required** in production.

**Generate a secret key:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Migrations Guide

Migrations describe your database schema. The order matters because of the custom
user model.

**First-time setup (fresh database):**

```bash
python manage.py makemigrations        # usually not needed — migrations are committed
python manage.py migrate               # applies everything in dependency order
```

Django applies them in this order automatically:
`contenttypes → auth → accounts (custom User) → admin → expenses → health → routines → sessions`.

**After you change a model** (add/remove a field, etc.):

```bash
python manage.py makemigrations <app_name>
python manage.py migrate
```

**Inspect or undo:**

```bash
python manage.py showmigrations              # see what's applied
python manage.py migrate routines 0001       # roll back routines to migration 0001
python manage.py sqlmigrate expenses 0001    # preview the SQL without running it
```

> **Important:** because LifeOS uses a custom user model (`accounts.User`), the
> `accounts` migration must exist before any app that references the user. The
> committed migrations already respect this, so a plain `migrate` is all you need.

---

## Running & Testing Each Module

Start the server (`python manage.py runserver`) and walk through each screen via the
bottom navigation. The fastest way to populate everything is `seed_data --demo`.

| Module     | URL                | What to test |
|------------|--------------------|--------------|
| Auth       | `/accounts/register/`, `/accounts/login/` | Create an account, log out, log back in. |
| Dashboard  | `/`                | Greeting, task ring, wellness tiles, weekly chart, upcoming list. |
| Routines   | `/routines/`       | Add a task → it appears on the timeline. Tap the circle to complete it (no reload). Pick a mood and energy level. Edit and delete. |
| Expenses   | `/expenses/`       | Add income (with a sender) and an expense. Check the balance updates and category bars fill. Filter the transaction list. Edit and delete. |
| Health     | `/health/...`      | Log weight/waist, sleep, a meal, or water via the quick-log forms — all reachable from the Dashboard. After saving you return to the Dashboard. Tap **Add 250ml** for a live water update. |
| Profile    | `/accounts/profile/`| Edit goals, watch stats recompute, flip the dark-mode switch. |
| Admin      | `/admin/`          | (After `createsuperuser`) inspect every model. |

### Automated smoke test

A full end-to-end test that exercises auth, every page, all CRUD, AJAX endpoints,
dark mode, and the chart pages is included:

```bash
ALLOWED_HOSTS="testserver,localhost,127.0.0.1" python smoke_test.py
```

It prints a pass/fail line per check and exits non-zero if anything fails.
(`smoke_test.py` is git-ignored by default — it's a dev tool, not part of the app.)

---

## Deploying to Render

You have two options. The Blueprint is the easiest.

### Option A — One-click Blueprint (recommended)

The repo includes `render.yaml`, which provisions the web service **and** a free
PostgreSQL database, and links them automatically.

1. Push your code to GitHub (see the next section).
2. On Render: **New + → Blueprint**, then select your repo.
3. Render reads `render.yaml`, creates `lifeos-db` and the `lifeos` web service,
   generates a `SECRET_KEY`, and wires `DATABASE_URL` for you.
4. Click **Apply**. The build runs `build.sh` (install → collectstatic → migrate → seed).
5. When it goes live, open the `.onrender.com` URL.

### Option B — Manual setup

1. **New + → PostgreSQL**, create a free database, and copy its **Internal Database URL**.
2. **New + → Web Service**, connect your repo, and set:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn lifeos.wsgi:application`
3. Add environment variables under the service's **Environment** tab:
   - `SECRET_KEY` — a fresh random string
   - `DEBUG` — `False`
   - `ALLOWED_HOSTS` — `.onrender.com`
   - `CSRF_TRUSTED_ORIGINS` — `https://*.onrender.com`
   - `DATABASE_URL` — paste the Internal Database URL from step 1
4. **Create Web Service.** Render installs, collects static (served by WhiteNoise),
   migrates, and seeds categories on each deploy.

> **Note on the free tier:** free Render web services sleep after inactivity and the
> first request afterward is slow to wake. The free Postgres instance also expires
> after a set period — fine for demos, upgrade for anything permanent.

To create an admin user on Render, open the service **Shell** and run
`python manage.py createsuperuser`.

---

## Pushing to GitHub

```bash
# From the project root, initialise git (skip if already a repo)
git init
git add .
git commit -m "LifeOS: Django + PostgreSQL productivity app"

# Create an empty repo on github.com first (no README/license),
# then connect and push:
git branch -M main
git remote add origin https://github.com/<your-username>/lifeos.git
git push -u origin main
```

`.gitignore` already excludes `.env`, `db.sqlite3`, `/staticfiles/`, `/media/`,
virtual environments, and caches — so your secrets and build artifacts stay out of git.

---

## Troubleshooting

**`DisallowedHost` / `Invalid HTTP_HOST`** — add your host to `ALLOWED_HOSTS` in `.env`.

**`password authentication failed for user "lifeos_user"`** — the credentials in
`DATABASE_URL` don't match what you created in Postgres. Re-check the `CREATE USER` step.

**Static files (CSS) missing in production** — make sure `build.sh` ran
`collectstatic` and that `DEBUG=False` is set. WhiteNoise serves the hashed files
from `staticfiles/`.

**`relation does not exist`** — you haven't migrated. Run `python manage.py migrate`.

**Charts are empty** — that's expected with no data; log some entries or run
`seed_data --demo`.

**CSRF verification failed on Render** — confirm `CSRF_TRUSTED_ORIGINS` includes
`https://*.onrender.com`.

---

Built with care for calm, intentional productivity.
