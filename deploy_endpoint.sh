#!/usr/bin/env bash

#############################################################################################
# define variables and set default values
BASEDIR=$(dirname $0)

nohup_pid="/tmp/deploy_endpoint.pid";
nohup_log="/tmp/deploy_endpoint.log";
nohup_cmd="$BASEDIR/w.sh";

pydio_token="";

#############################################################################################
# define functions

#
# AffiUsage: print help
#
affiUsage () {
  echo "Usage : deploy_endpoint.sh --pydio_token setThePydioToken ";
  echo "	-h, --help:  print this help message ";
  echo "	-pt, --pydio_token the pydio token to set (mandatory)";
}

#
# Kill old nohup
#   kill the process of "deploy endpoint" latest launch
#
kill_old_nohup () {
    echo "[info] testing if script already launched...";
    if test -f "$nohup_pid"; then
        pid=$(<$nohup_pid)
        echo "[WARNING] script already launched with pid=$pid. KILL IT!!! ☹";
        kill -9 $pid
        rm $nohup_pid
        echo "[info] old version of the script has been killed.";
    else
        echo "[info] curent script is not already launched in 'nohup mode' ☺";
    fi
}

#
# Launch new nohup
#   Create and launch new nohup for "deploy endpoint" process
#
launch_new_nohup () {
    echo "[info] launch nohup command to deploy endpoint; log file is '$nohup_log' ";
    nohup $nohup_cmd $pydio_token > $nohup_log 2>&1 &
    # get pid and save into file
    echo $! > $nohup_pid
    # get pid from file
    pid=$(<$nohup_pid)
    echo "[info] deploy endpoint script has been launch with pid=$pid ☺";
}

#############################################################################################
# read arvg
while [[ $# -gt 0 ]]
do
opt="$1"
case $opt in
    ""|"-h"|"--help")
    affiUsage
    exit 0;
    ;;
    "-pt"|"--pydio_token,")
    pydio_token="$2"
    shift # past argument
    ;;
#     --default)
#     DEFAULT=YES
#     ;;
    *)
# unknown option -> ignore
    ;;
esac
shift
done

#############################################################################################
# script actions

# test if param "pydio token" is set
if [[ "$pydio_token" != "" ]];then
    # normal script launch
    kill_old_nohup
    launch_new_nohup
    exit 0;
else
    # die is tears
    echo "[WARNING] missing mandatory parameter: 'pydio token' ☹";
    affiUsage;
    exit 1;
fi

exit 0;
