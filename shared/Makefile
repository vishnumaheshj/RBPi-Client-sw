all:
	gcc -c -fPIC server.c -o server.o
	gcc -shared -Wl,-soname,libshm.so -o libshm.so server.o
	cp libshm.so ../

clean:
	rm -f libshm.so server.o client ../libshm.so
