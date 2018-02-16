# docker-salt-formulas
Predictive, layered - docker image builds with pre-installed salt, salt-formulas, ecosystem...

Images are available at docker hub:

* https://hub.docker.com/r/epcim/salt-formulas/tags/

NOTE: Once finished I count to move the repo under https://github.com/salt-formulas

## Requisites

* DockerMake (https://github.com/avirshup/DockerMake)
* pyInvoke (https://github.com/pyinvoke/invoke)

Install:

    pip install dockermake pyinvoke

    pip install -e git+https://github.com/avirshup/DockerMake#egg=dockermake
    pip install -e git+https://github.com/pyinvoke/invoke#egg=invoke

## Usage

    inv --list
    inv all --dry
    inv all --push
    inv all --push -w    # warnings only: to survive on errors
 
    WIP:
    invoke target --target saltstack --dry --push



## TODO

TBD - grep sources for TODO/FIXME/NOTE.
