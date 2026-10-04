"""adiciona galeria ordenada de imagens aos produtos

Revision ID: 20261003_0002
Revises: 20260921_0001
"""

from alembic import op
import sqlalchemy as sa


revision = "20261003_0002"
down_revision = "20260921_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("alt_text", sa.String(length=255), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.CheckConstraint("position > 0", name="ck_product_image_position_positive"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "position", name="uq_product_image_position"),
    )
    op.create_index("ix_product_images_product_id", "product_images", ["product_id"], unique=False)

    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TABLE product_images ENABLE ROW LEVEL SECURITY")
        op.execute("REVOKE ALL ON TABLE product_images FROM anon, authenticated")


def downgrade() -> None:
    op.drop_index("ix_product_images_product_id", table_name="product_images")
    op.drop_table("product_images")
