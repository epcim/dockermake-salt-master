#!/bin/bash -e

if [ ! -z $SALT_EXT_PILLAR ]; then
    cp -avr /tmp/${SALT_EXT_PILLAR}.conf /etc/salt/master.d/
fi;

if [[ $# -lt 1 ]] || [[ "$1" == "--"* ]]; then
    exec /usr/bin/salt-master --log-file-level=quiet --log-level=info "$@"
else
    exec "$@"
fi
