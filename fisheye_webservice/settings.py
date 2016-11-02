import os
import logging

class Settings(object):
  """docstring for Settings"""
  APP_ROOT = os.path.dirname(os.path.realpath(__file__))

  # Number of allowed threads/process to run in parallel to process videos
  PROCESSINGS_THREADS_NUM = 2

  #
  # Uploads settings
  #
  UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
  CONVERTED_PAID_FOLDER = os.path.join(APP_ROOT, 'converted', 'paid')
  CONVERTED_UNPAID_FOLDER = os.path.join(APP_ROOT, 'converted', 'unpaid')
  ALLOWED_EXTENSIONS = ['mp4', 'avi']

  #
  # Log settings
  #
  LOG_FILE_PATH = os.path.join(APP_ROOT, 'fisheye_webservice.log')
  LOG_FILE_MAX_SIZE = 100 * 1024 # Bytes
  # logging level. See available https://docs.python.org/3/library/logging.html#logging-levels
  LOG_LEVEL = logging.DEBUG

  #
  # Video store timeouts (hours)
  #
  PAID_VIDEO_TIMEOUT = 72 # hours
  UNPAID_VIDEO_TIMEOUT = 24 # hours