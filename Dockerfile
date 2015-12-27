FROM ubuntu:15.04
# Docker builds seems to have a bug related with chfn
RUN ln -s -f /bin/true /usr/bin/chfn
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y git postgresql postgresql-contrib postgresql-client pgadmin3 postgresql-server-dev-all \
	python-dev libgeoip-dev libffi-dev npm curl python python-pip expect
# Player is not needed in the confinement
#RUN curl ftp://ftp.videolan.org/pub/debian/videolan-apt.asc | apt-key add -
#RUN echo "deb ftp://ftp.videolan.org/pub/debian/stable ./" | tee /etc/apt/sources.list.d/libdvdcss.list
#RUN apt-get update
#RUN apt-get install -y vlc vlc-data vlc-plugin-pulse browser-plugin-vlc mplayer2
USER postgres
RUN /etc/init.d/postgresql start &&\
	psql --command "CREATE USER docker WITH SUPERUSER PASSWORD '7yl74Zm4ZpcEsPMilEqUa4vNuRt7jvzm';" &&\
	createdb -O docker security
USER root
RUN useradd -ms /bin/bash docker
USER docker
RUN mkdir -p /home/docker/server
COPY src/server /home/docker/server
USER root
RUN pip install -r /home/docker/server/requirements.txt
RUN mkdir /usr/local/share/ca-certificates/extra
COPY src/server/certificates/rootCA/Security_P3G1_Root.crt /usr/local/share/ca-certificates/extra/
RUN update-ca-certificates --fresh
WORKDIR /home/docker/server/static/master
RUN npm install -g bower
RUN npm install -g gulp
RUN update-alternatives --install /usr/bin/node node /usr/bin/nodejs 99
RUN echo '{ "allow_root": true }' > /root/.bowerrc
RUN npm install
RUN bower install
RUN expect gulp_once.exp
WORKDIR /home/docker/server/database
RUN apt-get install -y python2.7-dev apache2
RUN /etc/init.d/postgresql start && sleep 60 && python storage_api.py
RUN a2enmod ssl rewrite proxy_http headers
COPY src/apache2_confs/default-ssl.conf /etc/apache2/sites-available/default-ssl.conf
RUN ln -s /etc/apache2/sites-available/default-ssl.conf /etc/apache2/sites-enabled/default-ssl.conf
COPY src/apache2_confs/apache2.conf /etc/apache2/apache2.conf
COPY src/apache2_confs/ports.conf /etc/apache2/ports.conf
COPY src/server/certificates/ssl/Security_P3G1_SSL.crt /etc/ssl/certs/
COPY src/server/certificates/ssl/Security_P3G1_SSL_key.pem /etc/ssl/private/
RUN service apache2 restart
EXPOSE 443
WORKDIR /home/docker/server
