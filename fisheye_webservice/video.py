from peewee import *

from base_model import BaseModel
from user import User
from datetime import datetime

class Video(BaseModel):
  user = ForeignKeyField(User)
  date_time = DateTimeField(default=datetime.now())
  ip = CharField()
  uuid=CharField()
  original_file_path = CharField()
  degree = FloatField()
  rotation = FloatField()
  converted_file_path = CharField()
  converted_file_size = IntegerField(default=-1)
  paid = BooleanField()
  error = CharField(null=True)

  def is_processed():
    return (converted_file_size >= 0)

