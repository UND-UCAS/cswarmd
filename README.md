# CSWARMD
## Cryptographic Swarm Deamon

this repository will handle development of the encryption daemon.

Current state: propper python package, can handle command line arguments and single mode of operation encrypt or decrypt while reading and writing to user-specified arbitrary sockets of type AF_INET
algorithm currently used: salsa20 (can be changed in the future if needed)
dependencies: libnacl (python bindings), libsodim (actual library)

known issues: as it currently stands, this code is quite fragile because there is no error checking whatsoever, so if something is not listening on the socket we intend to write to when we try to write to it, everyting dies in a bautiful fireball. BUT if the stars align and all is well in the world, it does all work as intended ... yay!

next steps:
	1. make the daemon modular so we can package this and start using command arguments - DONE

goals include:
	1. create a system daemon with systemd
	2. read arbitrary data from a socket and write encrypted stream of arbitrary data to another socket - DONE
