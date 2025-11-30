FROM debian:trixie

ENV DEBIAN_FRONTEND=noninteractive \
    APP_ROOT=/var/www/html/3vee \
    CHIMERA=/opt/chimera \
    EMANDIR=/usr/local/EMAN

ARG TARGETARCH

RUN apt-get -qq update && apt-get -qq install -y --no-install-recommends \
    apache2 \
    libapache2-mod-php php php-cli php-mysql php-xml php-gd php-curl \
    python3 python3-dev python3-pip python3-numpy python3-scipy python3-mysqldb python3-pil python3-setuptools python3-wheel \
    build-essential g++ make git wget curl ca-certificates \
    libssl-dev zlib1g-dev libbz2-dev libsqlite3-dev libncurses5-dev \
    libffi-dev libreadline-dev libgdbm-dev tk-dev uuid-dev \
    libopenblas-dev liblapack-dev gfortran \
    libfreetype6-dev libjpeg62-turbo-dev libpng-dev \
    libmariadb-dev pkg-config \
    mariadb-client netcat-openbsd \
    imagemagick meshlab xvfb xauth xfonts-base libglu1-mesa libxi6 libxrender1 \
    gawk procps unzip bzip2 \
    && rm -rf /var/lib/apt/lists/*

# ensure scripts sourcing /etc/bashrc do not fail noisily
RUN ln -sf /etc/bash.bashrc /etc/bashrc

# install UCSF Chimera (OSMesa build)
RUN if [ "${TARGETARCH}" = "amd64" ]; then \
      curl -L "https://www.cgl.ucsf.edu/chimera/cgi-bin/secure/chimera-get.py?ident=OHeQer2VSqNn9%2BRyrXpc5f1xvkdSQdv50hN50BTlifgjqu%2FK&file=linux_x86_64_osmesa%2Fchimera-1.19-linux_x86_64_osmesa.bin&choice=Notified" \
        -o /tmp/chimera.bin && \
      chmod +x /tmp/chimera.bin && \
      /tmp/chimera.bin --mode unattended --prefix ${CHIMERA} && \
      rm -f /tmp/chimera.bin; \
    else \
      echo "Skipping Chimera install on ${TARGETARCH} (installer is amd64-only)"; \
    fi

# install EMAN 1.9 (prebuilt cluster build) - amd64 only
RUN if [ "${TARGETARCH}" = "amd64" ]; then \
      curl -L "https://github.com/leginon-org/appion-redmine-files/raw/heads/main/eman-linux-x86_64-cluster-1.9.tar.gz" \
        -o /tmp/eman.tar.gz && \
      tar -xzf /tmp/eman.tar.gz -C /tmp && \
      mv /tmp/EMAN ${EMANDIR} && \
      cd ${EMANDIR} && \
      ./eman-installer && \
      rm -f /tmp/eman.tar.gz; \
    else \
      echo "Skipping EMAN install on ${TARGETARCH} (archive is amd64-only)"; \
      mkdir -p ${EMANDIR}; \
    fi

ENV PATH=${EMANDIR}/bin:${PATH} \
    LD_LIBRARY_PATH=${EMANDIR}/lib:${LD_LIBRARY_PATH} \
    PYTHONPATH=${EMANDIR}/lib:${PYTHONPATH}

ARG VOSSVOLVOX_REPO=https://github.com/vosslab/vossvolvox.git
ARG VOSSVOLVOX_REF=master
RUN git clone --depth 1 --branch ${VOSSVOLVOX_REF} ${VOSSVOLVOX_REPO} /tmp/vossvolvox

WORKDIR ${APP_ROOT}
COPY . ${APP_ROOT}

# build vossvolvox binaries and install helper data
RUN make -C /tmp/vossvolvox/src all && \
    mkdir -p ${APP_ROOT}/bin ${APP_ROOT}/dat ${APP_ROOT}/sh ${APP_ROOT}/output && \
    cp -a /tmp/vossvolvox/bin/. ${APP_ROOT}/bin/ && \
    cp /tmp/vossvolvox/mapman/lx_mapman ${APP_ROOT}/bin/mapman_linux.exe && \
    cp /tmp/vossvolvox/xyzr/atmtypenumbers ${APP_ROOT}/dat/atmtypenumbers.dat && \
    cp /tmp/vossvolvox/xyzr/atmtypenumbers ${APP_ROOT}/sh/atmtypenumbers && \
    cp /tmp/vossvolvox/xyzr/pdb_to_xyzr.sh ${APP_ROOT}/sh/pdb_to_xyzr.sh && \
    chmod +x ${APP_ROOT}/bin/*.exe ${APP_ROOT}/bin/mapman_linux.exe ${APP_ROOT}/sh/pdb_to_xyzr.sh && \
    rm -rf /tmp/vossvolvox

# Apache configuration
RUN set -eux; \
    a2dissite 000-default.conf; \
    cat <<'EOF' > /etc/apache2/sites-available/3vee.conf
<VirtualHost *:80>
    DocumentRoot /var/www/html/3vee
    <Directory /var/www/html/3vee>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog /var/log/apache2/3vee-error.log
    CustomLog /var/log/apache2/3vee-access.log combined
</VirtualHost>
EOF

RUN set -eux; \
    PHP_MOD=$(basename /etc/apache2/mods-available/php*.load .load); \
    a2ensite 3vee.conf; \
    a2enmod rewrite "${PHP_MOD}"; \
    printf "ServerName 3vee.local\n" > /etc/apache2/conf-available/servername.conf; \
    a2enconf servername

COPY docker/entrypoint.sh /usr/local/bin/3vee-entrypoint.sh
RUN chmod +x /usr/local/bin/3vee-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/3vee-entrypoint.sh"]
