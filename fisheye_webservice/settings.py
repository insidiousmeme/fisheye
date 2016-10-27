import os

class Settings(object):
  """docstring for Settings"""
  APP_ROOT = os.path.dirname(os.path.realpath(__file__))
  UPLOAD_FOLDER = os.path.join('uploads')
  PROCESSINGS_THREADS_NUM = 2
  CONVERTED_PAID_FOLDER = os.path.join('converted', 'paid')
  CONVERTED_UNPAID_FOLDER = os.path.join('converted', 'unpaid')
  ALLOWED_EXTENSIONS = ['mp4', 'avi']