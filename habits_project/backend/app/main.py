from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os, datetime, pytz
from typing import List
from . import models, crud, schemas, auth
from pydantic import BaseModel
from datetime import datetime, date

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./test.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title='Habits API')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    payload = auth.verify_token(token)
    if not payload or 'telegram_id' not in payload:
        raise HTTPException(status_code=401, detail='Invalid token')
    u = crud.get_or_create_user(db, payload['telegram_id'])
    return u

@app.post('/auth/token', response_model=schemas.Token)
def obtain_token(payload: schemas.UserCreate, db=Depends(get_db)):
    user = crud.get_or_create_user(db, payload.telegram_id)
    token = auth.create_access_token({'telegram_id': user.telegram_id})
    return {'access_token': token, 'token_type': 'bearer'}

@app.get('/habits', response_model=List[schemas.HabitOut])
def list_habits(token_user = Depends(get_current_user), db=Depends(get_db)):
    items = crud.list_habits(db, token_user)
    out = []
    for h in items:
        out.append({'id': h.id, 'user_id': h.user_id, 'title': h.title, 'time_of_day': h.time_of_day.strftime('%H:%M'), 'days': [int(x) for x in h.days.split(',')] if h.days else None, 'is_active': h.is_active})
    return out

@app.post('/habits', response_model=schemas.HabitOut)
def create_habit(h: schemas.HabitCreate, token_user = Depends(get_current_user), db=Depends(get_db)):
    tz = pytz.timezone(os.getenv('TIMEZONE','Europe/Sofia'))
    now = datetime.now(tz)
    start = os.getenv('ALLOWED_WINDOW_START','08:00')
    end = os.getenv('ALLOWED_WINDOW_END','22:00')
    st = datetime.strptime(start,'%H:%M').time()
    en = datetime.strptime(end,'%H:%M').time()
    if not (st <= now.time() <= en):
        raise HTTPException(status_code=403, detail=f'Changes allowed only between {start} and {end}')
    hh, mm = [int(x) for x in h.time_of_day.split(':')]
    import datetime as _dt
    tod = _dt.time(hh, mm)
    created = crud.create_habit(db, token_user, h.title, tod, h.days, h.is_active)
    return {'id': created.id, 'user_id': created.user_id, 'title': created.title, 'time_of_day': created.time_of_day.strftime('%H:%M'), 'days': [int(x) for x in created.days.split(',')] if created.days else None, 'is_active': created.is_active}

@app.post('/habits/{habit_id}/complete')
def complete_habit(habit_id: int, payload: schemas.CompleteIn, token_user = Depends(get_current_user), db=Depends(get_db)):
    day = payload.date or date.today()
    c = crud.mark_completion(db, habit_id, payload.status, day)
    return {'ok': True, 'habit_id': habit_id, 'date': str(day), 'status': payload.status}

@app.post('/due')
def due_now(db=Depends(get_db)):
    tz = pytz.timezone(os.getenv('TIMEZONE','Europe/Sofia'))
    now = datetime.now(tz)
    hhmm = now.strftime('%H:%M')
    items = crud.due_items(db, now.date(), hhmm)
    return {'items': items}

from apscheduler.schedulers.background import BackgroundScheduler
def start_scheduler():
    sched = BackgroundScheduler(timezone=os.getenv('TIMEZONE','Europe/Sofia'))
    def job_rollover():
        db = SessionLocal()
        try:
            crud.rollover_habits(db)
        finally:
            db.close()
    sched.add_job(job_rollover, 'cron', hour=0, minute=5)
    sched.start()

start_scheduler()
