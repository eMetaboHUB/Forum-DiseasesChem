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

# SETTINGS
ARG DEBIAN_FRONTEND=noninteractive

# INSTALL STUFF
RUN apt update && \
    apt install -y \
    wget curl \
    libxml2 libxml2-dev libxslt1-dev gcc \
    python3 python3-dev python3-setuptools python3-pip &&\
    pip3 install eutils==0.6.0 &&\
    pip3 install rdflib==4.2.2 &&\
    pip3 install numpy==1.18.2 &&\
    pip3 install elementpath==1.4.3 &&\
    pip3 install requests==2.23.0 &&\
    apt remove -y libxml2 libxml2-dev libxslt1-dev gcc &&\
    apt autoremove -y &&\
    apt clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
    
# SET WORK DIRECTORY
RUN mkdir /workdir \
    /workdir/data \
     /workdir/__pycache__/ \
    /workdir/data/HumanGEM

# COPY FILES
COPY app/*.py /workdir/
COPY app/__pycache__/* /workdir/__pycache__/
COPY docker_resources/HumanGEM.ttl /workdir/data/HumanGEM/HumanGEM.ttl

# SET WORK DIR.
WORKDIR /workdir

# TEST CMD
# python3 Get_CID_PMID_associations.py

# SET ENTRYPOINT
# ENTRYPOINT ["python3", ""]
