CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    med_status TEXT NOT NULL DEFAULT 'active',
    photo_path TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (med_status IN ('active', 'paused', 'completed')),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medication_id INTEGER NOT NULL,
    scheduled_date TEXT NOT NULL,
    scheduled_time TEXT NOT NULL,
    frequency TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    reminder_status TEXT NOT NULL DEFAULT 'enabled',
    status TEXT NOT NULL DEFAULT 'pending',
    last_taken_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (frequency IN ('daily', 'weekly', 'as-needed', 'one-time')),
    CHECK (reminder_status IN ('enabled', 'disabled')),
    CHECK (status IN ('pending', 'taken', 'skipped')),
    FOREIGN KEY (medication_id) REFERENCES medications (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reminder_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER NOT NULL,
    medication_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    scheduled_date TEXT NOT NULL,
    scheduled_time TEXT NOT NULL,
    action_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    CHECK (action IN ('taken', 'skipped')),
    FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE,
    FOREIGN KEY (medication_id) REFERENCES medications (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notification_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    medication_id INTEGER NOT NULL,
    schedule_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    message TEXT NOT NULL,
    scheduled_date TEXT NOT NULL,
    scheduled_time TEXT NOT NULL,
    sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (type IN ('email', 'push')),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (medication_id) REFERENCES medications (id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES schedules (id) ON DELETE CASCADE,
    UNIQUE (schedule_id, type, scheduled_date, scheduled_time)
);
