#!/usr/bin/python

"""
generate rpm spec from source rpm

Usage:
  pyrpmspec srpm <package_full_url> [--rpmbuild_root RBROOT]

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
    (package_url, package_name)=package_full_url.rsplit('/',1)

    need_prefix=False

    if package_url.rsplit('/',1)[1] == package_name[0]:
        package_url=package_url.rsplit('/',1)[0]
        need_prefix=True

    pattern = re.compile('(.*?)-(\d.*).src.rpm')
    match_result=pattern.match(package_name)
    package_name=match_result.group(1)
    package_ver=match_result.group(2)
    package_ver_var=package_name.replace('-','').replace('_','').replace('+','').upper()+'VER'

    spec_script.append('')
    spec_script.append('export %s' % package_ver_var+'='+package_ver)
    spec_script.append('export URL=%s' % package_url)
    if need_prefix:
        spec_script.append('wget -O $SRPMDIR/%s-%s.src.rpm $URL/%s-%s.src.rpm' % (package_name, '$'+package_ver_var, package_name[0]+'/'+package_name, '$'+package_ver_var))
    else:
        spec_script.append('wget -O $SRPMDIR/%s-%s.src.rpm $URL/%s-%s.src.rpm' % (package_name, '$'+package_ver_var, package_name, '$'+package_ver_var))
    spec_script.append('rpm -U $SRPMDIR/%s-%s.src.rpm' % (package_name, '$'+package_ver_var))
    if package_name.startswith('golang'):
        spec_script.append("sed -i -e 's/%global with_devel.*/%global with_devel 1/g' $RPMBUILDROOT/SPECS/"+package_name+".spec")
    if package_name.startswith('php'):
        spec_script.append('sed -i -e "/^Release/s#%{?dist}#%{?dist}%(%{_bindir}/php -r \'echo \\".\\".PHP_MAJOR_VERSION.\\".\\".PHP_MINOR_VERSION;\')#g" $RPMBUILDROOT/SPECS/'+package_name+'.spec')
    spec_script.append('rpmbuild -bb $RPMBUILDROOT/SPECS/%s.spec' % package_name)
    if package_name.startswith('php'):
        php_ver = '$(php -r \'echo ".".PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;\')'
        spec_script.append('rm -f $RPMDIR/%s-*el7%s*' % (package_name.replace('mingw','mingw*'), php_ver))
        spec_script.append('mv -f $RPMBUILDROOT/RPMS/noarch/%s-* $RPMDIR' % package_name.replace('mingw','mingw*'))
        spec_script.append('rpm -U $RPMDIR/%s-*el7%s*' % (package_name.replace('mingw','mingw*'), php_ver))
    else:
        spec_script.append('rm -f $RPMDIR/%s-*' % package_name.replace('mingw','mingw*'))
        if not package_name.startswith('golang') and not package_name.startswith('perl') and not package_name.startswith('rubygem'):
            spec_script.append('mv -f $RPMBUILDROOT/RPMS/x86_64/%s-* $RPMDIR' % package_name.replace('mingw','mingw*'))
        spec_script.append('mv -f $RPMBUILDROOT/RPMS/noarch/%s-* $RPMDIR' % package_name.replace('mingw','mingw*'))
        spec_script.append('rpm -U $RPMDIR/%s-*' % package_name.replace('mingw','mingw*'))

    print('\n'.join(spec_script))
    return None
