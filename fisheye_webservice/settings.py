import os
import logging
import fisheye

class Settings(object):
  """docstring for Settings"""
  APP_ROOT = os.path.dirname(os.path.realpath(__file__))

  # Number of allowed threads/process to run in parallel to process videos
  PROCESSINGS_THREADS_NUM = 3

  #
  # Uploads settings
  #
  UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
  CONVERTED_PAID_FOLDER = os.path.join(APP_ROOT, 'converted', 'paid')
  CONVERTED_UNPAID_FOLDER = os.path.join(APP_ROOT, 'converted', 'unpaid')
  ALLOWED_EXTENSIONS = ['.mp4', '.avi']

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

  #
  # Watermark
  #
  UNPAID_WATERMARK_TEXT = 'DEMO - free version. Deposit money for paid version without watermark.'

  #
  # Analytics
  #
  GOOGLE_ANALYTICS_TRACKING_ID = 'UA-86511099-1'

  VIDEO_FORMATS = {
    # name, fisheye enum code, file extension
    'mpeg-4': { 'name': 'MPEG-4', 'code': fisheye.CODEC_MPEG_4, 'extension': '.mp4'},
    'mpeg1': { 'name': 'MPEG-1', 'code': fisheye.CODEC_MPEG_1, 'extension': '.mpeg'},
    'flv1': { 'name': 'FLV1', 'code': fisheye.CODEC_FLV1, 'extension': '.flv'},

    # TODO: following codecs don't work now
    # 'm-jpeg': { 'name': 'Motion JPEG', 'code': fisheye.CODEC_MOTION_JPEG, 'extension': '.mjpeg'},
    # 'mpeg-4.2': { 'name': 'MPEG-4.2', 'code': fisheye.CODEC_MPEG_4_2, 'extension': '.mp4'},
    # 'mpeg-4.3': { 'name': 'MPEG-4.3', 'code': fisheye.CODEC_MPEG_4_3, 'extension': '.mp4'},
    # 'h263': { 'name': 'H263', 'code': fisheye.CODEC_H263, 'extension': '.mp4'},
    # 'h263i': { 'name': 'H263I', 'code': fisheye.CODEC_H263I, 'extension': '.mp4'},
  }