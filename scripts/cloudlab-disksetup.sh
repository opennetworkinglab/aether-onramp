#!/usr/bin/env bash

# Copyright 2017-present Open Networking Foundation
#
# SPDX-License-Identifier: Apache-2.0

###############################################
# Disk setup and symlinks for a CloudLab node #
###############################################

# Don't do anything if not a CloudLab node
[ ! -d /usr/local/etc/emulab ] && exit 0

# The watchdog will sometimes reset groups, turn it off
if [ -e /usr/local/etc/emulab/watchdog ]
then
  sudo /usr/bin/perl -w /usr/local/etc/emulab/watchdog stop
  sudo mv /usr/local/etc/emulab/watchdog /usr/local/etc/emulab/watchdog-disabled
fi

# Mount extra space, if haven't already
if [ ! -d /mnt/extra ]
then
    sudo mkdir -p /mnt/extra

    # for NVME SSD on Utah m510, not supported by mkextrafs
    if df | grep -q nvme0n1p1 && [ -e /usr/testbed/bin/mkextrafs ]
    then
        # set partition type of 4th partition to Linux, ignore errors
        echo -e "t\\n4\\n82\\np\\nw\\nq" | sudo fdisk /dev/nvme0n1 || true

        sudo mkfs.ext4 /dev/nvme0n1p4
        echo "/dev/nvme0n1p4 /mnt/extra/ ext4 defaults 0 0" | sudo tee -a /etc/fstab
        sudo mount /mnt/extra
        mount | grep nvme0n1p4 || (echo "ERROR: NVME mkfs/mount failed, exiting!" && exit 1)

    elif [ -e /usr/testbed/bin/mkextrafs ] && [ -b /dev/sdb ] # if on Clemson/Wisconsin Cloudlab
    then
        # Sometimes this command fails on the first try
        sudo /usr/testbed/bin/mkextrafs -s 1 -r /dev/sdb -qf "/mnt/extra/" || sudo /usr/testbed/bin/mkextrafs -s 1 -r /dev/sdb -qf "/mnt/extra/"

        # Check that the mount succeeded (sometimes mkextrafs succeeds but device not mounted)
        mount | grep sdb || (echo "ERROR: mkextrafs failed, exiting!" && exit 1)

    elif [ -e /usr/testbed/bin/mkextrafs ] && [ -b /dev/sda4 ] # if on Utah xl170
    then
        # set partition type of 4th partition to Linux, ignore errors
        printf "t\\n4\\n83\\np\\nw\\nq" | sudo fdisk /dev/sda || true

        sudo mkfs.ext4 /dev/sda4
        echo "/dev/sda4 /mnt/extra/ ext4 defaults 0 0" | sudo tee -a /etc/fstab
        sudo mount /mnt/extra
        mount | grep sda4 || (echo "ERROR: mkfs/mount failed, exiting!" && exit 1)
    fi
fi

# prepare for creating the libvirt/images symlink
sudo mkdir -p /var/lib/libvirt
sudo rm -rf /var/lib/libvirt/images

# create symlinks to /mnt/extra partition
for DIR in docker kubelet openstack-helm nova libvirt/images rancher
do
    sudo mkdir -p "/mnt/extra/$DIR"
    sudo chmod -R a+rwx "/mnt/extra/$DIR"
    if [ ! -e "/var/lib/$DIR" ]
    then
        sudo ln -s "/mnt/extra/$DIR" "/var/lib/$DIR"
    fi
done
sudo mkdir -p "/mnt/extra/k3s"
sudo chmod -R a+rwx "/mnt/extra/k3s"
if [ ! -e "/run/k3s" ]; then sudo ln -s "/mnt/extra/k3s" "/run/k3s"; fi
