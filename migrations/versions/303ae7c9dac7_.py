"""empty message

Revision ID: 303ae7c9dac7
Revises: d88e3fd4f24
Create Date: 2016-12-30 15:40:24.492360

"""

# revision identifiers, used by Alembic.
revision = '303ae7c9dac7'
down_revision = 'd88e3fd4f24'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('InstagramResult',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ig_name', sa.String(length=100), nullable=True),
    sa.Column('task_id', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('InstagramResult')
    ### end Alembic commands ###
