	README
======================

steps necessary to get server and hub-client up and running.

I) INSTALLATION INSTRUCTIONS
==============================

	1)Install virtualenv
		$apt install virtualenv
	2)Create a virtual python environment
		$virtualenv env
	3)Activate virtual environment
		$source env/bin/activate
	4)Install tornado
		$pip install tornado
	5)Do a make in tornado_backend/shared
		$make
	6)Create a symbolic link from dataSendRcv.bin in ZNP to tornado_backend/
		$ln -sf 'path to  dataSendRcv.bin' .

II) Running the program

	0)Activate virtualenv if not already activated
		$source env/bin/activate

	2) Run hub-client
		$python dev_client.py
		
		This will try to connect to server running at localhost port 8888 by default.
		Update the details if remote connection etc.

