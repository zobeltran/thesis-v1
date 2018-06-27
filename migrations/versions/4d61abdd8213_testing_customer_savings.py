"""Testing Customer Savings

Revision ID: 4d61abdd8213
Revises: 56ffc7f7ae94
Create Date: 2018-06-28 01:35:26.663941

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d61abdd8213'
down_revision = '56ffc7f7ae94'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customer',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('FirstName', sa.String(length=250), nullable=True),
    sa.Column('LastName', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('Id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('customer')
    # ### end Alembic commands ###
