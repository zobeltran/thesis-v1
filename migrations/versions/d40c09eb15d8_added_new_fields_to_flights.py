"""Added new fields to flights

Revision ID: d40c09eb15d8
Revises: 2933b661a9d9
Create Date: 2018-07-02 17:15:28.177396

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd40c09eb15d8'
down_revision = '2933b661a9d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('package',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('Destination', sa.String(length=50), nullable=True),
    sa.Column('Price', sa.Integer(), nullable=True),
    sa.Column('DaysOfStay', sa.Integer(), nullable=True),
    sa.Column('DepartureDate', sa.Date(), nullable=True),
    sa.Column('DepartureTime', sa.Time(), nullable=True),
    sa.Column('ReturnDate', sa.Date(), nullable=True),
    sa.Column('ReturnTime', sa.Time(), nullable=True),
    sa.Column('Intenerary', sa.String(length=1000), nullable=True),
    sa.Column('Inclusions', sa.String(length=1000), nullable=True),
    sa.Column('RemainingSlots', sa.Integer(), nullable=True),
    sa.Column('ExpirationDate', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('Id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('package')
    # ### end Alembic commands ###
