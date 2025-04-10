"""initial migration

Revision ID: 9d3144d6774d
Revises: 
Create Date: 2025-04-07 14:01:13.645559

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d3144d6774d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('setting', sa.Column('withdraw_limit', sa.Float(), nullable=False, server_default="5.0"))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('setting', 'withdraw_limit')
    # ### end Alembic commands ###
