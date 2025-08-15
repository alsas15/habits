from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Time, Boolean, Date, ForeignKey, DateTime, UniqueConstraint

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    time_of_day = Column(Time, nullable=False)
    days = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_notified = Column(Date, nullable=True)
    user = relationship("User", backref="habits")

class Completion(Base):
    __tablename__ = "completions"
    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    __table_args__ = (UniqueConstraint('habit_id', 'date', name='uq_habit_date'),)
