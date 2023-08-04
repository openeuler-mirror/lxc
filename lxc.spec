%global _release 2

Name:           lxc
Version:        5.0.2
Release:        %{_release}
Summary:        Linux Containers userspace tools
License:        LGPLv2+ and GPLv2 and GPLv3
URL:            https://github.com/lxc/lxc
Source0:        https://linuxcontainers.org/downloads/lxc/lxc-5.0.2.tar.gz

Patch0001:	0001-iSulad-add-json-files-and-adapt-to-meson.patch
Patch0002:	0002-iSulad-adapt-security-conf-attach-cgroup-and-start.patch
Patch0003:	0003-iSulad-adapt-conf-network-storage-and-termianl.patch
Patch0004:	0004-iSulad-adapt-confile-lxccontainer-and-start.patch
Patch0005:	0005-fix-compile-error.patch

BuildRequires:  systemd-units git libtool graphviz docbook2X doxygen chrpath
BuildRequires:  pkgconfig(libseccomp)
BuildRequires:  libcap libcap-devel libselinux-devel yajl yajl-devel
BuildRequires:  pkgconfig(bash-completion) meson
%ifarch riscv64
BuildRequires:  libatomic_ops
%endif

Requires:       lxc-libs = 5.0.2-%{release}

%package           libs
Summary:           Runtime library files for %{name}
Requires:          rsync libcap libseccomp libselinux
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd
Requires(post):    /sbin/ldconfig
Requires(postun):  /sbin/ldconfig

%description    libs
Linux Resource Containers provide process and resource isolation without the
overhead of full virtualization.

The %{name}-libs package contains libraries for running %{name} applications.


%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/lxc-4.0.3}

%description
Containers are insulated areas inside a system, which have their own namespace
for filesystem, network, PID, IPC, CPU and memory allocation and which can be
created using the Control Group and Namespace features included in the Linux
kernel.

This package provides the lxc-* tools and libraries for running lxc
applications, which can be used to start a single daemon in a container, or to
boot an entire "containerized" system, and to manage and debug your containers.

%package        devel
Summary:        Development files for lxc
Requires:       lxc = 5.0.2-%{release}
Requires:       pkgconfig

%description    devel
The lxc-devel package contains header files ,library and templates needed for
development of the Linux containers.


%package        help
Summary:        Documentation and templates for lxc
BuildArch:      noarch

%description    help
This package contains documentation for lxc for creating containers.

%prep
%autosetup -n lxc-5.0.2 -Sgit -p1

%build
%ifarch riscv64
export LDFLAGS="%{build_ldflags} -latomic -pthread"
%endif
meson setup -Disulad=true -Dtests=true -Dprefix=/usr build
meson compile -C build

%install
%{make_install}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}
mkdir -p %{buildroot}%{_datadir}/%{name}/__pycache__
touch %{buildroot}%{_datadir}/%{name}/__pycache__/%{name}

for file in $(find %{buildroot}/usr/bin/lxc-* -type f -exec file {} ';' | grep "\<ELF\>" | grep -vE "*\.static" | awk -F ':' '{print $1}')
do
    chrpath -d ${file}
done

for file in $(find %{buildroot}/usr/sbin/* -type f -exec file {} ';' | grep "\<ELF\>" | grep -vE "*\.static" | awk -F ':' '{print $1}')
do
    chrpath -d ${file}
done

for file in $(find %{buildroot}/usr/libexec/lxc/lxc-* -type f -exec file {} ';' | grep "\<ELF\>" | grep -vE "*\.static" | awk -F ':' '{print $1}')
do
    chrpath -d ${file}
done

%ifarch sw_64
chrpath -d %{buildroot}/usr/lib/liblxc.so
chmod +x %{buildroot}/usr/lib/liblxc.so
%else
chrpath -d %{buildroot}/usr/lib64/liblxc.so
chmod +x %{buildroot}/usr/lib64/liblxc.so
%endif
# docs
%ifarch sw_64
%else
cp -a AUTHORS %{buildroot}%{_pkgdocdir}
%endif

# cache dir
mkdir -p %{buildroot}%{_localstatedir}/cache/%{name}

if [ ! -d %{buildroot}%{_sysconfdir}/sysconfig ]
then
    mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
    touch %{buildroot}%{_sysconfdir}/sysconfig/%{name}
fi

# remove libtool .la file
rm -rf %{buildroot}%{_libdir}/liblxc.la
rm -rf %{buildroot}%{_sbindir}/init.%{name}.static
rm -rf %{buildroot}%{_sysconfdir}/default/%{name}
%check
meson test -C build

%post

%preun

%postun

%files
%defattr(-,root,root)
%{_bindir}/%{name}-*
%{_datadir}/%{name}/%{name}.functions
%dir %{_datadir}/bash-completion
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/*

%files libs
%defattr(-,root,root)
%{_libdir}/liblxc.so
%{_libdir}/liblxc.so.*
%{_libdir}/%{name}
%{_libexecdir}/%{name}
%{_sbindir}/init.%{name}
%{_sharedstatedir}/%{name}
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/lxc/*
%config(noreplace) %{_sysconfdir}/sysconfig/*

%dir %{_pkgdocdir}
%license COPYING
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}@.service
%{_unitdir}/%{name}-net.service
%{_unitdir}/%{name}-monitord.service
%dir %{_localstatedir}/cache/%{name}

%files devel
%defattr(-,root,root)
%{_libdir}/liblxc.a
%{_includedir}/%{name}/*
%{_libdir}/pkgconfig/%{name}.pc
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/lxc-patch.py*
%{_datadir}/%{name}/selinux
%dir %{_datadir}/%{name}/templates
%{_datadir}/%{name}/templates/lxc-*
%dir %{_datadir}/%{name}/config
%{_datadir}/%{name}/config/*
%dir %{_datadir}/%{name}/__pycache__
%{_datadir}/%{name}/__pycache__/*


%files help
%dir %{_pkgdocdir}
%{_pkgdocdir}/*
%ifarch sw_64
%else
%{_mandir}/man1/%{name}*
%{_mandir}/*/man1/%{name}*
%{_mandir}/man5/%{name}*
%{_mandir}/man7/%{name}*
%{_mandir}/*/man5/%{name}*
%{_mandir}/*/man7/%{name}*
%endif

%changelog
* Tue Aug 01 2023 zhangxiaoyu<zhangxiaoyu58@huawei.com> - 5.0.2-2
- Type:enhancement
- ID:NA
- SUG:NA
- DESC: add isulad code and fix compile error

* Thu Jul 13 2023 haozi007<liuhao27@huawei.com> - 5.0.2-1
- Type:enhancement
- ID:NA
- SUG:NA
- DESC: update to 5.0.2
