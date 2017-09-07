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


%package devel
Summary:  Development Libraries for %{name}
Group:    Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: pkgconfig


%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -q -n %{repo}-%{version}


%build
#libtoolize
#aclocal
#autoheader
#automake --add-missing
#autoconf
%configure
make %{?_smp_mflags}


%install
make install DESTDIR=%{buildroot}


%check
# empty for now

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files 
%{_libdir}/%{name}.so.*


%files devel
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/%{name}*
%{_libdir}/%{name}.so


%changelog
* {{ today }} root - {{ package_ver }}
 - first version
