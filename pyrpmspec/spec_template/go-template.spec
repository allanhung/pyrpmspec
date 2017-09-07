%global debug_package   %{nil}
%global provider        {{ provider }}
%global provider_tld    {{ provider_tld }}
%global project         {{ project }}
%global repo            {{ repo }}
%global import_path     {{ import_path }}
%global _version        {{ _version }}
%global commit          GITCOMMIT
%global shortcommit     %(c=%{commit}; echo ${c:0:7})
%global gopath          %{_datadir}/gocode


Name:           {{ repo_name }}
Version:        {{ package_ver }}
Release:        1.git%{shortcommit}%{?dist}
Summary:      	detail in git
License:        BSD
URL:            https://%{import_path}
Source0:        {{ source_filename }}.tar.gz
BuildRequires:	golang


%description
%{summary}
{{ devel_package }}
{{ devel_desc }}
%prep
%setup -q -n {{ source_filename }}


%build
{{ bin_build }}

%install
{{ bin_install }}
{{ devel_install }}
%check
# empty for now

{{ systemd }}
%files
{{ bin_file }}
{{ devel_file }}
%changelog
* {{ today }} root - {{ package_ver }}
 - first version
