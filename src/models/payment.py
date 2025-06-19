from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

from src.repository.database import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[float] = mapped_column()
    paid: Mapped[bool] = mapped_column(default=False)
    bank_payment_id: Mapped[str] = mapped_column(nullable=True)
    qr_code: Mapped[str] = mapped_column(nullable=True)
    payment_date: Mapped[datetime] = mapped_column(nullable=True)
    expiration_date: Mapped[datetime] = mapped_column(nullable=True)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'value': self.value,
            'paid': self.paid,
            'bank_payment_id': self.bank_payment_id,
            'qr_code': self.qr_code,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None
        }
