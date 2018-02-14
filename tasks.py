#!/bin/env python
# vim: sts=2 ts=2


from invoke import Collection, task

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


@task
def default(ctx):
    all(ctx)


@task
def all(ctx, dry=False, **kwargs):
    for t, options in ctx.target.items():
        matrix_build(ctx, t, matrix=options['matrix'], require=options['require'], dry=dry, **kwargs)


@task
def target(ctx, t=None):
    for tt, options in ctx.target.items():
        if tt is None:
            matrix_build(ctx, t, matrix=options['matrix'], require=options['require'])
        else:
            if tt == t :
                matrix_build(ctx, t, matrix=options['matrix'], require=options['require'])


@task
def clean(ctx):
    ctx.run("rm -rf {}".format(destination))


@task
def build(ctx, target, require=[], dist='debian', dist_rel='stretch', salt=None, formula_rev=None, dry=False, **kwargs):
    fmt = {'target'      : target,
           'dist'        : dist,
           'dist_rel'    : dist_rel,
           'formula_rev' : formula_rev,
           'salt'        : salt,
           'salt_src'    : '',
           'requires'    : '',
           'dry'         : '',
           'tag'         : '',
          }
    fmt.update(ctx['docker-make'])

    # Additional formating
    if salt != 'stable':
        # TODO, skip for all packaged versions available
        fmt['salt_source'] = 'git'
    if len(require) > 0:
        fmt['requires'] = '--requires ' + ' --requires '.join(require)
    if salt:
        fmt['tag'] += '-salt-{}'.format(salt)
    if formula_rev:
        fmt['tag'] += '-formula-{}'.format(formula_rev)
    if dry:
        fmt['dry'] += 'echo '


    # execute
    ctx.run("""
            {dry}docker-make -f DockerMake.{dist}.yml -u {repository}: \
            {target} -t {dist}-{dist_rel}{tag} \
            --requires {dist}-{dist_rel} \
            {requires} \
            --build-arg salt_version='"{salt_src} {salt}"' \
            --build-arg salt_formula_revision="{formula_rev}" \
            """.format(**fmt))

