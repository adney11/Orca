#!/bin/bash -x 
sudo apt-get install -y build-essential git debhelper autotools-dev dh-autoreconf iptables protobuf-compiler libprotobuf-dev pkg-config libssl-dev dnsmasq-base ssl-cert libxcb-present-dev libcairo2-dev libpango1.0-dev iproute2 apache2-dev apache2-bin iptables dnsmasq-base gnuplot iproute2 apache2-api-20120211 libwww-perl
git clone https://github.com/ravinet/mahimahi 
cd mahimahi
./autogen.sh && ./configure && make
sudo make install
sudo sysctl -w net.ipv4.ip_forward=1
