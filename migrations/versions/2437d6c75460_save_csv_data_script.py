"""Save csv data [script]

Revision ID: 2437d6c75460
Revises: f98963bfffd4
Create Date: 2024-05-13 04:13:07.420383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2437d6c75460'
down_revision = 'f98963bfffd4'
branch_labels = None
depends_on = None


def upgrade():
    from app.helpers import load_csv_data
    load_csv_data("app/files/vibra_challenge.csv")


def downgrade():
    pass
