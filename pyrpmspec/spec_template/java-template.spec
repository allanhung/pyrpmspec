%global debug_package      %{nil}
%global __os_install_post  %{nil}
%global provider           {{ provider }}
%global provider_tld       {{ provider_tld }}
%global project            {{ project }}
%global repo               {{ repo }}
%global import_path        %{provider}.%{provider_tld}/%{project}/%{repo}
%global commit             GITCOMMIT
%global shortcommit        %(c=%{commit}; echo ${c:0:7})
%global gopath             %{_datadir}/gocode


Name:           %{repo}
Version:        {{ package_ver }}
Release:        1.git%{shortcommit}%{?dist}
Summary:      	detail in git
License:        BSD
URL:            https://%{import_path}
Source0:        %{name}-%{version}.tar.gz
ExclusiveArch:  x86_64


%description
%{summary}

%prep
%setup -q

%build
echo "Nothing to build..."

%install
rm -rf %{buildroot}/opt
mkdir -p %{buildroot}/opt
# copy all file to buildroot
#%{_sysconfdir}        /etc
#%{_prefix}            /usr
#%{_exec_prefix}       %{_prefix}
#%{_bindir}            %{_exec_prefix}/bin
#%{_libdir}            %{_exec_prefix}/%{_lib}
#%{_libexecdir}        %{_exec_prefix}/libexec
#%{_sbindir}           %{_exec_prefix}/sbin
#%{_sharedstatedir}    /var/lib
#%{_datarootdir}       %{_prefix}/share
#%{_datadir}           %{_datarootdir}
#%{_includedir}        %{_prefix}/include
#%{_infodir}           /usr/share/info
#%{_mandir}            /usr/share/man
#%{_localstatedir}     /var
#%{_unitdir}           /usr/lib/systemd/system
mv opt/%{name} %{buildroot}/opt/

%check
# empty for now

{{ systemd }}
%files
%defattr(-,root,root,-)
# pack all file in buildroot
/opt/%{name}

%changelog
* {{ today }} root - {{ package_ver }}
 - first version
