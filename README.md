# docker-salt-formulas
Docker image builds for container with pre-installed salt, salt-formulas and ecosystem

# Requisites

* DockerMake (https://github.com/avirshup/DockerMake)
* pyInvoke (https://github.com/pyinvoke/invoke)

Install:

    pip install dockermake pyinvoke

    pip install -e git+https://github.com/avirshup/DockerMake#egg=dockermake
    pip install -e git+https://github.com/pyinvoke/invoke#egg=invoke

# Usage

    invoke -l
    invoke all --dry
    invoke all --push
 
    WIP:
    invoke target --target saltstack --dry --push

