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

# SET WORK DIRECTORY
RUN mkdir /workdir \
    /workdir/share-virtuoso/ \
    /workdir/out/ \
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
