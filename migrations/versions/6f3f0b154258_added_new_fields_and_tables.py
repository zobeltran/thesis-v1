"""Added new Fields and Tables

Revision ID: 6f3f0b154258
Revises: e3dba81d126c
Create Date: 2018-07-03 23:20:42.096981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f3f0b154258'
down_revision = 'e3dba81d126c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('HotelBooking',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('ReferenceNumber', sa.String(length=50), nullable=True),
    sa.Column('CustomersFk', sa.Integer(), nullable=True),
    sa.Column('HotelsFk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['CustomersFk'], ['Customers.Id'], ),
    sa.ForeignKeyConstraint(['HotelsFk'], ['Hotels.Id'], ),
    sa.PrimaryKeyConstraint('Id')
    )
    op.create_table('TicketBooking',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('ReferenceNumber', sa.String(length=50), nullable=True),
    sa.Column('CustomersFk', sa.Integer(), nullable=True),
    sa.Column('FlightFk', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['CustomersFk'], ['Customers.Id'], ),
    sa.ForeignKeyConstraint(['FlightFk'], ['Tickets.Id'], ),
    sa.PrimaryKeyConstraint('Id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('TicketBooking')
    op.drop_table('HotelBooking')
    # ### end Alembic commands ###
