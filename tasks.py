#!/bin/env python
# vim: sts=2 ts=2


from invoke import Collection, task
from string import Template
import re

def matrix_build(ctx, target, matrix=[], require=[], **kwargs):
    if 'dist' in matrix:
        m = matrix[:]
        m.remove('dist')
        for dist, r in ctx.matrix.dist.items():
            for dist_rel in r:
                matrix_build(ctx, target, matrix=m, require=require, dist=dist, dist_rel=dist_rel, **kwargs)
        return 0
    if 'salt' in matrix:
        m = matrix[:]
        m.remove('salt')
        for salt in ctx.matrix.salt:
            matrix_build(ctx, target, matrix=m, require=require, salt=salt, **kwargs)
        return 0
    if 'salt-formulas' in matrix:
        m = matrix[:]
        m.remove('salt-formulas')
        for formula_rev in ctx.matrix['salt-formulas']:
            matrix_build(ctx, target, matrix=m, require=require, formula_rev=formula_rev, **kwargs)
        return 0
    # finally
    build(ctx, target, require, **kwargs)



#TODO, (pre=[clean], post=[push])
@task(default=True)
def all(ctx, dry=False, push=False, **kwargs):
    for t, options in ctx.target.items():
        matrix_build(ctx, t, matrix=options['matrix'], require=options['require'], dry=dry, push=push, **kwargs)


# WIP - not yet ready, finally it should be merged with @task 'all'
# WIP - use namespace to expose images/targets as inoke tasks
#image = Collection('image')
@task
def target(ctx, t=None):
    for tt, options in ctx.target.items():
        if tt is None:
            #image.add_task(matrix_build, name=t)
            matrix_build(ctx, t, matrix=options['matrix'], require=options['require'])
        else:
            if tt == t :
                matrix_build(ctx, t, matrix=options['matrix'], require=options['require'])


@task
def clean(ctx):
    ctx.run("rm -rf {}".format(destination))


@task
def build(ctx, target, require=[], dist='debian', dist_rel='stretch', salt=None, formula_rev=None, dry=False, push=False, **kwargs):
    fmt = {'target'      : target,
           'dist'        : dist,
           'dist_rel'    : dist_rel,
           'salt'        : salt,
           'formula_rev' : formula_rev,
           'requires'    : '{}-{}'.format(dist, dist_rel),
           'tag'         : '',
          }
    fmt.update(ctx.dockermake)

    # Additional formating
    ## compose image tag
    if salt:
        s = str(salt).replace(' ', '').strip()
        s = s.replace('stable', '') if len(s.replace('stable', '')) > 0  else s
        s = s.replace('gitv', 'git') if len(s.replace('gitv', 'git')) > 0  else s
        fmt['tag'] += '-salt-{}'.format(s)
    if formula_rev:
        fmt['tag'] += '-formula-{}'.format(formula_rev)
    ## additional layers
    if len(require) > 0:
        fmt['requires'] += ' ' + ' '.join(require)
    ## catch git develop || git <revision>
    if salt and (not str(salt).startswith(('stable')) and not str(salt).startswith(('git'))):
        fmt['salt'] = 'git ' + str(fmt['salt'])
    ## dry mode echo cmds only
    if dry:
        fmt['dry'] = 'echo \''
        fmt['fin'] = '\''
    ## pusht to registry
    if push:
        fmt['push'] = '--push-to-registry'
    ## add docker-make cli arguments/options specified in invoke.yml
    if ctx.dockermake.get('options', False):
        fmt['opts'] = ctx.dockermake.options

    # execute
    cmd = Template("""
            ${dry}docker-make -f DockerMake.${dist}.yml -u ${repository}: --name ${target} \
            \t-t ${dist}-${dist_rel}${tag} \
            \t--requires ${requires} \
            \t--build-arg SALT_VERSION="${salt}" \
            \t--build-arg SALT_FORMULA_REVISION="${formula_rev}" \
            \t${push} ${opts} \
            ${fin}""").safe_substitute(fmt)
    ctx.run(cmd.replace('  ', ''))
    # finally remove non-matched vars
    #ctx.run(re.sub('\$[_a-zA-Z0-9]+', '', cmd.replace('  ', '')))

