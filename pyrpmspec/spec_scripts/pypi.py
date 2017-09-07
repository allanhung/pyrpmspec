#!/usr/bin/python

"""
generate rpm spec for pypi

Usage:
  pyrpmspec pypi <python_module_name> <version> [--docker] [--rpmbuild_root RBROOT]

Options:
  -h --help                 Show this screen.
  --rpmbuild_root RBROOT    rpmbuild root directory   [default: /root/rpmbuild]
"""

from docopt import docopt
import sys

def gen_spec(args):
    spec_script = []
    package_name=args['<python_module_name>']
    package_ver=args['<version>']
    rpmbuild_root = args['--rpmbuild_root']

    package_ver_var=package_name.replace('-','').replace('_','').replace('.','').upper()+'VER'

    spec_script.append('')
    spec_script.append('export %s' % package_ver_var+'='+package_ver)
    spec_script.append('pyp2rpm -n %s --srpm' % package_name)
    source_dir = './sources' if args['--docker'] else '$SRCDIR'
    spec_dir = './specs' if args['--docker'] else '$SPECSDIR'
    if package_name.startswith('python-'):
        short_package_name = package_name[7:]
        spec_script.append('sed -i -e "/^%global pypi_name/s#'+package_name+'#'+short_package_name+'#g" $RPMBUILDROOT/SPECS/python-'+package_name+'.spec')
        spec_script.append('sed -i -e "/^%setup -q -n %{pypi_name}/s#pypi_name#name#g" $RPMBUILDROOT/SPECS/python-'+package_name+'.spec')
        spec_script.append('/bin/cp -f $RPMBUILDROOT/SOURCES/%s-%s.tar.gz %s/%s-%s.tar.gz' % (package_name, '$'+package_ver_var, source_dir, short_package_name, '$'+package_ver_var))
        spec_script.append('/bin/cp -f $RPMBUILDROOT/SPECS/python-%s.spec %s/%s.spec' % (package_name, spec_dir, package_name))
        if args['--docker']:
            spec_script.append('echo "" >> readme.txt')
            spec_script.append('echo "rpmbuild -bb \\$RPMBUILDROOT/SPECS/%s.spec" >> readme.txt' % package_name)
            spec_script.append('echo "rpm -U \\$(find \\$RPMBUILDROOT/RPMS -iname \\"%s-*.rpm\\" -a ! -iname \\"%s-*debug*.rpm\\"| tr \\"\\n\\" \\" \\")" >> readme.txt'  % (package_name, package_name))
        else:       
            spec_script.append('/bin/cp -f %s/%s-%s.tar.gz $RPMBUILDROOT/SOURCES/%s-%s.tar.gz' % (source_dir, short_package_name, '$'+package_ver_var, short_package_name, '$'+package_ver_var))
            spec_script.append('/bin/cp -f %s/%s.spec $RPMBUILDROOT/SPECS/' % (spec_dir, package_name))
            spec_script.append('rpmbuild -bb $RPMBUILDROOT/SPECS/%s.spec' % package_name)
            spec_script.append('rm -f $RPMDIR/%s-*' % package_name)
            spec_script.append('mv -f $RPMBUILDROOT/RPMS/noarch/%s-* $RPMDIR' % package_name)
    else:
        spec_script.append('/bin/cp -f $RPMBUILDROOT/SOURCES/%s-%s.tar.gz %s/' % (package_name, '$'+package_ver_var, source_dir))
        spec_script.append('/bin/cp -f $RPMBUILDROOT/SPECS/python-%s.spec %s/' % (package_name, spec_dir))
        if args['--docker']:
            spec_script.append('echo "" >> readme.txt')
            spec_script.append('echo "rpmbuild -bb \\$RPMBUILDROOT/SPECS/python-%s.spec" >> readme.txt' % package_name)
            spec_script.append('echo "rpm -U \\$(find \\$RPMBUILDROOT/RPMS -iname \\"python-%s-*.rpm\\" -a ! -iname \\"python-%s-*debug*.rpm\\"| tr \\"\\n\\" \\" \\")" >> readme.txt'  % (package_name, package_name))
        else:
            spec_script.append('/bin/cp -f %s/%s-%s.tar.gz $RPMBUILDROOT/SOURCES/%s-%s.tar.gz' % (source_dir, package_name, '$'+package_ver_var, package_name, '$'+package_ver_var))
            spec_script.append('/bin/cp -f %s/python-%s.spec $RPMBUILDROOT/SPECS/' % (spec_dir, package_name))
            spec_script.append('rpmbuild -bb $RPMBUILDROOT/SPECS/python-%s.spec' % package_name)
            spec_script.append('rm -f $RPMDIR/python-%s-*' % package_name)
            spec_script.append('mv -f $RPMBUILDROOT/RPMS/noarch/python-%s-* $RPMDIR' % package_name)
    print('\n'.join(spec_script))
    return None
