Summary:	A dynamic adaptive system tuning daemon
Name:		tuned
Version:	2.5.1
Release:	0.1
License:	GPL v2+
Source0:	https://fedorahosted.org/releases/t/u/tuned/%{name}-%{version}.tar.bz2
URL:		https://fedorahosted.org/tuned/
BuildRequires:	python
BuildRequires:	systemd
BuildArch:	noarch
Requires(post):	systemd, virt-what
Requires(preun):	systemd
Requires(postun):	systemd
Requires:	python-decorator
Requires:	dbus-python
Requires:	pygobject3-base
Requires:	python-pyudev
Requires:	util-linux
Requires:	python-perf
Requires:	virt-what
Requires:	python-configobj
Requires:	ethtool
Requires:	gawk
Requires:	kernel-tools
Requires:	hdparm

%description
The tuned package contains a daemon that tunes system settings
dynamically. It does so by monitoring the usage of several system
components periodically. Based on that information components will
then be put into lower or higher power saving modes to adapt to the
current usage. Currently only ethernet network and ATA harddisk
devices are implemented.

%package gtk
Summary:	GTK GUI for tuned
Requires:	%{name} = %{version}-%{release}
Requires:	powertop
Requires:	pygobject3-base
Requires:	polkit

%description gtk
GTK GUI that can control tuned and provide simple profile editor.

%package utils
Summary:	Various tuned utilities
Requires:	%{name} = %{version}-%{release}
Requires:	powertop

%description utils
This package contains utilities that can help you to fine tune and
debug your system and manage tuned profiles.

%package utils-systemtap
Summary:	Disk and net statistic monitoring systemtap scripts
Requires:	%{name} = %{version}-%{release}
Requires:	systemtap

%description utils-systemtap
This package contains several systemtap scripts to allow detailed
manual monitoring of the system. Instead of the typical IO/sec it
collects minimal, maximal and average time between operations to be
able to identify applications that behave power inefficient (many
small operations instead of fewer large ones).

%package profiles-sap
Summary:	Additional tuned profile(s) targeted to SAP NetWeaver loads
Requires:	%{name} = %{version}-%{release}

%description profiles-sap
Additional tuned profile(s) targeted to SAP NetWeaver loads.

%package profiles-oracle
Summary:	Additional tuned profile(s) targeted to Oracle loads
Requires:	%{name} = %{version}-%{release}

%description profiles-oracle
Additional tuned profile(s) targeted to Oracle loads.

%package profiles-sap-hana
Summary:	Additional tuned profile(s) targeted to SAP HANA loads
Requires:	%{name} = %{version}-%{release}

%description profiles-sap-hana
Additional tuned profile(s) targeted to SAP HANA loads.

%package profiles-atomic
Summary:	Additional tuned profile(s) targeted to Atomic
Requires:	%{name} = %{version}-%{release}

%description profiles-atomic
Additional tuned profile(s) targeted to Atomic host and guest.

%package profiles-realtime
Summary:	Additional tuned profile(s) targeted to realtime
Requires:	%{name} = %{version}-%{release}
Requires:	tuna

%description profiles-realtime
Additional tuned profile(s) targeted to realtime.

%package profiles-nfv
Summary:	Additional tuned profile(s) targeted to Network Function Virtualization (NFV)
Requires:	%{name} = %{version}-%{release}
Requires:	%{name}-profiles-realtime = %{version}-%{release}
Requires:	tuna

%description profiles-nfv
Additional tuned profile(s) targeted to Network Function
Virtualization (NFV).

%package profiles-compat
Summary:	Additional tuned profiles mainly for backward compatibility with tuned 1.0
Requires:	%{name} = %{version}-%{release}

%description profiles-compat
Additional tuned profiles mainly for backward compatibility with tuned
1.0. It can be also used to fine tune your system for specific
scenarios.

%prep
%setup -q


%build


%install
rm -rf $RPM_BUILD_ROOT
%{__make} install DESTDIR=$RPM_BUILD_ROOT DOCDIR=%{docdir}
%if 0%{?rhel}
sed -i 's/\(dynamic_tuning[ \t]*=[ \t]*\).*/\10/' $RPM_BUILD_ROOT%{_sysconfdir}/tuned/tuned-main.conf
%endif

# conditional support for grub2, grub2 is not available on all architectures
# and tuned is noarch package, thus the following hack is needed
install -d $RPM_BUILD_ROOT%{_datadir}/tuned/grub2
mv $RPM_BUILD_ROOT%{_sysconfdir}/grub.d/00_tuned $RPM_BUILD_ROOT%{_datadir}/tuned/grub2/00_tuned
rmdir $RPM_BUILD_ROOT%{_sysconfdir}/grub.d

%post
%systemd_post tuned.service

# convert active_profile from full path to name (if needed)
sed -i 's|.*/\([^/]\+\)/[^\.]\+\.conf|\1|' %{_sysconfdir}/tuned/active_profile

# convert GRUB_CMDLINE_LINUX to GRUB_CMDLINE_LINUX_DEFAULT
sed -i 's/GRUB_CMDLINE_LINUX="$GRUB_CMDLINE_LINUX \\$tuned_params"/GRUB_CMDLINE_LINUX_DEFAULT="$GRUB_CMDLINE_LINUX_DEFAULT \\$tuned_params"/' \
  %{_sysconfdir}/default/grub


%preun
%systemd_preun tuned.service


%postun
%systemd_postun_with_restart tuned.service

# conditional support for grub2, grub2 is not available on all architectures
# and tuned is noarch package, thus the following hack is needed
if [ "$1" == 0 ]; then
  rm -f %{_sysconfdir}/grub.d/00_tuned || :
# unpatch /etc/default/grub
  sed -i '/GRUB_CMDLINE_LINUX_DEFAULT="$GRUB_CMDLINE_LINUX_DEFAULT \\$tuned_params"/d' %{_sysconfdir}/default/grub
fi


%triggerun -- tuned < 2.0-0
# remove ktune from old tuned, now part of tuned
/usr%service ktune stop &>/dev/null || :
/usr/sbin/chkconfig --del ktune &>/dev/null || :


%posttrans
# conditional support for grub2, grub2 is not available on all architectures
# and tuned is noarch package, thus the following hack is needed
if [ -d %{_sysconfdir}/grub.d ]; then
  cp -a %{_datadir}/tuned/grub2/00_tuned %{_sysconfdir}/grub.d/00_tuned
fi


%files
%defattr(644,root,root,755)
%exclude %{docdir}/README.utils
%exclude %{docdir}/README.scomes
%doc %{docdir}
%{bash_compdir}/tuned-adm
%exclude %{py_sitescriptdir}/tuned/gtk
%{py_sitescriptdir}/tuned
%attr(755,root,root) %{_sbindir}/tuned
%attr(755,root,root) %{_sbindir}/tuned-adm
%exclude %{_sysconfdir}/tuned/realtime-variables.conf
%exclude %{_prefix}/lib/tuned/default
%exclude %{_prefix}/lib/tuned/desktop-powersave
%exclude %{_prefix}/lib/tuned/laptop-ac-powersave
%exclude %{_prefix}/lib/tuned/server-powersave
%exclude %{_prefix}/lib/tuned/laptop-battery-powersave
%exclude %{_prefix}/lib/tuned/enterprise-storage
%exclude %{_prefix}/lib/tuned/spindown-disk
%exclude %{_prefix}/lib/tuned/sap-netweaver
%exclude %{_prefix}/lib/tuned/sap-hana
%exclude %{_prefix}/lib/tuned/sap-hana-vmware
%exclude %{_prefix}/lib/tuned/oracle
%exclude %{_prefix}/lib/tuned/atomic-host
%exclude %{_prefix}/lib/tuned/atomic-guest
%exclude %{_prefix}/lib/tuned/realtime
%exclude %{_prefix}/lib/tuned/realtime-virtual-guest
%exclude %{_prefix}/lib/tuned/realtime-virtual-host
%{_prefix}/lib/tuned
%dir %{_sysconfdir}/tuned
%dir %{_libexecdir}/tuned
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/tuned/active_profile
%config(noreplace) %{_sysconfdir}/tuned/tuned-main.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/tuned/bootcmdline
/etc/dbus-1/system.d/com.redhat.tuned.conf
%{systemdtmpfilesdir}/tuned.conf
%{systemdunitdir}/tuned.service
%dir %{_localstatedir}/log/tuned
%dir /run/tuned
%{_mandir}/man5/tuned*
%{_mandir}/man7/tuned-profiles.7*
%{_mandir}/man8/tuned*
%dir %{_datadir}/tuned
%{_datadir}/tuned/grub2

%files gtk
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/tuned-gui
%{py_sitescriptdir}/tuned/gtk
%{_datadir}/tuned/ui
%{_datadir}/polkit-1/actions/org.tuned.gui.policy

%files utils
%defattr(644,root,root,755)
%doc COPYING
%attr(755,root,root) %{_bindir}/powertop2tuned
%{_libexecdir}/tuned/pmqos-static*

%files utils-systemtap
%defattr(644,root,root,755)
%doc doc/README.utils
%doc doc/README.scomes
%doc COPYING
%attr(755,root,root) %{_sbindir}/varnetload
%attr(755,root,root) %{_sbindir}/netdevstat
%attr(755,root,root) %{_sbindir}/diskdevstat
%attr(755,root,root) %{_sbindir}/scomes
%{_mandir}/man8/varnetload.*
%{_mandir}/man8/netdevstat.*
%{_mandir}/man8/diskdevstat.*
%{_mandir}/man8/scomes.*

%files profiles-sap
%defattr(644,root,root,755)
%{_prefix}/lib/tuned/sap-netweaver
%{_mandir}/man7/tuned-profiles-sap.7*

%files profiles-sap-hana
%defattr(644,root,root,755)
%{_prefix}/lib/tuned/sap-hana
%{_prefix}/lib/tuned/sap-hana-vmware
%{_mandir}/man7/tuned-profiles-sap-hana.7*

%files profiles-oracle
%defattr(644,root,root,755)
%{_prefix}/lib/tuned/oracle
%{_mandir}/man7/tuned-profiles-oracle.7*

%files profiles-atomic
%defattr(644,root,root,755)
%{_prefix}/lib/tuned/atomic-host
%{_prefix}/lib/tuned/atomic-guest
%{_mandir}/man7/tuned-profiles-atomic.7*

%files profiles-realtime
%defattr(644,root,root,755)
%config(noreplace) %{_sysconfdir}/tuned/realtime-variables.conf
%{_prefix}/lib/tuned/realtime
%{_mandir}/man7/tuned-profiles-realtime.7*

%files profiles-nfv
%defattr(644,root,root,755)
%config(noreplace) %{_sysconfdir}/tuned/realtime-virtual-guest-variables.conf
%config(noreplace) %{_sysconfdir}/tuned/realtime-virtual-host-variables.conf
%{_prefix}/lib/tuned/realtime-virtual-guest
%{_prefix}/lib/tuned/realtime-virtual-host
%{_libexecdir}/tuned/defirqaffinity*
%{_mandir}/man7/tuned-profiles-nfv.7*

%files profiles-compat
%defattr(644,root,root,755)
%{_prefix}/lib/tuned/default
%{_prefix}/lib/tuned/desktop-powersave
%{_prefix}/lib/tuned/laptop-ac-powersave
%{_prefix}/lib/tuned/server-powersave
%{_prefix}/lib/tuned/laptop-battery-powersave
%{_prefix}/lib/tuned/enterprise-storage
%{_prefix}/lib/tuned/spindown-disk
%{_mandir}/man7/tuned-profiles-compat.7*

%clean
rm -rf $RPM_BUILD_ROOT
