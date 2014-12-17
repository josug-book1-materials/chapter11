#!/bin/bash -x

# Scenario of chap 11.5.4
#
# function get_uuid () { cat - | grep " id " | awk '{print $4}'; }
# cinder create --display-name ansible-dbs-vol 5
# cinder create --display-name ansible-dbs-bak-vol 5
# ANSIBLE_DBS_VOL=`cinder show ansible-dbs-vol | get_uuid`
# ANSIBLE_DBS_BAK_VOL=`cinder show ansible-dbs-bak-vol | get_uuid`
# ANSIBLE_DBS_VM=`nova list --field name | grep dbs- | awk '{print $2}'`
# nova volume-attach $ANSIBLE_DBS_VM $ANSIBLE_DBS_VOL
# nova volume-attach $ANSIBLE_DBS_VM $ANSIBLE_DBS_BAK_VOL
#
# ssh root@<dbs>
# fdisk /dev/vdc
#  vdc1 -> Linux LVM (8e)
# fdisk /dev/vdd
#  vdd1 -> Linux (83)
#
# [root@dbs-4ad603ef-6f59-45e3-882c-bcf26bc13d22 ~]# lsblk
# vdc    252:32   0    5G  0 disk
# └─vdc1 252:33   0    5G  0 part
# vdd    252:48   0    5G  0 disk
# └─vdd1 252:49   0    5G  0 part

pvcreate /dev/vdc1
vgcreate mysql_vg /dev/vdc1
lvcreate --name mysql_vol01 -L 3g mysql_vg
pvs
vgs
lvs

mkfs.ext4 -L mysql_data /dev/mysql_vg/mysql_vol01
tune2fs -c 0 -i 0 -r 0 /dev/mysql_vg/mysql_vol01
lsblk

echo "Migrating mysql data to LVM partition"
mkdir -p /tmp/data
mount LABEL=mysql_data /tmp/data
chown -R mysql:mysql /tmp/data
service mysqld stop
mv /var/lib/mysql/* /tmp/data/
umount /tmp/data

if ! `grep -q /var/lib/mysql /etc/fstab`; then
  echo "LABEL=mysql_data /var/lib/mysql ext4 defaults,noatime 0 2" >> /etc/fstab
  echo "Added /var/lib/mysql to /etc/fstab"
fi

mount /var/lib/mysql
service mysqld start

#-------------------------------------------

mkfs.ext4 /dev/vdd1
tune2fs -c 0 -i 0 -r 0 /dev/vdd1

lsblk

#-------------------------------------------
# Ansible host
#
# ansible-playbook -i sample_app_inventory.py -t snapshot,backup -u root db_backup.yml

#-------------------------------------------
# @dbs
#
# mount /backup
# ls /backup
# umount /backup
