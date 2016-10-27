#!/usr/bin/env python3

"""
setup.py file for fisheye module
"""

from distutils.core import setup, Extension
import os

root_dir = os.path.join('..')
include_dir = root_dir
opencv3_include_dir = os.path.join(root_dir, '..', '..', 'opencv-3.1.0', 'install', 'include')

lib_dir = root_dir

fisheye_module = Extension(
  '_fisheye',
  sources=['./fisheye_wrap.cxx'],
  include_dirs=[include_dir, opencv3_include_dir],
  libraries=['fisheye'],
  extra_link_args=['-L' + lib_dir]
)

setup (name = 'fisheye',
       version = '0.1',
       author      = "Dmitry Belous <dmigous@gmail.com>",
       description = """Swig fisheye wrapper""",
       ext_modules = [fisheye_module],
       py_modules = ["fisheye"],
       )
