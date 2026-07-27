SCHEMA = """
        PRAGMA foreign_keys = ON;

        CREATE TABLE users (
            user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            version INTEGER NOT NULL,
            disabled INTEGER NOT NULL
        );

        CREATE TABLE sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            token_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            version INTEGER NOT NULL,
            revoked INTEGER NOT NULL,
            FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE
        );

        CREATE INDEX idx_sessions_user_id
        ON sessions(user_id);
    """
