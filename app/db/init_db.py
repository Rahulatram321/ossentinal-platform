"""Database initialization entry point for the web process and migrations."""
from core.database import init_db, seed_demo_data


def initialize_database(seed_demo: bool = False) -> None:
    init_db()
    if seed_demo:
        seed_demo_data()
