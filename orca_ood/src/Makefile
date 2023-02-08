CC = g++
LIBS = -pthread

all: orca-server-mahimahi client

orca-server-mahimahi:
	${CC} ${LIBS} orca-server-mahimahi.cc flow.cc -o ../orca-server-mahimahi

client: 
	${CC} ${LIBS} client.c -o ../client
