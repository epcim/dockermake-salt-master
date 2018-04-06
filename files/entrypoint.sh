#!/bin/bash -e

function log_info() {
    echo "[INFO] $*"
}

if [ ! -z $SALT_EXT_PILLAR ]; then
    cp -avr /tmp/salt/${SALT_EXT_PILLAR}.conf /etc/salt/master.d/
fi;

# Enable API
if [[ $SALT_API -eq 1 ]]; then
  cp -avr /tmp/salt/auth.conf /etc/salt/master.d/
  cp -avr /tmp/salt/api.conf  /etc/salt/master.d/
  if [ -z $SALT_API_PASSWORD ]; then
      SALT_API_PASSWORD=$(pwgen -1 8)
      log_info "No SALT_API_PASSWORD provided, using auto-generated ${SALT_API_PASSWORD}"
  fi
  log_info "Setting password for user salt"
  echo "salt:${SALT_API_PASSWORD}" | chpasswd

  log_info "Starting salt-api"
  /usr/bin/salt-api --log-file-level=quiet --log-level=info -d
fi


if [[ $# -lt 1 ]] || [[ "$1" == "--"* ]]; then
    exec /usr/bin/salt-master --log-file-level=quiet --log-level=info "$@"
else
    exec "$@"
fi

# vim: sts=2 ts=2 sw=2 ft=bash
