"""One-time migration to add plan columns to the existing users table.

Adds 'plan' and 'plan_expires_at' columns to the existing SQLite users table
if they do not already exist. Safe to run multiple times.
"""
import os
import sqlite3


def main():
    db_path = os.path.join('instance', 'app.db')
    if not os.path.exists(db_path):
        print(f'DB not found at {db_path}; skipping users migration.')
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cols = [r[1] for r in cur.execute('PRAGMA table_info(users)').fetchall()]

    if 'plan' not in cols:
        cur.execute("ALTER TABLE users ADD COLUMN plan VARCHAR(20) DEFAULT 'free'")
        print('Added: plan')
    else:
        print('Already present: plan')

    if 'plan_expires_at' not in cols:
        cur.execute('ALTER TABLE users ADD COLUMN plan_expires_at DATETIME')
        print('Added: plan_expires_at')
    else:
        print('Already present: plan_expires_at')

    conn.commit()
    cols_after = [r[1] for r in cur.execute('PRAGMA table_info(users)').fetchall()]
    print('Final users columns:', cols_after)
    conn.close()


if __name__ == '__main__':
    main()

