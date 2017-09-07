#!/usr/bin/python

"""
generate rpm spec for golang

Usage:
  pyrpmspec go <git_hub_url> <version> [--rpmbuild_root RBROOT] [--bin] [--dev] [--docker] [--systemd] [--tag TAG]

Options:
  -h --help                 Show this screen.
  --rpmbuild_root RBROOT    rpmbuild root directory   [default: /root/rpmbuild]
  --tag           TAG       git tag                   [default: ]
"""

from docopt import docopt
import os
import sys
import re
import common
import datetime

def gen_bin_context(repo, args):    
    bin_context = {}
    if args['--bin']:
        # bin build
        bin_build_script = []
        bin_build_script.append('export GOPATH=$(pwd):$(pwd)/vendor:%{gopath}')
#        bin_build_script.append('mkdir -p /tmp/%{repo}/src/%{provider}.%{provider_tld}/%{project}/%{repo}')
#        bin_build_script.append('cp -af * /tmp/%{repo}/src/%{provider}.%{provider_tld}/%{project}/%{repo}/')
#        bin_build_script.append('mv /tmp/%{repo}/src .')
#        bin_build_script.append('rm -rf /tmp/%{repo}/src')
        bin_build_script.append('mkdir -p src/%{provider}.%{provider_tld}/%{project}')
        bin_build_script.append('ln -s ../../../ src/%{provider}.%{provider_tld}/%{project}/%{repo}')
        bin_build_script.append('if [ -d vendor ] && ! [ -d vendor/src ]; then')
        bin_build_script.append('  mkdir -p vendor/src')
        bin_build_script.append('  for dir in $(find vendor \! -name "src" -a \! -name "vendor" -maxdepth 1) ; do')
        bin_build_script.append('    mydir=`basename $dir`')
        bin_build_script.append('    ln -s ../$mydir vendor/src/$mydir')
        bin_build_script.append('  done')
        bin_build_script.append('fi')
        bin_build_script.append('cd src/%{provider}.%{provider_tld}/%{project}/%{repo}GOBINDIR')
        bin_build_script.append('go build -v -x -o '+repo+'.bin')
        bin_build_script.append('')
        bin_context['bin_build']='\n'.join(bin_build_script)
        # bin install
        bin_install_script = []
        bin_install_script.append('install -D -p -m 0755 src/%{provider}.%{provider_tld}/%{project}/%{repo}GOBINDIR/%{repo}.bin %{buildroot}%{_bindir}/%{repo}')
        bin_build_script.append('')
        bin_context['bin_install']='\n'.join(bin_install_script)
        # bin file
        bin_file_script = []
        bin_file_script.append('%{_bindir}/'+repo)
        bin_file_script.append('')
        bin_file_script.append('')
        bin_context['bin_file']='\n'.join(bin_file_script)
    else:
        bin_context['bin_build']=''
        bin_context['bin_install']=''
        bin_context['bin_file']=''
    return bin_context

def gen_devel_context(args):
    devel_context = {}
    if args['--dev']:
        # devel package
        devel_package_script = []
        devel_package_script.append('')
        devel_package_script.append('')
        devel_package_script.append('%package devel')
        devel_package_script.append('Summary:       %{summary}')
        devel_package_script.append('BuildArch:     noarch')
        devel_package_script.append('')
        devel_package_script.append('')
        devel_context['devel_package']='\n'.join(devel_package_script)
        # devel desc
        devel_desc_script = []
        devel_desc_script.append('%description devel')
        devel_desc_script.append('%{summary}')
        devel_desc_script.append('')
        devel_desc_script.append('')
        devel_context['devel_desc']='\n'.join(devel_desc_script)
        # devel install
        devel_install_script = []
        devel_install_script.append('# devel')
        devel_install_script.append('install -d -p %{buildroot}/%{gopath}/src/%{import_path}/')
        devel_install_script.append('# find all *.go but no *_test.go files and generate devel.file-list')
        devel_install_script.append('for file in $(find . -iname "*.go" \! -iname "*_test.go" -o -iname "*.s") ; do')
        devel_install_script.append('    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)')
        devel_install_script.append('    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file')
        devel_install_script.append('    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list')
        devel_install_script.append('done')
        devel_install_script.append('')
        devel_install_script.append('')
        devel_context['devel_install']='\n'.join(devel_install_script)
        # devel file
        devel_file_script = []
        devel_file_script.append('')
        devel_file_script.append('%files devel -f devel.file-list')
        devel_file_script.append('%doc README.md')
        devel_file_script.append('%dir %{gopath}/src/%{import_path}')
        devel_file_script.append('')
        devel_file_script.append('')
        devel_context['devel_file']='\n'.join(devel_file_script)
    else:
        devel_context['devel_package']=''
        devel_context['devel_desc']=''
        devel_context['devel_install']=''
        devel_context['devel_file']=''
    return devel_context

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
    go_dev_only = Ture if 'dev' in args.keys() else False
    spec_template = 'go-template.spec'

    spec_script = []
    package_dict = {}
    package_url=args['<git_hub_url>']
    package_dict['_version']=args['<version>']
    package_dict['package_ver']=args['<version>'].replace('-','_')
    rpmbuild_root = args['--rpmbuild_root']
    git_tag = args['TAG']

    gopkg = ('gopkg.in' in package_url)
    if gopkg:
        pattern=re.compile('https://(.*?)/(.*)\.(.*)')
        match=re.match(pattern, package_url)
        if '/' in match.group(2):
            (pkg_project, pkg_repo) = match.group(2).split('/')
        else:
            pkg_project = 'go-'+match.group(2)
            pkg_repo = match.group(2)
        branch=match.group(3)
        branch_git_version=common.get_gopkg_version_dict(package_url)[branch]
        package_url='https://github.com/'+pkg_project+'/'+pkg_repo
        (provider, provider_tld) = match.group(1).split('.')
        import_path=match.group(1)+'/'+match.group(2)+'.'+match.group(3)
    else:
        import_path='%{provider}.%{provider_tld}/%{project}/%{repo}'

    pattern=re.compile('https://(.*?)/(.*?)/(.*)')
    match=re.match(pattern, package_url)
    download_mathod = 'wget' if '/' in match.groups(3) else 'git'

    (package_dict['provider'], package_dict['provider_tld']) = match.group(1).split('.')
    if not gopkg:
        provider=package_dict['provider']
    package_dict['project'] = match.group(2)
    package_dict['repo'] = match.group(3).split('/')[0].replace('.git','')
    package_dict['repo_name'] = 'golang-'+provider+'-'+package_dict['repo']+'-'+branch if gopkg else 'golang-'+provider+'-'+package_dict['project']+'-'+package_dict['repo']
    package_dict['import_path'] = import_path
    package_dict.update(gen_bin_context(package_dict['repo'], args))
    package_dict.update(gen_devel_context(args))
    package_dict.update(gen_systemd_context(args))
    package_dict['today'] = datetime.datetime.now().strftime("%a %b %d %Y")

    package_ver_var=package_dict['repo'].replace('-','').replace('_','').replace('.','').upper()+'VER'    
    repo_name = package_dict['repo_name']
    spec_filename = repo_name+'.spec'
    repo_filename_prefix = package_dict['project']+'-'+package_dict['repo']+'-'+branch+'-$'+package_ver_var if gopkg else package_dict['project']+'-'+package_dict['repo']+'-$'+package_ver_var
    repo_filename = repo_filename_prefix+'.tar.gz'
    package_dict['source_filename'] = repo_filename_prefix.replace('$'+package_ver_var,'%{_version}')
    common.render_template('\n'.join(common.read_template(os.path.join(common.template_dir,spec_template))), package_dict, os.path.join(rpmbuild_root, 'SPECS', spec_filename))

    source_dir = './sources' if args['--docker'] else '$SRCDIR'
    spec_dir = './specs' if args['--docker'] else '$SPECSDIR'
    spec_script.append('')
    spec_script.append('export %s' % package_ver_var+'='+package_dict['_version'])
    if download_mathod == 'git':
        spec_script.append('cd /usr/local/src')
        spec_script.append('rm -rf /usr/local/src/'+repo_filename_prefix)
        spec_script.append('git clone --depth=10 -b '+git_tag+'$'+package_ver_var+' '+package_url+'.git '+repo_filename_prefix)
        if gopkg:
            spec_script.append('cd /usr/local/src/'+repo_filename_prefix)
            spec_script.append('(git tag -l |grep '+branch_git_version+') && git checkout '+branch_git_version+' || git checkout -b '+branch_git_version)
            spec_script.append('cd ..')
        spec_script.append('tar -zcf $RPMBUILDROOT/SOURCES/'+repo_filename+' '+repo_filename_prefix)
        if args['--bin']:
            spec_script.append('export GOBINDIR=`find '+repo_filename_prefix+'/ -name "main.go"|awk -F"'+repo_filename_prefix+'" {\'$2\'}|awk -F"/main.go" {\'$1\'}`')
        spec_script.append('cd /usr/local/src/'+repo_filename_prefix)
        spec_script.append('export GITCOMMIT=`git rev-parse HEAD`')
        spec_script.append('cd ..')
        if args['--bin']:
            spec_script.append('sed -i -e "s#GOBINDIR#$GOBINDIR#g" $RPMBUILDROOT/SPECS/'+spec_filename)
        spec_script.append('sed -i -e "/^%global/s#%global commit.*#%global commit          $GITCOMMIT#g" $RPMBUILDROOT/SPECS/'+spec_filename)
    else:
        spec_script.append('wget -O $SRCDIR/'+repo_filename+' '+package_url)
        spec_script.append('export GITCOMMIT='+sys.argv[3])
    spec_script.append('')
    spec_script.append('/bin/cp -f $RPMBUILDROOT/SPECS/'+spec_filename+' '+spec_dir+'/')
    if args['--docker']:
        spec_script.append('echo "" >> readme.txt')
        spec_script.append('echo "rpmbuild -bb \\$RPMBUILDROOT/SPECS/'+spec_filename+'" >> readme.txt')
        spec_script.append('echo "rpm -U \\$(find \\$RPMBUILDROOT/RPMS -iname \\"'+repo_name+'-*.rpm\\" -a ! -iname \\"'+repo_name+'-*debug*.rpm\\"| tr \\"\\n\\" \\" \\")" >> readme.txt')
    else:
        spec_script.append('/bin/cp -f $SRCDIR/'+repo_filename+' $RPMBUILDROOT/SOURCES/')
        spec_script.append('/bin/cp -f $SPECSDIR/'+spec_filename+' $RPMBUILDROOT/SPECS/')
        spec_script.append('rpmbuild -bb $RPMBUILDROOT/SPECS/'+spec_filename)
        spec_script.append('rm -f $RPMDIR/'+repo_name+'-*')
        if args['--bin']:
            spec_script.append('mv -f $RPMBUILDROOT/RPMS/x86_64/'+repo_name+'-* $RPMDIR')
        if args['--dev']:
            spec_script.append('mv -f $RPMBUILDROOT/RPMS/noarch/'+repo_name+'-devel-* $RPMDIR')
        spec_script.append('rpm -U $RPMDIR/'+repo_name+'-devel-*')
        if not args['--bin']:
            spec_script.append('rm -f $RPMBUILDROOT/RPMS/x86_64/'+repo_name+'-*')
    print('\n'.join(spec_script))
    return None
