%global debug_package   %{nil}
%global provider        {{ provider }}
%global provider_tld    {{ provider_tld }}
%global project         {{ project }}
%global repo            {{ repo }}
%global import_path     {{ import_path }}
%global commit          GITCOMMIT
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           {{ repo_name }}
Version:        {{ package_ver }}
Release:        1.git%{shortcommit}%{?dist}
Summary:      	detail in git
License:        BSD
URL:            https://%{import_path}
Source0:        {{ source_filename }}.tar.gz
Source1:        %{repo}.nginx
BuildRequires:	nvm
BuildArch:      noarch

%description
%{summary}

%prep
%setup -q -n {{ source_filename }}


%build
echo '{ "allow_root": true }' > .bowerrc
source /opt/nvm/nvm.sh                                                                                                                                                                                                                                                         
nvm use 5.1.0
npm install
npm run build

%install
install -d -m 0755 %{buildroot}/opt/%{project}/%{repo}
cp -a build/webpack/* %{buildroot}/opt/%{project}/%{repo}/
install -d -m 755 %{buildroot}%{_sysconfdir}/nginx/conf.d
install -p -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/nginx/conf.d/%{repo}.conf.example

%check
# empty for now

%files
%{_sysconfdir}/nginx/conf.d/%{repo}.conf.example
/opt/%{project}/%{repo}

%changelog
* {{ today }} root - {{ package_ver }}
 - first version
