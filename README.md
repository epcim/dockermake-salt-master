# docker-salt-formulas
Predictive, layered - docker image builds with pre-installed salt, salt-formulas, ecosystem...

Images are available at docker hub:

* https://hub.docker.com/r/epcim/salt/tags/

NOTE: Once finished I count to move the repo under https://github.com/salt-formulas

## Requisites

* DockerMake (https://github.com/avirshup/DockerMake)
* pyInvoke (https://github.com/pyinvoke/invoke)

Install:

    # install from Pipenv[.lock]
    pipenv --two
    pippnv install
    pipenv shell

    # or alternatively with pip, ...
    pip install dockermake pyinvoke
    pip install -e "git+https://github.com/avirshup/DockerMake#egg=dockermake"
    pip install -e "git+https://github.com/pyinvoke/invoke#egg=invoke"

## Build

    inv --list

    inv all --dry
    inv all --dry-targets

    # build whole matrix
    inv all --push
    inv all --push -w    # warnings only: to survive on errors
 
    # individual targets
    # invoke [target] [--[args][=value]] [--push]
    invoke all --dry-targets --filter "{'target':'saltstack', 'salt': 'stable'}"
    invoke build wheelhouse --require "salt salt-formulas wheel" --dist=debian --dist-rel=stretch --salt=develop --formula-rev=nightly --push

## Targets

Images are published on docker hu under `epcim/salt` and build with a tag notation:

      <target>-<distribution>-<distribution codename>[-salt-<salt version>[-formula-<formula version>]]

An example:

      docker.io/epcim/salt:saltmaster-ubuntu-xenial-salt-stable-formula-nightly

I can easily switch to docker-hub organization and build images under it's own namespace with tags as it's more common (lates, date, version number).

In my use-case (CI) I am always interested in latest version of the containers in the upstream and I rather advise you to build or at least fetch your
own copy and tag it yourself at you own repo and frequency as required.

Volumes:

  TBD

Usage:

  TBD

### saltstack[-ubuntu-xenial-salt-stable]

Target with pre-installed salt and common dependencies.


### saltmaster[-ubuntu-xenial-salt-stable-formula-nightly]

TBD

Target with pre-installed salt, formulas form gh:salt-formulas and gh:saltstack formulas (if duplicit then skipped, sources and the order is configurable).
Tini serves salt-master process.

### saltmaster-reclass[-ubuntu-xenial-salt-stable-formula-nightly]

TBD

Target with pre-installed salt, formulas form gh:salt-formulas and gh:saltstack formulas (if duplicit then skipped, sources and the order is configurable).
Reclass is installed form gh:salt-formulas/reclass and pre-configured.
Tini serves salt-master process.

### Other To Be Added

TBD
