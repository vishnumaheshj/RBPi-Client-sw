	README
======================

steps necessary to install and start local-server

I) INSTALLATION INSTRUCTIONS
==============================

	1)Install tornado
		$pip install tornado
	2)Install pymongo
		$pip install pymongo
	3)Install bidict
		$pip install bidict
	4)Install mongodb according to instructions at http://koenaerts.ca/compile-and-install-mongodb-on-raspberry-pi/
		$wget https://fastdl.mongodb.org/src/mongodb-src-r3.2.12.tar.gz
	5)Create /data/db for mongod
		$mkdir -p /data/db
	6)Set locale for mongodb(/etc/default/locale)
		$update-locale LC_ALL=C

II) Running the program

	1) Run server
		$python server.py

		This will run the server on localhost at port 8888 by default

	3)Access the server from a local/remote browser
		URL= http://localhost:8888
			or
		URL= http://ip:8888 [if remote]
		This should show connected hubs and provides and interface to send messages to hub via server
