%global debug_package   %{nil}
%global provider        {{ provider }}
%global provider_tld    {{ provider_tld }}
%global project         {{ project }}
%global repo            {{ repo }}
%global import_path     %{provider}.%{provider_tld}/%{project}/%{repo}
%global commit          GITCOMMIT
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global pypi_name       %{repo}


Name:           python-%{repo}
Version:        {{ package_ver }}
Release:        1.git%{shortcommit}%{?dist}
Summary:      	detail in git
License:        BSD
URL:            https://%{import_path}
Source0:        %{repo}-%{version}.tar.gz
BuildRequires:  python2-devel

%description
%{summary}

%prep
%setup -q -n %{repo}-%{version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install --skip-build --root %{buildroot}


%check
# empty for now

%files 
%doc 
%{python2_sitelib}/%{pypi_name}-%{version}-py?.?.egg-info
%{python2_sitelib}/%{pypi_name}

%changelog
* {{ today }} root - {{ package_ver }}
 - first version
