#!/bin/bash
#For reference only. Connecting to wap wifi from cli. Not very suited for scripting
wpa_supplicant -s -B -P /run/wpa_supplicant.wlan0.pid -i wlan0 -D nl80211,wext -c /etc/wpa_supplicant/wpa_supplicant.conf
echo $1 $2
wpa_cli remove_network 0
wpa_cli add_network
echo "SSID"
wpa_cli set_network 0 ssid \'\"$1\"\'
wpa_cli set_network 0 key_mgmt WPA-PSK
echo "PASS"
#wpa_cli set_network 0 psk \'\"$2\"\'
#wpa_cli enable_network 0
