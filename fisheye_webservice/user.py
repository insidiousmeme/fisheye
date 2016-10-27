from peewee import *

from base_model import BaseModel
from datetime import datetime

class User(BaseModel):
  # constants
  PAYMENT_LEVEL_UNLIMITED=1
  PAYMENT_LEVEL_LIMITED=2

  # fields
  email = CharField(unique=True)
  password = CharField()
  date_time = DateTimeField(default=datetime.now())
  ip = CharField()
  payment_level = IntegerField(default=PAYMENT_LEVEL_UNLIMITED) # (1=unlimited, 2=limited)
  number_of_sessions_left = IntegerField(default=0)

