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
    pip3 install rdflib==5.0.0 &&\
    pip3 install numpy==1.18.2 &&\
    pip3 install elementpath==1.4.3 &&\
    pip3 install requests==2.23.0 &&\
    pip3 install pandas==1.0.3 &&\
    apt remove -y libxml2 libxml2-dev libxslt1-dev gcc &&\
    apt autoremove -y &&\
    apt clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# INSTALL R AND PACKAGES
RUN apt update && \
    apt-get install -y r-base

RUN R -e "install.packages('optparse', repos = 'http://cran.us.r-project.org')"
RUN R -e "install.packages('bigstatsr', repos = 'http://cran.us.r-project.org')"
RUN R -e "install.packages('parallel', repos = 'http://cran.us.r-project.org')"
RUN R -e "install.packages('foreach', repos = 'http://cran.us.r-project.org')"
RUN R -e "install.packages('R.utils', repos = 'http://cran.us.r-project.org')"

# SET WORK DIRECTORY
RUN mkdir /workdir \
    /workdir/share-virtuoso/ \
    /workdir/out/ \
    /workdir/config/ \
    /workdir/app \
    /workdir/data \
    /workdir/app/SBML_upgrade \
    /workdir/app/build_RDF_store \
    /workdir/app/metab2mesh \
    /workdir/app/metab2mesh/post-processes \
    /workdir/app/metab2mesh/SPARQL \
    /workdir/app/ChemOnt
    

# COPY FILES
COPY app/*.py /workdir/app/

COPY app/SBML_upgrade/*.py /workdir/app/SBML_upgrade/
COPY app/SBML_upgrade/table_info.csv /workdir/app/SBML_upgrade/

COPY app/build_RDF_store/*.py /workdir/app/build_RDF_store/

COPY app/metab2mesh/*.py /workdir/app/metab2mesh/
COPY app/metab2mesh/post-processes/* /workdir/app/metab2mesh/post-processes/
COPY app/metab2mesh/SPARQL/*.py /workdir/app/metab2mesh/SPARQL/

COPY app/ChemOnt/*.py /workdir/app/ChemOnt/

# SET WORK DIR.
WORKDIR /workdir

# TEST CMD
# python3 Get_CID_PMID_associations.py

# SET ENTRYPOINT
# ENTRYPOINT ["python3", ""]
