"""adiciona escopo administrativo e dados minimos de acesso

Revision ID: 20261005_0003
Revises: 20261003_0002
"""

from alembic import op
import sqlalchemy as sa


revision = "20261005_0003"
down_revision = "20261003_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("admin_scope", sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column("registration_ip", sa.String(length=45), nullable=True))
        batch_op.add_column(sa.Column("registration_location", sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("last_login_ip", sa.String(length=45), nullable=True))
        batch_op.add_column(sa.Column("last_login_location", sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.create_check_constraint(
            "ck_users_admin_scope",
            "admin_scope IS NULL OR admin_scope IN ('SITE', 'ATHLETICS')",
        )

    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
        op.execute("REVOKE ALL ON TABLE users FROM anon, authenticated")


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("ck_users_admin_scope", type_="check")
        batch_op.drop_column("last_login_at")
        batch_op.drop_column("last_login_location")
        batch_op.drop_column("last_login_ip")
        batch_op.drop_column("registration_location")
        batch_op.drop_column("registration_ip")
        batch_op.drop_column("admin_scope")
