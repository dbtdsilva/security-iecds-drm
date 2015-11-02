#/bin/bash
sudo apt-get install postgresql postgresql-contrib postgresql-client pgadmin3
sudo -u postgres psql security -c "\password"
# 7yl74Zm4ZpcEsPMilEqUa4vNuRt7jvzm
sudo -u postgres createdb security