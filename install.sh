#!/usr/bin/env bash
sudo apt-get install postgresql postgresql-contrib postgresql-client pgadmin3 postgresql-server-dev-9.4 \
	python-dev libgeoip-dev libffi-dev npm curl python python-pip apache2
curl ftp://ftp.videolan.org/pub/debian/videolan-apt.asc | sudo apt-key add -
echo "deb ftp://ftp.videolan.org/pub/debian/stable ./" | sudo tee /etc/apt/sources.list.d/libdvdcss.list
sudo apt-get update
sudo apt-get install vlc vlc-data vlc-plugin-pulse browser-plugin-vlc mplayer2 
sudo apt-get install ubuntu-restricted-extras
sudo -u postgres psql --command "CREATE USER docker WITH SUPERUSER PASSWORD '7yl74Zm4ZpcEsPMilEqUa4vNuRt7jvzm';"
sudo -u postgres createdb -O docker security
pip install -r src/server/requirements.txt
sudo mkdir /usr/local/share/ca-certificates/extra
sudo cp src/server/certificates/rootCA/Security_P3G1_Root.crt /usr/local/share/ca-certificates/extra/
sudo update-ca-certificates --fresh
cd src/server/static/master
sudo npm install -g bower
sudo npm install -g gulp
sudo update-alternatives --install /usr/bin/node node /usr/bin/nodejs 99
sudo npm install
bower install
expect gulp_once.exp
cd ../../database
python storage_api.py
sudo a2enmod ssl rewrite proxy_http headers
cd ../../..
sudo cp src/apache2_confs/default-ssl.conf /etc/apache2/sites-available/default-ssl.conf
if [ ! -f /etc/apache2/sites-enabled/default-ssl.conf ]; then
    sudo ln -s /etc/apache2/sites-available/default-ssl.conf /etc/apache2/sites-enabled/default-ssl.conf
fi
sudo cp src/apache2_confs/apache2.conf /etc/apache2/apache2.conf
sudo cp src/apache2_confs/ports.conf /etc/apache2/ports.conf
sudo cp src/server/certificates/ssl/Security_P3G1_SSL.crt /etc/ssl/certs/
sudo cp src/server/certificates/ssl/Security_P3G1_SSL_key.pem /etc/ssl/private/
sudo service apache2 restart
cd src/player
sudo apt-get install python-tk python-imaging-tk
