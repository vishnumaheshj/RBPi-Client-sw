Create a hotspot if no known network found. Else connect

1)Install Hostapd for creating hotspot, and dnsmasq as minimal dns server
	apt install hostapd
	apt install dnsmasq
2)Disable automatic start on boot of hostapd and dnsmasq
	systemctl disable hostapd
	systemctl disable dnsmasq
3)Copy hostapd.conf to /etc/hostapd/hostapd.conf
4)In /etc/default/hostapd add DAEMON_CONF="/etc/hostapd/hostapd.conf"
5)Copy the lines in dnsmasq.conf to /etc/dnsmasq.conf
6)Copy interfaces to /etc/network/interfaces
7)Copy DotslashHotspot.service to /etc/systemd/system/
8)Enable the service
	sudo systemctl enable DotslashHotspot.service
9)Make sure that iw is installed. 
10)Copy DotslashHotspot to /usr/bin/DotslashHotspot and make sure that it is executable.


