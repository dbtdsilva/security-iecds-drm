#/bin/bash
sudo apt-get install postgresql postgresql-contrib postgresql-client pgadmin3 postgresql-server-dev-9.4 \
	python-dev libgeoip-dev libffi-dev
sudo -u postgres createdb security
sudo -u postgres psql security -c "\password"
# 7yl74Zm4ZpcEsPMilEqUa4vNuRt7jvzm
pip install -r src/server/requirements.txt
sudo mkdir /usr/share/ca-certificates/extra
sudo cp src/server/certificates/rootCA/Security_P3G1_Root.crt /usr/share/ca-certificates/extra/
sudo dpkg-reconfigure ca-certificates
