# call parent container
FROM ubuntu:20.04

# set author
MAINTAINER Nils Paulhe <nils.paulhe@inrae.fr>

### 
### [CONTAINER CORE FUNCTIONS]: 
###   install an environement for this Git project
### [NOTE] 
###  - has a custom work directory in `/workdir`.
### 

# USER SETTINGS
ARG USER_ID
ARG GROUP_ID

RUN addgroup --gid $GROUP_ID user
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user

# SETTINGS
ARG DEBIAN_FRONTEND=noninteractive

# INSTALL STUFF
RUN apt update && \
    apt install -y \
    wget curl vim htop sshpass \
    libxml2 libxml2-dev libxslt1-dev gcc \
    python3 python3-dev python3-setuptools python3-pip &&\
    pip3 install pyparsing==2.* &&\
    pip3 install eutils==0.6.0 &&\
    pip3 install rdflib==6.0.0 &&\
    pip3 install numpy==1.18.2 &&\
    pip3 install elementpath==1.4.3 &&\
    pip3 install requests==2.23.0 &&\
    pip3 install BeautifulSoup4==4.9.3 &&\
    pip3 install pandas==1.0.3 &&\
    apt remove -y libxml2 libxml2-dev libxslt1-dev gcc &&\
    apt autoremove -y &&\
    apt clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# INSTALL R AND PACKAGES
RUN apt update && \
    apt-get install -y r-base

# RUN R -e "install.packages('optparse', repos = 'http://cran.us.r-project.org')"
# RUN R -e "install.packages('bigstatsr', repos = 'http://cran.us.r-project.org')"
# RUN R -e "install.packages('parallel', repos = 'http://cran.us.r-project.org')"
# RUN R -e "install.packages('foreach', repos = 'http://cran.us.r-project.org')"
# RUN R -e "install.packages('R.utils', repos = 'http://cran.us.r-project.org')"
# RUN R -e "install.packages('readr', repos = 'http://cran.us.r-project.org')"

# INSTALL JAVA: https://github.com/datawire/docker-debian-openjdk-11/blob/master/Dockerfile

WORKDIR /opt
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
    && curl \
        -L \
        -o openjdk.tar.gz \
        https://download.java.net/java/GA/jdk11/13/GPL/openjdk-11.0.1_linux-x64_bin.tar.gz \
    && mkdir jdk \
    && tar zxf openjdk.tar.gz -C jdk --strip-components=1 \
    && rm -rf openjdk.tar.gz \
    && apt-get -y --purge autoremove curl \
    && ln -sf /opt/jdk/bin/* /usr/local/bin/ \
    && rm -rf /var/lib/apt/lists/* \
    && java  --version \
    && javac --version \
    && jlink --version

# SET WORK DIRECTORY
RUN mkdir /workdir \
    /workdir/share-virtuoso/ \
    /workdir/out/ \
    /workdir/config/ \
    /workdir/app \
    /workdir/workflow \
    /workdir/logs-app
    

# COPY FILES
COPY app /workdir/app
COPY workflow /workdir/workflow

# REMOVE PYCACHE
RUN find /workdir/app | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

# ADD PERMISSIONS
RUN chown -R $USER_ID:$GROUP_ID /workdir

# SET WORK DIR.
USER user
WORKDIR /workdir

# SET ENTRYPOINT
# ENTRYPOINT ["python3", ""]
