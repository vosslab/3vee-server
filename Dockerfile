FROM debian:buster

ENV DEBIAN_FRONTEND=noninteractive \
    APP_ROOT=/var/www/html/3vee \
    CHIMERA=/opt/chimera

RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-php php php-cli php-mysql php-xml php-gd php-curl \
    python python-dev python-setuptools python-numpy python-scipy \
    python-mysqldb python-imaging python-tk \
    build-essential g++ make git wget curl ca-certificates \
    mariadb-client netcat-openbsd \
    imagemagick meshlab xvfb xauth xfonts-base libglu1-mesa libxi6 libxrender1 \
    gawk procps unzip bzip2 \
    && rm -rf /var/lib/apt/lists/*

# ensure scripts sourcing /etc/bashrc do not fail noisily
RUN ln -sf /etc/bash.bashrc /etc/bashrc

# install UCSF Chimera (OSMesa build)
RUN curl -L "https://www.cgl.ucsf.edu/chimera/cgi-bin/secure/chimera-get.py?ident=OHeQer2VSqNn9%2BRyrXpc5f1xvkdSQdv50hN50BTlifgjqu%2FK&file=linux_x86_64_osmesa%2Fchimera-1.19-linux_x86_64_osmesa.bin&choice=Notified" \
    -o /tmp/chimera.bin && \
    chmod +x /tmp/chimera.bin && \
    /tmp/chimera.bin --mode unattended --prefix ${CHIMERA} && \
    rm -f /tmp/chimera.bin

WORKDIR ${APP_ROOT}
COPY . ${APP_ROOT}

# mirror historical layout: /var/www/html/3vee/py -> project root
RUN ln -sfn ${APP_ROOT} ${APP_ROOT}/py

# build vossvolvox binaries and install helper data
RUN make -C vossvolvox/src all && \
    mkdir -p ${APP_ROOT}/bin ${APP_ROOT}/dat ${APP_ROOT}/sh ${APP_ROOT}/output && \
    cp -a vossvolvox/bin/. ${APP_ROOT}/bin/ && \
    cp vossvolvox/mapman/lx_mapman ${APP_ROOT}/bin/mapman_linux.exe && \
    cp vossvolvox/xyzr/atmtypenumbers ${APP_ROOT}/dat/atmtypenumbers.dat && \
    cp vossvolvox/xyzr/atmtypenumbers ${APP_ROOT}/sh/atmtypenumbers && \
    cp vossvolvox/xyzr/pdb_to_xyzr.sh ${APP_ROOT}/sh/pdb_to_xyzr.sh && \
    chmod +x ${APP_ROOT}/bin/*.exe ${APP_ROOT}/bin/mapman_linux.exe ${APP_ROOT}/sh/pdb_to_xyzr.sh

# Apache configuration
RUN a2dissite 000-default.conf && \
    printf "%s\n" "<VirtualHost *:80>" \
    "    DocumentRoot ${APP_ROOT}" \
    "    <Directory ${APP_ROOT}>" \
    "        Options Indexes FollowSymLinks" \
    "        AllowOverride All" \
    "        Require all granted" \
    "    </Directory>" \
    "    ErrorLog /var/log/apache2/3vee-error.log" \
    "    CustomLog /var/log/apache2/3vee-access.log combined" \
    "</VirtualHost>" > /etc/apache2/sites-available/3vee.conf && \
    a2ensite 3vee.conf && \
    a2enmod php7.3 rewrite && \
    printf "ServerName 3vee.local\n" > /etc/apache2/conf-available/servername.conf && \
    a2enconf servername

COPY docker/entrypoint.sh /usr/local/bin/3vee-entrypoint.sh
RUN chmod +x /usr/local/bin/3vee-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/3vee-entrypoint.sh"]
