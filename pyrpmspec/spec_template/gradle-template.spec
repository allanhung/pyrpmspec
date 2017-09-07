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
BuildArch:      noarch

%description
%{summary}

%prep
%setup -q -n {{ source_filename }}


%build
find . -type d -name "build" | xargs rm -rf
./gradlew clean
./gradlew install
find . -name "*SNAPSHOT.jar" | xargs rm -f

%install
install -d -m 0755 %{buildroot}/opt/%{project}/libs
find . -name "*.jar" |grep build |xargs -i cp {} %{buildroot}/opt/%{project}/libs/

%check
# empty for now

%files
/opt/%{project}/libs

%changelog
* {{ today }} root - {{ package_ver }}
 - first version
