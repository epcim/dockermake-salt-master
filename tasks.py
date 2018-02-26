#!/bin/env python
# vim: sts=2 ts=2 sw=2


from invoke import Collection, task
from string import Template
import re
import ast

# TODOs:
# - WIP - use namespace to expose images/targets as inoke tasks # image = Collection('image')
# - add option from cli to override matrix configuration stored in invoke.yml

@task
def clean(ctx):
    ctx.run("rm -rf {}".format(destination))

#TODO, (pre=[clean], post=[push])
@task(default=True)
def all(ctx, dry=False, push=False, dry_targets=False, filter=None, **kwargs):
    filter = ast.literal_eval(str(filter)) if filter else {}
    for t, options in ctx.target.items():
        if not t.startswith(filter.get('target', '')): continue
        matrix_build(ctx, t, matrix=options['matrix'], require=options['require'],
                     dry=dry, push=push, dry_targets=dry_targets, filter=filter, **kwargs)

@task
def build(ctx, target, require=[], dist='debian', dist_rel='stretch', salt=None, formula_rev=None, push=False, dry=False, dry_targets=False, **kwargs):

    kwargs['dist'] = dist
    kwargs['dist_rel'] = dist_rel
    kwargs['dry'] = True if dry_targets or dry else False
    kwargs['formula_rev'] = formula_rev
    kwargs['push'] = push
    kwargs['require'] = require
    kwargs['salt'] = salt
    kwargs['target'] = target
    # command formating + update
    fmt = {'tag': ''}
    fmt.update(ctx.dockermake)
    fmt.update(kwargs)
    fmt.update({'requires': '{}-{}'.format(fmt['dist'], fmt['dist_rel'])})

    _dockermake_args_helper(fmt, **fmt)

    if dry_targets:
        kw = ''
        for k,v in kwargs.items():
            if not k.startswith(('dist', 'dist_rel', 'formula_rev', 'salt', 'build_arg')): continue
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

def matrix_build(ctx, target, matrix=[], require=[], filter={}, **kwargs):
    "salt-formulas docker images build matrix fn"

    if 'dist' in matrix:
        m = matrix[:]
        m.remove('dist')
        for d, dr in ctx.matrix.dist.items():
            for r in dr:
                if not d.startswith(filter.get('dist', '')): continue
                if not r.startswith(filter.get('dist-rel', '')): continue
                matrix_build(ctx, target, matrix=m, require=require, dist=d, dist_rel=r, filter=filter, **kwargs)
        return 0
    if 'salt' in matrix:
        m = matrix[:]
        m.remove('salt')
        for s in ctx.matrix.salt:
            if not s.startswith(filter.get('salt', '')): continue
            matrix_build(ctx, target, matrix=m, require=require, salt=s, filter=filter, **kwargs)
        return 0
    if 'salt-formulas' in matrix:
        m = matrix[:]
        m.remove('salt-formulas')
        for f in ctx.matrix['salt-formulas']:
            if not f.startswith(filter.get('formula-rev', '')): continue
            matrix_build(ctx, target, matrix=m, require=require, formula_rev=f, filter=filter, **kwargs)
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
    else:
        fmt['dry'] = ''
    ## pusht to registry
    if push:
        fmt['push'] = '--push-to-registry'
    else:
        fmt['push'] = ''
    return fmt

