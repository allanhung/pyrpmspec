#!/usr/bin/python

"""
generate rpm spec for golang

Usage:
  pyrpmspec nodejs <git_hub_url> <version> [--rpmbuild_root RBROOT] [--bin] [--dev] [--systemd]

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
    spec_template = 'nodejs-template.spec'

    spec_script = []
    package_dict = {}
    package_url=args['<git_hub_url>']
    package_dict['package_ver']=args['<version>']
    rpmbuild_root = args['--rpmbuild_root']

    import_path='%{provider}.%{provider_tld}/%{project}/%{repo}'
    pattern=re.compile('https://(.*?)/(.*?)/(.*)')
    match=re.match(pattern, package_url)
    download_mathod = 'wget' if '/' in match.groups(3) else 'git'

    (package_dict['provider'], package_dict['provider_tld']) = match.group(1).split('.')
    provider=package_dict['provider']
    package_dict['project'] = match.group(2)
    package_dict['repo'] = match.group(3).split('/')[0].replace('.git','')
    package_dict['repo_name'] = package_dict['project']+'-'+package_dict['repo']
    package_dict['import_path'] = import_path
    package_dict['today'] = datetime.datetime.now().strftime("%a %b %d %Y")

    package_ver_var=package_dict['repo'].replace('-','').replace('_','').replace('.','').upper()+'VER'    
    repo_name = package_dict['repo_name']
    spec_filename = repo_name+'.spec'
    repo_filename_prefix = package_dict['project']+'-'+package_dict['repo']+'-$'+package_ver_var
    repo_filename = repo_filename_prefix+'.tar.gz'
    package_dict['source_filename'] = repo_filename_prefix.replace('$'+package_ver_var,'%{version}')
    common.render_template('\n'.join(common.read_template(os.path.join(common.template_dir,spec_template))), package_dict, os.path.join(rpmbuild_root, 'SPECS', spec_filename))

    nginx_conf = []
    nginx_conf.append('server {')
    nginx_conf.append('    listen       80;')
    nginx_conf.append('    server_name  _;')
    nginx_conf.append('    index        index.html;')
    nginx_conf.append('    root         /opt/'+package_dict['project']+'/'+package_dict['repo']+';')
    nginx_conf.append('}')
    common.render_template('{{ context }}', {'context': '\n'.join(nginx_conf)}, os.path.join(rpmbuild_root, 'SOURCES', package_dict['repo_name']+'.nginx'))

    spec_script.append('')
    spec_script.append('export %s' % package_ver_var+'='+package_dict['package_ver'])
    if download_mathod == 'git':
        spec_script.append('cd /usr/local/src')
        spec_script.append('rm -rf /usr/local/src/'+repo_filename_prefix)
        spec_script.append('git clone --depth=10 '+package_url+'.git '+repo_filename_prefix)
        spec_script.append('tar -zcf $SRCDIR/'+repo_filename+' '+repo_filename_prefix)
        spec_script.append('cd /usr/local/src/'+repo_filename_prefix)
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
    spec_script.append('mv -f $RPMBUILDROOT/RPMS/noarch/'+repo_name+'-* $RPMDIR')
    print('\n'.join(spec_script))
    return None
