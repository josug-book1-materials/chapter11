#!/bin/bash

usage() {
  echo "Usage: $0 <sample_app_inventory.ini> <openrc>"
  exit 1
}

if [ -z "$2" ]; then
  usage
fi

inifile=$1
openrc=$2

if [ ! -f $inifile ]; then
  echo "$inifile not found"
  exit 1
fi
if [ ! -f $openrc ]; then
  echo "$openrc not found"
  exit 1
fi

. $openrc

sed -i -e "s|%OS_USERNAME%|$OS_USERNAME|" $inifile 
sed -i -e "s|%OS_PASSWORD%|$OS_PASSWORD|" $inifile 
sed -i -e "s|%AUTH_URL%|$OS_AUTH_URL|" $inifile 
sed -i -e "s|%REGION_NAME%|$OS_REGION_NAME|" $inifile 
sed -i -e "s|%TENANT_NAME%|$OS_TENANT_NAME|" $inifile 
