from setuptools import setup

setup(
    name='Fisheye Webservice',
    version='0.1',
    long_description="web service for convertion of fisheye videos",
    packages=['Webservice'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'peewee', 'Flask-WTF', 'wtforms']
)