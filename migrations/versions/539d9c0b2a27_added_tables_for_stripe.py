"""Added Tables for Stripe

Revision ID: 539d9c0b2a27
Revises: 0d67de567f54
Create Date: 2018-07-04 13:23:47.039284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '539d9c0b2a27'
down_revision = '0d67de567f54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Payments',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('PaymentReference', sa.String(length=50), nullable=True),
    sa.Column('BookingReference', sa.String(length=50), nullable=True),
    sa.Column('PaymentFor', sa.String(length=50), nullable=True),
    sa.Column('StripeCustomer', sa.Integer(), nullable=True),
    sa.Column('StripChargeId', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['StripeCustomer'], ['StripeCustomers.Id'], ),
    sa.PrimaryKeyConstraint('Id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Payments')
    # ### end Alembic commands ###
