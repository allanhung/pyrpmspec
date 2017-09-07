#!/usr/bin/python

"""
generate rpm spec for perl

Usage:
  pyrpmspec perl <package_full_url> [--rpmbuild_root RBROOT]

Options:
  -h --help                 Show this screen.
  --rpmbuild_root RBROOT    rpmbuild root directory   [default: /root/rpmbuild]
"""

from docopt import docopt
import sys
import re

def gen_spec(args):
    spec_script = []
    package_full_url=args['<package_full_url>']
    rpmbuild_root = args['--rpmbuild_root']

    re_result = re.match('(.*)/(.*?)-(\d.*).tar.gz$', package_full_url)
    (package_url, package_name, package_ver) = (re_result.group(1), re_result.group(2), re_result.group(3))
    package_ver_var=package_name.replace('-','').replace('_','').upper()+'VER'

    spec_script.append('')
    spec_script.append('export %s' % package_ver_var+'='+package_ver)
    spec_script.append('wget -O $SRCDIR/%s-%s.tar.gz %s/%s-%s.tar.gz' % (package_name, '$'+package_ver_var, package_url, package_name, '$'+package_ver_var))
    spec_script.append('cpanspec $SRCDIR/%s-${%s%%-*}.tar.gz --packager root' % (package_name, package_ver_var))
    spec_script.append('/bin/cp -f $RPMBUILDROOT/SPECS/perl-%s.spec $SPECDIR' % (package_name))
    spec_script.append('/bin/cp -f $SRCDIR/%s-${%s%%-*}.tar.gz $RPMBUILDROOT/SOURCES' % (package_name, package_ver_var))
    spec_script.append('/bin/cp -f $SPECDIR/perl-%s.spec $RPMBUILDROOT/SPECS' % (package_name))
    spec_script.append('rpmbuild -bb $RPMBUILDROOT/SPECS/perl-%s.spec' % package_name)
    spec_script.append('mv -f $RPMBUILDROOT/RPMS/x86_64/perl-%s-* $RPMDIR' % package_name)
    spec_script.append('rpm -U $RPMDIR/perl-%s-*' % package_name)
    print('\n'.join(spec_script))
    return None
