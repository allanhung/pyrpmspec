%global debug_package   %{nil}
%global provider        {{ provider }}
%global provider_tld    {{ provider_tld }}
%global project         {{ project }}
%global repo            {{ repo }}
%global import_path     %{provider}.%{provider_tld}/%{project}/%{repo}
%global commit          GITCOMMIT
%global shortcommit     %(c=%{commit}; echo ${c:0:7})


Name:           %{repo}
Version:        {{ package_ver }}
Release:        1.git%{shortcommit}%{?dist}
Summary:      	detail in git
License:        BSD
URL:            https://%{import_path}
Source0:        %{repo}-%{version}.tar.gz


%description
%{summary}


%prep
%setup -q -n %{repo}-%{version}


%build


%install
make install DESTDIR=%{buildroot}


%check
# empty for now


%files 


%changelog
* {{ today }} root - {{ package_ver }}
 - first version
