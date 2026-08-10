from app import create_app
from app.models import User
import re

app = create_app('development')
c = app.test_client()

with app.app_context():
    u = User.query.filter_by(email='diag@example.com').first()
    if not u:
        u = User.query.first()
    print('TEST USER:', u.email)

# ---------- 1. Guest clicks "Choose Pro" ----------
# Fetch pricing page as guest to get CSRF token
page = c.get('/pricing')
html = page.get_data(as_text=True)
m = re.search(r'name="csrf-token" content="([^"]+)"', html)
csrf = m.group(1) if m else ''
print('\n[1] Guest pricing page loaded. CSRF:', bool(csrf))
print('    data-logged-in present:', 'data-logged-in' in html)

# Guest clicks Choose Pro -> select-plan stores pending_plan
r = c.post('/payment/select-plan', json={'plan': 'pro'},
           headers={'X-CSRFToken': csrf, 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'})
print('    select-plan status:', r.status_code, r.get_json())

# ---------- 2. simulate login as the user (pending plan in session persists) ----------
# We re-use the same client so the session cookie carries pending_plan
login_page = c.get('/auth/login')
lhtml = login_page.get_data(as_text=True)
lm = re.search(r'name="csrf-token" content="([^"]+)"', lhtml)
lcsrf = lm.group(1) if lm else ''
# find the form csrf hidden field
fm = re.search(r'name="csrf_token" value="([^"]+)"', lhtml)
form_csrf = fm.group(1) if fm else ''
print('\n[2] Login page loaded. CSRF:', bool(lcsrf), 'form_csrf:', bool(form_csrf))

r = c.post('/auth/login', data={'email': u.email, 'password': 'password123', 'csrf_token': form_csrf, 'remember': 'y'}, follow_redirects=False)
print('    login status:', r.status_code, 'final_location:', r.headers.get('Location'))

# If login redirects to /pricing (pending plan), that confirms plan preservation
loc = r.headers.get('Location', '')
print('    redirects to pricing (plan preserved):', loc.endswith('/pricing'))

# ---------- 3. On pricing page, auto-resume via clear-plan returns pending_plan ----------
# Load pricing now authenticated
r = c.get('/pricing')
html2 = r.get_data(as_text=True)
m2 = re.search(r'name="csrf-token" content="([^"]+)"', html2)
csrf2 = m2.group(1) if m2 else ''
print('\n[3] Authenticated pricing page. data-logged-in=true present:', 'data-logged-in="true"' in html2)

# clear-plan returns the pending plan and clears it (auto-resume call)
r = c.post('/payment/clear-plan', json={},
           headers={'X-CSRFToken': csrf2, 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'})
print('    clear-plan (auto-resume read):', r.status_code, r.get_json())

# ---------- 4. Now create-order for the resumed plan ----------
r = c.post('/payment/create-order', json={'plan': 'pro'},
           headers={'X-CSRFToken': csrf2, 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'})
body = r.get_json()
print('\n[4] create-order (auto-resumed):', r.status_code, '| order_id:', body.get('order_id') if body else None, '| key_id:', 'present' if body and body.get('key_id') else 'MISSING')

# ---------- 5. clear-plan again should return None (already cleared) ----------
r = c.post('/payment/clear-plan', json={},
           headers={'X-CSRFToken': csrf2, 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'})
print('\n[5] clear-plan again (should be None):', r.status_code, r.get_json())
