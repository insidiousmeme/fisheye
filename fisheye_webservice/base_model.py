from peewee import * 
import os

from settings import Settings

DATABASE = os.path.join(Settings.APP_ROOT, 'fisheye_webservice.db')
db = SqliteDatabase(DATABASE)

class BaseModel(Model):
    class Meta:
        database = db