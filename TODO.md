# Razorpay Payment Integration - TODO

## Backend
- [x] Inspect project structure, routes, models, config, requirements
- [x] Add `razorpay` to requirements.txt
- [x] Add `load_dotenv()` + Razorpay config to config.py
- [x] Create `app/models/payment.py` (Payment model)
- [x] Add `plan`/`plan_expires_at` to User model
- [x] Import Payment in `app/models/__init__.py`
- [x] Create `app/blueprints/payment.py` (create-order + verify)
- [x] Register `payment_bp` in `app/__init__.py`

## Frontend
- [x] Wire Pro button in `app/templates/main/pricing.html`
- [x] Create `app/static/js/payment.js`

## Environment
- [x] Create `.env` + `.env.example`
- [x] Create `.gitignore` (exclude .env, venv, etc.)

## Database
- [x] Run `migrate_plan.py` to add plan columns to existing users table

## Install & Test
- [x] Install razorpay SDK
- [x] Verify app starts & pricing page renders
