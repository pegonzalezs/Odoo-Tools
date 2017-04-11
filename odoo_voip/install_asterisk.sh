#!/bin/bash

################################################################################
# Script for installing Asterisk on Centos 7
# Author: Pedro Gonzalez
#-------------------------------------------------------------------------------
# DOCUMENTATION:
# Asterisk dependencies declared by Odoo
# https://www.odoo.com/documentation/user/9.0/es/crm/leads/voip/setup.html
#-------------------------------------------------------------------------------
# STEPS:
#   - Execute the script to install Odoo as root: ./initial-script.sh
################################################################################

SERVER_NAME="your.domain.com"

echo "-------------------------------------------"
echo "########## Update Server #########"
echo "-------------------------------------------"
echo -e "\n---- Updating Centos ----"
yum update -y
yum install epel-release -y

echo "--------------------------------------------------"
echo "########## Install Asterisk Dependencies #########"
echo "--------------------------------------------------"
echo -e "---- Installing Dependencies... ----"
sudo yum install -y wget gcc gcc-c++ ncurses-devel libxml2-devel sqlite-devel libsrtp-devel libuuid-devel openssl-devel libsrtp libsrtp-devel bzip2 jansson-devel

echo "--------------------------------------------------"
echo "########## Install PJSIP #########"
echo "--------------------------------------------------"
sudo cd /usr/src
sudo wget http://www.pjsip.org/release/2.3/pjproject-2.3.tar.bz2
sudo tar xvjf pjproject*
sudo cd pjproject*
./configure CFLAGS="-DNDEBUG -DPJ_HAS_IPV6=1" --prefix=/usr --libdir=/usr/lib64 --enable-shared --disable-video --disable-sound --disable-opencore-amr
make dep
make
make install
ldconfig

echo "--------------------------------------------------"
echo "############## Install Asterisk ##################"
echo "--------------------------------------------------"
sudo cd /usr/src
sudo wget http://downloads.asterisk.org/pub/telephony/asterisk/old-releases/asterisk-13.7.0.tar.gz
sudo tar zxvf asterisk*
sudo cd ./asterisk*
sudo ./configure --with-pjproject --with-ssl --with-srtp

echo "--------------------------------------------------"
echo "############## Check Resource RES-SRTP & PJSIP ##################"
echo "--------------------------------------------------"
sudo make menuselect
sudo make && sudo make install

echo "-------------------------------------------------------------------------"
echo "############## Install Configuration Files and Service ##################"
echo "-------------------------------------------------------------------------"
sudo make samples
sudo make config

echo "------------------------------------------------------"
echo "############## Install Certificates ##################"
echo "------------------------------------------------------"
sudo mkdir /etc/asterisk/keys
sudo cd contrib/scripts
sudo ./ast_tls_cert -C $SERVER_NAME -O "My Asterisk" -d /etc/asterisk/keys

echo "------------------------------------------------------"
echo "############## Create User Asterisk ##################"
echo "------------------------------------------------------"
sudo adduser asterisk -M -c "Asterisk User"
sudo chown asterisk. -R /var/run/asterisk
sudo chown asterisk. -R /etc/asterisk
chown asterisk. -R /usr/lib/asterisk

echo "------------------------------------------------------"
echo "############## Configure Firewall ##################"
echo "------------------------------------------------------"
sudo firewall-cmd --zone=public --add-port=5060/udp --permanent
sudo firewall-cmd --zone=public --add-port=5060/tcp --permanent
sudo firewall-cmd --zone=public --add-port=5061/udp --permanent
sudo firewall-cmd --zone=public --add-port=5061/tcp --permanent
sudo firewall-cmd --zone=public --add-port=4569/udp --permanent
sudo firewall-cmd --zone=public --add-port=5038/tcp --permanent
sudo firewall-cmd --zone=public --add-port=10000-20000/udp --permanent
sudo firewall-cmd --zone=public --add-port=8088/tcp --permanent
sudo firewall-cmd --zone=public --add-port=8088/udp --permanent
sudo firewall-cmd --reload

#### KNOWN ISSUES #####
# Known Issues
# 1.- asterisk: error while loading shared libraries: libasteriskssl.so.1: cannot open shared object file: No such file or directory
#     Check which libraries are not found => ldd /usr/sbin/asterisk
#     Solution -> create symbolic link in /usr/lib64 => ln -s /usr/lib/libasteriskssl.so.1 /usr/lib64/libasteriskssl.so.1
