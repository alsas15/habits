from sqlalchemy.orm import Session
from . import models
from datetime import datetime, date
from typing import List, Optional

def get_or_create_user(db: Session, telegram_id: str):
    u = db.query(models.User).filter(models.User.telegram_id == telegram_id).first()
    if u:
        return u
    u = models.User(telegram_id=telegram_id)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def create_habit(db: Session, user: models.User, title: str, time_of_day, days: Optional[List[int]], is_active: bool):
    h = models.Habit(user_id=user.id, title=title, time_of_day=time_of_day, days=','.join(str(d) for d in (days or [])) if days else None, is_active=is_active, created_at=datetime.utcnow())
    db.add(h)
    db.commit()
    db.refresh(h)
    return h

def list_habits(db: Session, user: models.User):
    return db.query(models.Habit).filter(models.Habit.user_id == user.id).all()

def get_habit(db: Session, habit_id: int):
    return db.query(models.Habit).get(habit_id)

def update_habit(db: Session, habit: models.Habit, **data):
    for k, v in data.items():
        if v is not None:
            setattr(habit, k, v)
    db.commit()
    db.refresh(habit)
    return habit

def delete_habit(db: Session, habit: models.Habit):
    db.delete(habit)
    db.commit()

def mark_completion(db: Session, habit_id: int, status: str, day: date):
    c = db.query(models.Completion).filter(models.Completion.habit_id==habit_id, models.Completion.date==day).first()
    if c:
        c.status = status
    else:
        c = models.Completion(habit_id=habit_id, date=day, status=status)
        db.add(c)
    db.commit()
    return c

def get_completions_for_habit(db: Session, habit_id: int, limit_days: int=30):
    return db.query(models.Completion).filter(models.Completion.habit_id==habit_id).order_by(models.Completion.date.desc()).limit(limit_days).all()

def due_items(db: Session, now_date, hhmm):
    items = []
    habits = db.query(models.Habit).filter(models.Habit.is_active==True).all()
    for h in habits:
        if h.days:
            allowed = set(int(x) for x in h.days.split(',') if x)
            if now_date.weekday() not in allowed:
                continue
        if h.time_of_day.strftime('%H:%M') != hhmm:
            continue
        if h.last_notified == now_date:
            continue
        user = db.query(models.User).get(h.user_id)
        if not user:
            continue
        items.append({'telegram_id': user.telegram_id, 'text': f"Напоминание: {h.title} ({hhmm})", 'habit_id': h.id})
        h.last_notified = now_date
    db.commit()
    return items

def rollover_habits(db: Session, days_threshold: int = 21):
    from datetime import date, timedelta
    yesterday = date.today() - timedelta(days=1)
    habits = db.query(models.Habit).all()
    for h in habits:
        c = db.query(models.Completion).filter(models.Completion.habit_id==h.id, models.Completion.date==yesterday).first()
        if not c:
            db.add(models.Completion(habit_id=h.id, date=yesterday, status='missed'))
    db.commit()
    return True
