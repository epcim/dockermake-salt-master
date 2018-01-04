#FROM epcim/salty-whales:xenial-2017.7
FROM ubuntu:latest
MAINTAINER Petr Michalec "<epcim@apealive.net>"

# ARGs
#

ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true \
    LANG=C.UTF-8 \
    LANGUAGE=$LANG \
    TZ=Etc/UTC

RUN echo "Layer Ubuntu upgrade" \
 && apt-get update -q \
 && apt-get upgrade -qy

RUN echo "Layer salt prereq. and common pkgs" \
 && apt-get install -qy \
      vim-tiny \
      curl \
      git \
      sudo \
      python-pip \
      python-wheel \
      python-setuptools \
      python-dev \
      zlib1g-dev \
      apt-transport-https \
      netcat \
      ca-certificates \
      locales \
      tzdata \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache /home/*/.cache

RUN echo "Layer salt-formulas"  &&\
        set -xev &&\
        # boostrap.sh options
        export BOOTSTRAP_SALTSTACK_OPTS="-dX ${salt_version:-git develop}" &&\
        export DISTRIB_REVISION="${salt_formula_revision:-nightly}" &&\
        # configure git/ssh
        git config --global user.email || git config --global user.email 'ci@ci.local' &&\
        git config --global user.name || git config --global user.name 'CI' &&\
        mkdir -p /root/.ssh/ &&\
        touch /root/.ssh/config &&\
        touch /root/.ssh/known_hosts &&\
        # install ingeration/formulas/other salt prereq
        pip install setuptools ruamel.yaml &&\
        # configure salt
        ## install shared reclass model (optional)
        mkdir -p /srv/salt/reclass/classes/system &&\
        git clone https://github.com/Mirantis/reclass-system-salt-model /srv/salt/reclass/classes/system &&\
        ## install shared salt-class model (optional)
        mkdir -p /srv/salt/reclass/saltclass/system &&\
        git clone https://github.com/epcim/saltclass-system /srv/salt/saltclass/classes/system &&\
        ## scripted salt-formulas bootstrap (optional)
        git clone https://github.com/salt-formulas/salt-formulas-scripts /srv/salt/scripts &&\
        bash -c "echo 'salt-formulas bootstrap' &&\
        rm -f /etc/apt/sources.list.d/*salt*.list || true &&\
        source /srv/salt/scripts/bootstrap.sh && cd /srv/salt/scripts &&\
        source_local_envs &&\
        configure_pkg_repo &&\
        system_config_salt_modules_prereq &&\
        install_reclass develop &&\
        system_config_ssh_conf" &&\
        curl -L https://bootstrap.saltstack.com | $SUDO sh -s -- ${BOOTSTRAP_SALTSTACK_OPTS} &&\
        # pre-install stable salt-formulas (optional)
        apt-get install -qy salt-formula-* &&\
        # saltclass fixup (optional)
        cp -a /usr/share/salt-formulas/reclass /usr/share/salt-formulas/saltclass &&\
        for i in $(grep -r -e '^applications:' -e '^parameters:' -l ${SALT_CLASS_SERVICE:-/usr/share/salt-formulas/saltclass/service}); do \
          sed -i 's/applications:/states:/g;s/parameters:/pillars:/g' $i; \
        done &&\
        # clean up
        apt-get clean &&\
        apt-get autoclean &&\
        apt-get autoremove -y &&\
        rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache /home/*/.cache  /var/tmp/* /tmp/*

VOLUME ["/etc/salt/pki", "/srv/salt/env", "/srv/salt/pillar", "/srv/salt/reclass", "/srv/salt/saltclass"]
EXPOSE 4505 4506

#TODO, mind, no entrypoint to start salt master service
