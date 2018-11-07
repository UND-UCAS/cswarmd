# CSWARMD
## Cryptographic Swarm Deamon

this repository will handle development of the encryption daemon.

Current state: quick and dirty python scripty to handle the encryption and recieve from a socket as a proof of concept
algorithm currently used: salsa20 (can be changed in the future if needed)
dependencies: libnacl (python bindings), libsodim (actual library)

next steps:
	1. make the daemon modular so we can package this and start using command arguments

goals include:
	1. create a system daemon with systemd
	2. read arbitrary data from a socket and write encrypted stream of arbitrary data to another socket
