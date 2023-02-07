

cpp: nuke
	docker build . -t base-socialnetwork --no-cache 

nuke: 
	docker stop $$(docker ps -aq)
	docker rm $$(docker ps -aq)
	docker image rm $$(docker image ls -q)