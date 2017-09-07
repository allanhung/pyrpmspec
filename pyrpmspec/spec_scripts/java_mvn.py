#!/usr/bin/python

"""
generate rpm spec for golang

Usage:
  pyrpmspec java_mvn <git_hub_url> <version> [--rpmbuild_root RBROOT] [--systemd]

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

def gen_systemd_context(args):
    systemd_context = {}
    if args['--systemd']:
        systemd_script = []
        systemd_script.append('%pre')
        systemd_script.append('')
        systemd_script.append('%post')
        systemd_script.append('%systemd_post %{repo}')
        systemd_script.append('')
        systemd_script.append('%preun')
        systemd_script.append('%systemd_preun %{repo}')
        systemd_script.append('')
        systemd_script.append('%postun')
        systemd_script.append('%systemd_postun_with_restart %{repo}')
        systemd_script.append('')
        systemd_script.append('')
        systemd_context['systemd']='\n'.join(systemd_script)
    else:
        systemd_context['systemd']=''
    return systemd_context

def gen_spec(args):
    spec_template = 'java-template.spec'

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
    package_dict.update(gen_systemd_context(args))
    package_dict['today'] = datetime.datetime.now().strftime("%a %b %d %Y")

    package_ver_var=package_dict['repo'].replace('-','').replace('_','').replace('.','').upper()+'VER'
    spec_filename = package_dict['repo']+'.spec'
    repo_filename_prefix = package_dict['repo']+'-$'+package_ver_var
    repo_filename = repo_filename_prefix+'.tar.gz'
    common.render_template('\n'.join(common.read_template(os.path.join(common.template_dir,spec_template))), package_dict, os.path.join(rpmbuild_root, 'SPECS', spec_filename))

    spec_script.append('')
    spec_script.append('export %s' % package_ver_var+'='+package_dict['package_ver'])
    if download_mathod == 'git':
        spec_script.append('cd /usr/local/src')
        spec_script.append('rm -rf /usr/local/src/'+repo_filename_prefix)
        spec_script.append('git clone --depth=10 '+package_url+' '+repo_filename_prefix)
        spec_script.append('tar -zcf $SRCDIR/'+repo_filename_prefix+'-src.tar.gz '+repo_filename_prefix)
    else:
        spec_script.append('wget -O $SRCDIR/'+repo_filename_prefix+'-src.tar.gz '+package_url)
        spec_script.append('cd /usr/local/src')
        spec_script.append('rm -rf /usr/local/src/'+repo_filename_prefix)
        spec_script.append('tar -zxf $SRCDIR/'+repo_filename_prefix+'-src.tar.gz')
    spec_script.append('cd /usr/local/src/'+repo_filename_prefix)
    spec_script.append('export GITCOMMIT=`git rev-parse HEAD`')
    spec_script.append('#mvn clean package -DskipTests')
    spec_script.append('#mvn clean install')
    spec_script.append('mvn clean package')
    spec_script.append('rm -rf /usr/local/src/'+repo_filename_prefix+'/'+repo_filename_prefix+'/opt/'+package_dict['repo'])
    spec_script.append('mkdir -p /usr/local/src/'+repo_filename_prefix+'/'+repo_filename_prefix+'/opt/'+package_dict['repo'])
    spec_script.append('tar -zxf /usr/local/src/'+repo_filename_prefix+'/target/'+repo_filename_prefix+'-SNAPSHOT.tar.gz -C /usr/local/src/'+repo_filename_prefix+'/'+repo_filename_prefix+'/opt/'+package_dict['repo'])
    spec_script.append('tar -zcf $SRCDIR/'+repo_filename_prefix+'-bin.tar.gz '+repo_filename_prefix)
    spec_script.append('cd ..')
    spec_script.append('sed -i -e "/^%global/s#%global commit.*#%global commit          $GITCOMMIT#g" $RPMBUILDROOT/SPECS/'+spec_filename)
    spec_script.append('')
    spec_script.append('/bin/cp -f $RPMBUILDROOT/SPECS/'+spec_filename+' $SPECSDIR/')
    spec_script.append('/bin/cp -f $SRCDIR/'+repo_filename_prefix+'-bin.tar.gz $RPMBUILDROOT/SOURCES/'+repo_filename)
    spec_script.append('/bin/cp -f $SPECSDIR/'+spec_filename+' $RPMBUILDROOT/SPECS/')
    spec_script.append('rpmbuild -bb $RPMBUILDROOT/SPECS/'+spec_filename)
    spec_script.append('rm -f $RPMDIR/'+package_dict['repo']+'-*')
    spec_script.append('mv -f $RPMBUILDROOT/RPMS/x86_64/'+package_dict['repo']+'-* $RPMDIR')
    print('\n'.join(spec_script))
    return None
