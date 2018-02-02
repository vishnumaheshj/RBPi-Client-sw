1) Hosts a server at 10.0.0.10(With the configuration in wifi-manager can be accessed as dotslash.net)
2) Use Hub Identification Number for authentication. For now storing hash in /etc/DotShadow and comparing. Find out the proper way
3)Uses a forced scan using iw to find available wifi and prints it in /wifi
4)Accepts ssid and password from user. Creates wpa_conf file in /etc/dot_wpa.conf
5)Terminates the server after receiving wifi and password from user
