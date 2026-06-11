"""Admin user management CLI."""
from __future__ import annotations

import click

from server.infrastructure.database import init_db, get_session
from server.infrastructure.models import AdminUser
from server.api.middleware.auth import hash_password


@click.group()
def admin():
    """Manage FIT-OCR admin users."""
    init_db()


@admin.command("create-user")
@click.option("--username", "-u", required=True, help="Admin username")
@click.option("--password", "-p", required=True, help="Admin password")
def create_user(username: str, password: str):
    """Create a new admin user."""
    db = get_session()
    try:
        existing = db.query(AdminUser).filter(AdminUser.username == username).first()
        if existing:
            click.echo(f"User '{username}' already exists.")
            return

        user = AdminUser(username=username, hashed_password=hash_password(password))
        db.add(user)
        db.commit()
        click.echo(f"Admin user '{username}' created.")
    finally:
        db.close()


@admin.command("list-users")
def list_users():
    """List all admin users."""
    db = get_session()
    try:
        users = db.query(AdminUser).all()
        if not users:
            click.echo("No admin users found.")
            return
        for u in users:
            click.echo(f"  {u.username} (created {u.created_at.strftime('%Y-%m-%d')})")
    finally:
        db.close()
