from contextlib import contextmanager
from pathlib import Path
import json, sqlite3, secrets
from build.integration.common import ROOT

DB = ROOT / 'output/deployment/demo.db'

@contextmanager
def connection():
    DB.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DB,timeout=15)
    db.row_factory=sqlite3.Row
    try:
        db.execute('PRAGMA foreign_keys=ON')
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def initialize():
    with connection() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS schema_version(version INTEGER PRIMARY KEY);
        INSERT OR IGNORE INTO schema_version VALUES(1);
        CREATE TABLE IF NOT EXISTS orders(
            id TEXT PRIMARY KEY, service TEXT NOT NULL, quantity REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'received', note TEXT NOT NULL,
            feedback INTEGER, created TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS batches(
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, input_kg REAL NOT NULL,
            output_kg REAL NOT NULL DEFAULT 0, waste_kg REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'received');
        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY, title TEXT NOT NULL, due TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending');
        CREATE TABLE IF NOT EXISTS equipment(
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, state TEXT NOT NULL,
            maintenance_due TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audit(
            id INTEGER PRIMARY KEY, event TEXT NOT NULL, details TEXT NOT NULL,
            created TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS assessments(
            id INTEGER PRIMARY KEY, result TEXT NOT NULL,
            created TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)

def audit(db,event,details):
    db.execute('INSERT INTO audit(event,details) VALUES(?,?)',(event,json.dumps(details)))

def rows(table):
    if table not in {'orders','batches','tasks','equipment','audit','assessments','settings'}:
        raise ValueError('Invalid table')
    with connection() as db:
        return [dict(row) for row in db.execute(f'SELECT * FROM {table} LIMIT 500')]

def create_order(service,quantity,note):
    token=secrets.token_urlsafe(24)
    with connection() as db:
        db.execute('INSERT INTO orders(id,service,quantity,note) VALUES(?,?,?,?)',(token,service,quantity,note))
        audit(db,'order.created',{'service':service,'quantity':quantity})
    return token
