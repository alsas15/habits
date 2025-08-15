from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    telegram_id: str

class HabitCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    time_of_day: str  # HH:MM
    days: Optional[List[int]] = None
    is_active: bool = True

class HabitUpdate(BaseModel):
    title: Optional[str] = None
    time_of_day: Optional[str] = None
    days: Optional[List[int]] = None
    is_active: Optional[bool] = None

class HabitOut(BaseModel):
    id: int
    user_id: int
    title: str
    time_of_day: str
    days: Optional[List[int]]
    is_active: bool

class CompleteIn(BaseModel):
    habit_id: int
    date: Optional[date] = None
    status: str
