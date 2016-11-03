#!/bin/bash
set -e

ln -sf /mnt/fisheye_webservice/ /var/www/html/
chown apache:apache /var/www/html/fisheye_webservice -R
chown apache:apache /mnt/fisheye_webservice -R

if ! grep -q "fisheye_webservice" /etc/httpd/conf/httpd.conf; then
  cat /var/www/html/fisheye_webservice/httpd_fisheye_webservice.conf >> /etc/httpd/conf/httpd.conf
fi
pip3 install -r /var/www/html/fisheye_webservice/requirements.txt

cd /mnt/fisheye && make all install
cd /mnt/fisheye/python/ && python setup.py install