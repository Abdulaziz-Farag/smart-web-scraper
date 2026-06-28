-- Smart Web Scraper Database Schema

CREATE TABLE IF NOT EXISTS scraped_data (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url         TEXT,
    table_name  TEXT NOT NULL,
    data        TEXT NOT NULL,
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scrape_sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url         TEXT NOT NULL,
    total_items INTEGER DEFAULT 0,
    status      TEXT DEFAULT 'running',
    started_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_table_name ON scraped_data(table_name);
CREATE INDEX IF NOT EXISTS idx_created_at ON scraped_data(created_at);
