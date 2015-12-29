sudo /etc/init.d/postgresql start
sudo service apache2 start
cd src/server/database;
until sudo python storage_api.py; do echo "Waiting for database to startup"; sleep 30; done
cd ..;
sudo python server.py
