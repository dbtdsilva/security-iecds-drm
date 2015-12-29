#!/bin/bash
if [[ "$#" -ne "1" || ("$1" != "start" && "$1" != "stop" && "$1" != "status" && "$1" != "reset") ]]; then
	echo " * Usage: ./iecds-server [start|stop|status|reset]"
	echo " ** Reset will create the docker image again, erasing the database"
	exit
fi

images_count=`docker images | grep "ubuntu/iecds_server" | wc -l`
if [ "$images_count" -eq "1" ]; then
	echo " * You must build the docker image for iecds-server first (Advice: use install.sh script on root folder)"
	exit
fi

running=`docker ps | grep "iecds_server" | wc -l`
exists=`docker ps -a | grep "iecds_server" | wc -l`

if [ "$1" = "status" ]; then
	if [[ "$exists" -eq "0" || "$running" -eq "0" ]]; then
		echo "* Docker image is not running."
	else
		echo "* Docker image is running."
		docker ps | grep "iecds_server"
	fi
elif [ "$1" = "start" ]; then
	if [ "$exists" -eq "0" ]; then
		sudo docker run --name=iecds_server --privileged=true -d -p 443:443 ubuntu/iecds-server /bin/bash -c "/etc/init.d/postgresql start && service apache2 start && cd /home/docker/server/database; until python storage_api.py; do echo 'sleep 30 seconds'; sleep 30; done && cd /home/docker/server; python server.py"
	else
		sudo docker start iecds_server
	fi
elif [ "$1" = "stop" ]; then
	sudo docker stop iecds_server
elif [ "$1" = "reset" ]; then
	if [ "$running" -eq "1" ]; then
		sudo docker stop iecds_server
	fi

	if [ "$exists" -eq "1" ]; then
		sudo docker rm iecds_server
	fi
	sudo docker run --name=iecds_server --privileged=true -d -p 443:443 ubuntu/iecds-server /bin/bash -c "/etc/init.d/postgresql start && service apache2 start && cd /home/docker/server/database; until python storage_api.py; do echo 'sleep 30 seconds'; sleep 30; done && cd /home/docker/server; python server.py"
fi
