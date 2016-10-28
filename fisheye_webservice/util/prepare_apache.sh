#!/bin/bash
set -e

ln -s /mnt/fisheye/fisheye_webservice/ /var/www/html/
chown apache:apache /var/www/html/fisheye_webservice/ -R

cat /var/www/html/fisheye_webservice/httpd_fisheye_webservice.conf >> /etc/httpd/conf/httpd.conf
pip3 install -r /var/www/html/fisheye_webservice/requirements.txt

cd /mnt/fisheye/fisheye && make all install
cd /mnt/fisheye/fisheye/python/ && python setup.py install