#/bin/bash
sudo apt-get install postgresql postgresql-contrib postgresql-client pgadmin3 postgresql-server-dev-9.4 \
	python-dev libgeoip-dev libffi-dev npm curl
curl ftp://ftp.videolan.org/pub/debian/videolan-apt.asc | sudo apt-key add -
echo "deb ftp://ftp.videolan.org/pub/debian/stable ./" | sudo tee /etc/apt/sources.list.d/libdvdcss.list
sudo apt-get update
sudo apt-get install vlc vlc-data vlc-plugin-pulse browser-plugin-vlc mplayer2 
sudo apt-get install ubuntu-restricted-extras
sudo -u postgres createdb security
sudo -u postgres psql security -c "\password"
# 7yl74Zm4ZpcEsPMilEqUa4vNuRt7jvzm
pip install -r src/server/requirements.txt
sudo mkdir /usr/share/ca-certificates/extra
sudo cp src/server/certificates/rootCA/Security_P3G1_Root.crt /usr/share/ca-certificates/extra/
sudo dpkg-reconfigure ca-certificates
cd src/server/static/master
sudo npm install
sudo npm install -g bower
sudo npm install -g gulp
bower install
echo "\n\n\tLet gulp loads to generate app.js and base.js\n"
gulp
cd ../../database
python storage-api.py
