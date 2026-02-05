"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-04 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Use SQLAlchemy metadata to create all tables
    from models import Base
    conn = op.get_bind()
    Base.metadata.create_all(bind=conn)


def downgrade():
    from models import Base
    conn = op.get_bind()
    Base.metadata.drop_all(bind=conn)
