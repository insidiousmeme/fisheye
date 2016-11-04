#!/bin/bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT=$ROOT_DIR/../../../
UPSTART_TEMPLATE=$ROOT_DIR/fisheye_webserver_template.conf
UPSTART_OUTPUT_CONF=/etc/init/fisheye_webserver.conf
sed "s@__fisheye_repo_path__@$REPO_ROOT@g" $UPSTART_TEMPLATE > $UPSTART_OUTPUT_CONF