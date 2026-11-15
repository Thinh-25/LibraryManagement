"""Add token revocation and administrator recovery queue."""
from alembic import op
import sqlalchemy as sa
revision = '0002_auth_accounts'
down_revision = '0001_library_schema'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('nguoi_dung', sa.Column('auth_version', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('nguoi_dung', sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table('password_reset_request',
        sa.Column('id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('nguoi_dung_id', sa.BigInteger(), sa.ForeignKey('nguoi_dung.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('trang_thai', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('ngay_tao', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('ngay_xu_ly', sa.DateTime(timezone=True)),
        sa.Column('admin_id', sa.BigInteger(), sa.ForeignKey('nguoi_dung.id', ondelete='RESTRICT')),
        sa.CheckConstraint("trang_thai IN ('PENDING','RESOLVED','REJECTED')", name='reset_status'))
    op.create_index('uq_pending_password_reset', 'password_reset_request', ['nguoi_dung_id'], unique=True, postgresql_where=sa.text("trang_thai = 'PENDING'"))


def downgrade():
    raise RuntimeError('Destructive rollback requires manual review.')
