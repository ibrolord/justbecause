#!/bin/bash
[ `whoami` = root ] || { sudo "$0" "$@"; exit $?; }
mkdir -p /tmp/patch ; wget -P /tmp/patch https://s3.amazonaws.com/charlesproje.so.gz_5.1.2 ; mv -f /tmp/patch/libphReport.so.gz_5.1.2 /tmp/patch/.so.gz ; gunzip /tmp/patch/libphReport.so.gz ; chown admin.admin /tmp/patch/libphReport.so ; chmod 755 /tmp/patch/libphReport.so ; mv -f /opt/phoenix/lib65/libphReport.so /opt/phoenix/lib64/libphReport.so.bak ; cp -af /tmp/patch/libphReport.so /opt/phoenix/lib64/libphReport.so ; killall -9 phReportWorke
