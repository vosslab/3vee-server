FROM debian:trixie

ENV DEBIAN_FRONTEND=noninteractive \
    APP_ROOT=/var/www/html/3vee

ARG TARGETARCH

RUN apt-get -qq update && apt-get -qq install -y --no-install-recommends \
    apache2 \
    libapache2-mod-php php php-cli php-mysql php-xml php-gd php-curl \
    python3 python3-dev python3-pip python3-numpy python3-scipy python3-mysqldb python3-pymysql python3-pil python3-setuptools python3-wheel \
    build-essential g++ make git wget curl ca-certificates \
    libssl-dev zlib1g-dev libbz2-dev libsqlite3-dev libncurses5-dev \
    libffi-dev libreadline-dev libgdbm-dev tk-dev uuid-dev \
    libopenblas-dev liblapack-dev gfortran \
    libfreetype6-dev libjpeg62-turbo-dev libpng-dev \
    libmariadb-dev pkg-config \
    mariadb-client netcat-openbsd \
    imagemagick meshlab xvfb xauth xfonts-base libglu1-mesa libxi6 libxrender1 \
    assimp-utils \
    gawk procps unzip bzip2 \
    && rm -rf /var/lib/apt/lists/*

# ensure scripts sourcing /etc/bashrc do not fail noisily
RUN ln -sf /etc/bash.bashrc /etc/bashrc

# matplotlib cache dir (writable for headless rendering)
ENV MPLCONFIGDIR=/tmp/matplotlib-cache
RUN mkdir -p ${MPLCONFIGDIR} && chmod 777 ${MPLCONFIGDIR}

ARG VOSSVOLVOX_REPO=https://github.com/vosslab/vossvolvox.git
ARG VOSSVOLVOX_REF=master
RUN git clone --branch ${VOSSVOLVOX_REF} ${VOSSVOLVOX_REPO} /tmp/vossvolvox

WORKDIR ${APP_ROOT}

# Prestage Python requirements for caching
RUN mkdir -p py
COPY py/requirements.txt py/requirements.txt

ENV PYTHONPATH=${APP_ROOT}/py:${PYTHONPATH}

RUN pip3 install --break-system-packages --no-cache-dir -r py/requirements.txt

# build vossvolvox binaries and install helper data (portable CPU flags)
RUN make -C /tmp/vossvolvox/src CPU_FLAGS="-mtune=generic" all && \
    mkdir -p ${APP_ROOT}/bin ${APP_ROOT}/dat ${APP_ROOT}/sh ${APP_ROOT}/output && \
    cp -a /tmp/vossvolvox/bin/. ${APP_ROOT}/bin/ && \
    cp /tmp/vossvolvox/xyzr/atmtypenumbers ${APP_ROOT}/dat/atmtypenumbers.dat && \
    cp /tmp/vossvolvox/xyzr/atmtypenumbers ${APP_ROOT}/sh/atmtypenumbers && \
    cp /tmp/vossvolvox/xyzr/pdb_to_xyzr.sh ${APP_ROOT}/sh/pdb_to_xyzr.sh && \
    chmod +x ${APP_ROOT}/bin/*.exe ${APP_ROOT}/sh/pdb_to_xyzr.sh && \
    rm -rf /tmp/vossvolvox

# Now copy the rest of the application (PHP/Python/static)
COPY . ${APP_ROOT}

# Remove local pymysql stub so the image uses the real driver package
RUN rm -f ${APP_ROOT}/py/pymysql.py

# Apache configuration
COPY docker/3vee.conf /etc/apache2/sites-available/3vee.conf
RUN set -eux; \
    a2dissite 000-default.conf; \
    PHP_MOD=$(basename /etc/apache2/mods-available/php*.load .load); \
    a2ensite 3vee.conf; \
    a2enmod rewrite "${PHP_MOD}"; \
    printf "ServerName 3vee.local\n" > /etc/apache2/conf-available/servername.conf; \
    a2enconf servername

COPY docker/entrypoint.sh /usr/local/bin/3vee-entrypoint.sh
RUN chmod +x /usr/local/bin/3vee-entrypoint.sh

EXPOSE 80

RUN echo "visit http://localhost:8080/php/index.php"

ENTRYPOINT ["/usr/local/bin/3vee-entrypoint.sh"]
