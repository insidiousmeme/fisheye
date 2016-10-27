import os
import uuid

from time import sleep
from flask import Flask, request, flash, redirect, url_for, send_from_directory, g
from flask import render_template

from peewee import *
from fisheye import FisheyeVideoConverter
import concurrent.futures
import threading

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import FloatField, IntegerField, StringField, PasswordField, validators

from user import User
from video import Video
from settings import Settings
from base_model import db
from fisheye import FisheyeVideoConverter


UNAUTHORIZED_USER_EMAIL = 'unauthorized@mytech.today'

# Print all queries to stderr.
# import logging
# logger = logging.getLogger('peewee')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())

app = Flask(__name__)
app.secret_key = 'c298845c-beb8-4fdc-aef0-eabd22082697'

class ConvertFisheyeVideoForm(FlaskForm):
  email = StringField('Email Address', [validators.DataRequired()])
  password = PasswordField('Password', [validators.DataRequired()])
  video = FileField('Video File')
  degree = IntegerField('Degree', [validators.NumberRange(message='Degree should be from 0 to 250', min=0, max=250)], default=0)
  rotation = FloatField('Rotation', [validators.NumberRange(message='Rotation should be from 0 to 359.99', min=0, max=359.99)], default=0)

def allowed_file(filename):
  return '.' in filename and \
    filename.lower().rsplit('.', 1)[1] in Settings.ALLOWED_EXTENSIONS

@app.before_first_request
def init_application():
  os.makedirs(Settings.CONVERTED_UNPAID_FOLDER, exist_ok=True)
  os.makedirs(Settings.CONVERTED_PAID_FOLDER, exist_ok=True)
  os.makedirs(Settings.UPLOAD_FOLDER, exist_ok=True)
  db.create_tables([User, Video], safe=True)
  create_unauthorized_user()

  threading.Thread(target=video_processor).start()

@app.before_request
def before_request():
  g.db = db
  g.db.connect()


@app.after_request
def after_request(response):
  g.db.close()
  return response

@app.route('/', methods=['GET', 'POST'])
def index():
  form=ConvertFisheyeVideoForm()
  if request.method == 'POST':
    filename = form.video.data.filename
    # if user does not select file, browser also
    # submit a empty part without filename
    if allowed_file(filename):
      to_unpaid = False
      try:
        user = User.get(User.email == form.email.data, User.password == form.password.data)
      except:
        to_unpaid = True
        user = User.get(User.email == UNAUTHORIZED_USER_EMAIL)

      if user and user.payment_level == User.PAYMENT_LEVEL_LIMITED and user.number_of_sessions_left < 1:
        to_unpaid = True

      extension = os.path.splitext(filename)[1]
      video_uuid = str(uuid.uuid4())
      filename = video_uuid + extension
      remote_addr = request.remote_addr if request.remote_addr is not None else ''
      original_file_path = os.path.join(Settings.UPLOAD_FOLDER, filename)
      converted_file_path = os.path.join((Settings.CONVERTED_UNPAID_FOLDER if to_unpaid else Settings.CONVERTED_PAID_FOLDER), filename)

      # save video on disk
      form.video.data.save(original_file_path)

      # save to info to db
      video = Video.create(user=user,
                           ip=remote_addr,
                           uuid=video_uuid,
                           original_file_path=original_file_path,
                           degree=form.degree.data,
                           rotation=form.rotation.data,
                           converted_file_path=converted_file_path)
      video.save()

      return redirect(url_for('get_result', video_uuid=video_uuid))
    else:
      return render_template('index.html', error='File format not allowed')

  return render_template('index.html', form=form)


@app.route('/get_result/<video_uuid>')
def get_result(video_uuid):
  try:
    video = Video.get(Video.uuid == video_uuid)
  except:
    return render_template('get_result.html', error='There is no such video with given link')


  link = url_for('download', video_uuid=video.uuid) if video.converted_file_size > 0 else ''
  return render_template('get_result.html', link=link)


@app.route('/download/<video_uuid>')
def download(video_uuid):
  try:
    video = Video.get(Video.uuid == video_uuid)
  except:
    return render_template('get_result.html', error='There is no such video with given link')

  if video.error:
    return render_template('get_result.html', error=video.error)

  return send_from_directory('.', video.converted_file_path)


def convert_fisheye_video(original_file_path, converted_file_path, degree, rotation):
  video = Video.get(Video.original_file_path == original_file_path)
  try:
    converter = FisheyeVideoConverter()
    print('START CONVERION of ' + video.uuid)
    converter.fisheye_convert(original_file_path,
                              converted_file_path,
                              degree,
                              rotation)
  except Exception:
    video.error = 'Failed to convert video'
    video.save()
    return

  video.converted_file_size = os.path.getsize(video.converted_file_path)
  video.save()

  user = video.user
  if user.payment_level == User.PAYMENT_LEVEL_LIMITED:
    user.number_of_sessions_left -=1
    user.save()


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

      # print('================WAITING================')
      concurrent.futures.wait(futures)
      # not_processesed_videos = Video.select().where(Video.converted_file_size == -1).order_by(
      #     Video.date_time.asc())
      # print('not processed = ' + str(not_processesed_videos.count()))
      # print('================DONE================')


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

if __name__ == '__main__':
  app.run()
