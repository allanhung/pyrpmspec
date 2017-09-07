#!/usr/bin/python

"""
generate rpm spec for golang

Usage:
  pyrpmspec ruby <git_hub_url> <version> [--rpmbuild_root RBROOT]

Options:
  -h --help                 Show this screen.
  --rpmbuild_root RBROOT    rpmbuild root directory   [default: /root/rpmbuild]
"""

from docopt import docopt
import os
import sys
import re
import common
import datetime

def gen_spec(args):
    go_dev_only = Ture if 'dev' in args.keys() else False
    spec_template = 'ruby-template.spec'

    spec_script = []
    package_dict = {}
    package_url=args['<git_hub_url>']
    package_dict['package_ver']=args['<version>']
    rpmbuild_root = args['--rpmbuild_root']

    pattern=re.compile('https://(.*?)/(.*?)/(.*)')
    match=re.match(pattern, package_url)
    download_mathod = 'wget' if '/' in match.groups(3) else 'git'

    (package_dict['provider'], package_dict['provider_tld']) = match.group(1).split('.')
    package_dict['project'] = match.group(2)
    package_dict['repo'] = match.group(3).split('/')[0].replace('.git','')
    package_dict['today'] = datetime.datetime.now().strftime("%a %b %d %Y")

    package_ver_var=package_dict['repo'].replace('-','').replace('_','').replace('.','').upper()+'VER'
    repo_name = package_dict['repo']
    spec_filename = repo_name+'.spec'
    repo_filename = package_dict['repo']+'-$'+package_ver_var+'.tar.gz'
    common.render_template('\n'.join(common.read_template(os.path.join(common.template_dir,spec_template))), package_dict, os.path.join(rpmbuild_root, 'SPECS', spec_filename))

    spec_script.append('')
    spec_script.append('export %s' % package_ver_var+'='+package_dict['package_ver'])
    if download_mathod == 'git':
        spec_script.append('cd /usr/local/src')
        spec_script.append('rm -rf /usr/local/src/'+package_dict['repo']+'-$'+package_ver_var)
        spec_script.append('git clone --depth=10 '+package_url+'.git '+package_dict['repo']+'-$'+package_ver_var)
        spec_script.append('tar -zcf $SRCDIR/'+repo_filename+' '+package_dict['repo']+'-$'+package_ver_var)
        spec_script.append('cd /usr/local/src/'+package_dict['repo']+'-$'+package_ver_var)
        spec_script.append('export GITCOMMIT=`git rev-parse HEAD`')
        spec_script.append('cd ..')
        spec_script.append('sed -i -e "/^%global/s#%global commit.*#%global commit          $GITCOMMIT#g" $RPMBUILDROOT/SPECS/'+spec_filename)
    else:
        spec_script.append('wget -O $SRCDIR/'+repo_filename+' '+package_url)
        spec_script.append('export GITCOMMIT='+sys.argv[3])
    spec_script.append('')
    spec_script.append('/bin/cp -f $RPMBUILDROOT/SPECS/'+spec_filename+' $SPECSDIR/')
    spec_script.append('/bin/cp -f $SRCDIR/'+repo_filename+' $RPMBUILDROOT/SOURCES/')
    spec_script.append('/bin/cp -f $SPECSDIR/'+spec_filename+' $RPMBUILDROOT/SPECS/')
    spec_script.append('rpmbuild -bb $RPMBUILDROOT/SPECS/'+spec_filename)
    spec_script.append('rm -f $RPMDIR/'+repo_name+'-*')
    spec_script.append('mv -f $RPMBUILDROOT/RPMS/x86_64/'+repo_name+'-* $RPMDIR')
    print('\n'.join(spec_script))
    return None
