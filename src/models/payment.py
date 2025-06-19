from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

from src.repository.database import db


class Payment(db.Model):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[float] = mapped_column()
    paid: Mapped[bool] = mapped_column(default=False)
    bank_payment_id: Mapped[int] = mapped_column(nullable=True)
    qr_code: Mapped[str] = mapped_column(nullable=True)
    payment_date: Mapped[datetime] = mapped_column(nullable=True)
    expiration_date: Mapped[datetime] = mapped_column(nullable=True)
