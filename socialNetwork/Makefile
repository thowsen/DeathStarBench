
# sudo apt install thrift-compiler libthrift-0.16.0

# all: thrift nuke

cpp: nuke
	docker build . -t base-socialnetwork --no-cache 

thrift: 
	thrift -r --gen cpp social_network.thrift
# thrift -r --gen lua social_network.thrift

nuke: 
	docker stop $$(docker ps -aq)
	docker rm $$(docker ps -aq)
	docker image rm $$(docker image ls -q)