import os
import uuid

from time import sleep
from datetime import datetime, timedelta

from flask import Flask, request, flash, redirect, url_for, send_from_directory, g, render_template
from flask_analytics import Analytics

from peewee import *
from fisheye import FisheyeVideoConverter
import concurrent.futures
import threading

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import FloatField, IntegerField, StringField, PasswordField, validators, ValidationError

from user import User
from video import Video
from settings import Settings
from base_model import db
from fisheye import FisheyeVideoConverter

import logging
from logging.handlers import RotatingFileHandler

UNAUTHORIZED_USER_EMAIL = 'unauthorized@mytech.today'

app = Flask(__name__)

# docs: https://github.com/citruspi/Flask-Analytics
Analytics(app)
app.config['ANALYTICS']['GOOGLE_UNIVERSAL_ANALYTICS']['ACCOUNT'] = Settings.GOOGLE_ANALYTICS_TRACKING_ID

app.secret_key = 'c298845c-beb8-4fdc-aef0-eabd22082697'

#
# Setup logger
#
handler = RotatingFileHandler(Settings.LOG_FILE_PATH,
                              maxBytes=Settings.LOG_FILE_MAX_SIZE,
                              backupCount=1)
handler.setLevel(Settings.LOG_LEVEL)
formatter = logging.Formatter(
    "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(Settings.LOG_LEVEL)

#
# Helper functions
#

def VideoFileValidator(form, field):
  filename = field.raw_data[0].filename
  if not filename:
    raise ValidationError("You must select file to upload.")
  ext = os.path.splitext(filename)[1]
  app.logger.debug("User trying to upload file with extension %s", ext)
  if not ext.lower() in Settings.ALLOWED_EXTENSIONS:
    app.logger.error('File format %s not allowed', ext)
    extensions_list = ', '.join(Settings.ALLOWED_EXTENSIONS)
    raise ValidationError(" must be an video file with extension " + extensions_list)

class ConvertFisheyeVideoForm(FlaskForm):
  email = StringField('Email Address', [validators.DataRequired(), validators.Email()])
  password = PasswordField('Password', [validators.DataRequired()])
  video = FileField('Video File', validators=[VideoFileValidator])
  degree = FloatField('Degree', [validators.NumberRange(message='Degree should be from 0 to 250.00', min=0, max=250), validators.DataRequired()])
  rotation = FloatField('Rotation', [validators.NumberRange(message='Rotation should be from 0 to 359.99', min=0, max=359.99), validators.DataRequired()])

def convert_fisheye_video(original_file_path, converted_file_path, degree, rotation):
  try:
    app.logger.debug('Querying video %s', original_file_path)
    video = Video.get(Video.original_file_path == original_file_path)
  except:
    app.logger.critical('Video %s not found in database', original_file_path)
    return

  try:
    converter = FisheyeVideoConverter()
    app.logger.info('Start converion %s of %s', ("PAID" if video.paid else "UNPAID"), video.uuid)
    if video.paid:
      converter.Convert(original_file_path, converted_file_path, degree, rotation)
    else:
      converter.Convert(original_file_path, converted_file_path, degree, rotation, Settings.UNPAID_WATERMARK_TEXT)
  except Exception:
    app.logger.error('Failed to convert video %s', video.uuid)
    video.error = 'Failed to convert video'
    video.converted_file_size = 0 # to remove it from processing queue
    video.save()
    return

  video.converted_file_size = os.path.getsize(video.converted_file_path)
  video.save()
  app.logger.info('Successfully finished conversion of %s, converted file size is %d',
                  video.uuid,
                  video.converted_file_size)

  user = video.user
  if user.payment_level == User.PAYMENT_LEVEL_LIMITED:
    user.number_of_sessions_left -=1
    user.save()
    app.logger.debug('Reduced %s paid sessions to %d', user.email, user.number_of_sessions_left)

def video_processor():
  while True:
    try:
      not_processesed_videos = Video.select().where(Video.converted_file_size == -1).order_by(
          Video.date_time.asc())
    except Video.DoesNotExist:
      sleep(15) # if no video to process then sleep 15 sec
      continue

    if not not_processesed_videos:
      sleep(15) # if no video to process then sleep 15 sec
      continue


    with concurrent.futures.ProcessPoolExecutor(max_workers=Settings.PROCESSINGS_THREADS_NUM) as executor:
      # for video in not_processesed_videos:
      futures = {executor.submit(
                  convert_fisheye_video,
                  video.original_file_path,
                  video.converted_file_path,
                  video.degree,
                  video.rotation): video for video in not_processesed_videos}

      app.logger.info('Started video processing')
      concurrent.futures.wait(futures)
      not_processesed_videos = Video.select().where(Video.converted_file_size == -1).order_by(
          Video.date_time.asc())
      app.logger.info('Currently %d videos in processing queue', not_processesed_videos.count())

def video_files_cleaner():
  while True:
    try:
      app.logger.debug('Deleting paid videos older than %d hours', Settings.PAID_VIDEO_TIMEOUT)
      ttl = datetime.now() - timedelta(hours=Settings.PAID_VIDEO_TIMEOUT)
      for video in Video.select().where(Video.paid == True, Video.date_time < ttl):
        os.remove(video.original_file_path)
        os.remove(video.converted_file_path)
        video.delete_instance()
    except:
      pass

    try:
      app.logger.debug('Deleting unpaid videos older than %d hours', Settings.UNPAID_VIDEO_TIMEOUT)
      ttl = datetime.now() - timedelta(hours=Settings.UNPAID_VIDEO_TIMEOUT)
      for video in Video.select().where(Video.paid == False, Video.date_time < ttl):
        os.remove(video.original_file_path)
        os.remove(video.converted_file_path)
        video.delete_instance()
    except:
      pass

    # Make a check once an hour
    sleep(1 * 60 * 60) # 1 hour

def create_unauthorized_user():
  # Ensure that there is user created in db for unauthorized video processing
  try:
    User.create(
      email=UNAUTHORIZED_USER_EMAIL,
      password='unauthorized_mytech.today',
      ip='127.0.0.1',
      payment_level=User.PAYMENT_LEVEL_UNLIMITED
    ).save()
  except:
    pass

@app.before_first_request
def init_application():
  app.logger.debug('Creating folders')
  # create directories if not exists
  os.makedirs(os.path.join(Settings.CONVERTED_UNPAID_FOLDER), exist_ok=True)
  os.makedirs(os.path.join(Settings.CONVERTED_PAID_FOLDER), exist_ok=True)
  os.makedirs(os.path.join(Settings.UPLOAD_FOLDER), exist_ok=True)

  app.logger.debug('Initializating DB')
  # create tables in db if not exists
  db.create_tables([User, Video], safe=True)
  create_unauthorized_user()

  app.logger.debug('Starting video_processor thread')
  threading.Thread(target=video_processor).start()

  app.logger.debug('Starting video_files_cleaner thread')
  threading.Thread(target=video_files_cleaner).start()

@app.before_request
def before_request():
  g.db = db
  g.db.connect()

@app.after_request
def after_request(response):
  g.db.close()
  return response

#
# Routes
#
@app.route('/', methods=['GET', 'POST'])
def index():
  form=ConvertFisheyeVideoForm()
  if request.method == 'POST' and form.validate():
    filename = form.video.data.filename

    paid = False
    try:
      user = User.get(User.email == form.email.data, User.password == form.password.data)
      app.logger.info('User %s authorization success.', user.email)
    except:
      app.logger.info('There is no user %s with given password. Falling to unpaid session.', form.email.data)
      paid = False
      user = User.get(User.email == UNAUTHORIZED_USER_EMAIL)

    if user and user.payment_level == User.PAYMENT_LEVEL_LIMITED and user.number_of_sessions_left < 1:
      app.logger.info('User %s has no paid sessions left. Falling to unpaid session', user.email)
      paid = False

    extension = os.path.splitext(filename)[1]
    video_uuid = str(uuid.uuid4())
    filename = video_uuid + extension
    remote_addr = request.remote_addr if request.remote_addr is not None else ''
    original_file_path = os.path.join(Settings.UPLOAD_FOLDER, filename)
    converted_file_path = os.path.join(
        (Settings.CONVERTED_UNPAID_FOLDER if not paid \
          else Settings.CONVERTED_PAID_FOLDER), filename)

    app.logger.debug('Saving video %s on disk', video_uuid)
    form.video.data.save(original_file_path)
    app.logger.debug('Saved video %s original file size is %d Bytes', video_uuid, os.path.getsize(original_file_path))

    app.logger.debug('Saving video info to db')
    video = Video.create(user=user,
                         ip=remote_addr,
                         uuid=video_uuid,
                         original_file_path=original_file_path,
                         degree=form.degree.data,
                         rotation=form.rotation.data,
                         converted_file_path=converted_file_path,
                         paid=paid)
    video.save()
    return redirect(url_for('get_result', video_uuid=video_uuid))


  return render_template('index.html', form=form)


@app.route('/get_result/<video_uuid>')
def get_result(video_uuid):
  try:
    app.logger.debug('Querying video %s', video_uuid)
    video = Video.get(Video.uuid == video_uuid)
  except:
    app.logger.debug('Video %s not found in database', video_uuid)
    return render_template('get_result.html', error='There is no such video with given link')


  video_processed = (video.converted_file_size > 0)

  app.logger.debug('Video %s was found in database, its status is "%s"',
                   video_uuid,
                   'ready' if video_processed else 'pending')

  link = url_for('download', video_uuid=video.uuid) if video_processed else ''
  return render_template('get_result.html', link=link)


@app.route('/download/<video_uuid>')
def download(video_uuid):
  try:
    app.logger.debug('Querying video %s', video_uuid)
    video = Video.get(Video.uuid == video_uuid)
  except:
    app.logger.debug('Video %s not found in database', video_uuid)
    return render_template('get_result.html', error='There is no such video with given link')

  if video.error:
    app.logger.info('Error occured during processing of video %s: %s', video_uuid, video.error)
    return render_template('get_result.html', error=video.error)

  app.logger.info('Giving user data stream to download video %s', video_uuid)
  return send_from_directory(os.path.dirname(video.converted_file_path),
                             os.path.basename(video.converted_file_path))

#
# Main
#

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
