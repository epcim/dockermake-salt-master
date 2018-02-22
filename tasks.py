#!/bin/env python
# vim: sts=2 ts=2


from invoke import Collection, task
from string import Template
import re

# WIP - use namespace to expose images/targets as inoke tasks
# image = Collection('image')

@task
def clean(ctx):
    ctx.run("rm -rf {}".format(destination))

#TODO, (pre=[clean], post=[push])
@task(default=True)
def all(ctx, dry=False, push=False, dry_targets=False, **kwargs):
    for t, options in ctx.target.items():
        matrix_build(ctx, t, matrix=options['matrix'], require=options['require'],
                     dry=dry, push=push, dry_targets=dry_targets, **kwargs)

@task
def build(ctx, target, require=[], dist='debian', dist_rel='stretch', salt=None, formula_rev=None, push=False, dry=False, dry_targets=False, **kwargs):

    # defaults
    fmt = {'target'      : target,
           'dist'        : dist,
           'dist_rel'    : dist_rel,
           'salt'        : salt,
           'formula_rev' : formula_rev,
           'requires'    : '',
           'tag'         : '',
          }

    # update
    fmt.update({'requires': '{}-{}'.format(fmt['dist'], fmt['dist_rel'])})
    fmt.update(ctx.dockermake)
    kwargs['require'] = require
    kwargs['dist'] = dist
    kwargs['dist_rel'] = dist_rel
    kwargs['salt'] = salt
    kwargs['formula_rev'] = formula_rev
    kwargs['push'] = push
    kwargs['dry'] = True if dry_targets or dry else False
    #_dockermake_args_helper(fmt, salt=salt, formula_rev=formula_rev, push=push, dry=dry, **kwargs)
    _dockermake_args_helper(fmt, **kwargs)

    if dry_targets:
        kw = ''
        for k,v in kwargs.items():
            if k in ['dry', 'dry_targets', 'require']: continue
            if not v: continue
            kw +='--{}'.format(k.replace('_','-'))
            kw += ' ' if v == True else '="{}" '.format(str(v))
        print('invoke build {} --require "{}" {}'.format( target, ' '.join(require), kw))
        if not dry: return

    # execute
    cmd = Template("""
            ${dry}docker-make -f DockerMake.${dist}.yml -u ${repository}: --name ${target} \
            \t-t ${dist}-${dist_rel}${tag} \
            \t--requires ${requires} \
            \t--build-arg SALT_VERSION="${salt}" \
            \t--build-arg SALT_FORMULA_REVISION="${formula_rev}" \
            \t${push} ${options} \
            ${fin}""").safe_substitute(fmt)
    ctx.run(cmd.replace('  ', ''))


## helpers

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
    else:
        build(ctx, target, require, **kwargs)


def _dockermake_args_helper(fmt, salt=False, formula_rev=False, require=[], dry=False, push=False, **kwargs):
    "Additional formating for CLI options"

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
    return fmt

