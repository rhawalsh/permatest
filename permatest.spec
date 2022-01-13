%define  debug_package %{nil}
Name:		permatest
Version:	1
Release:	1%{?dist}
Summary:	Permabit kernel module for logging
License:	GPLv2
URL:		http://www.permabit.com/
Source0:	%{name}-%{version}.tgz
Requires:       dkms
Requires:       kernel-devel
Requires:       make

%description
Permabit kernel logging module for use during testing

%prep
%setup -q

%build
# Nothing doing here, as we're going to build on whatever kernel we end up
# running inside.

%install
src_directory=$RPM_BUILD_ROOT/%{_usr}/src/%{name}-%{version}
mkdir -p ${src_directory}
cp -r * ${src_directory}/
cat > ${src_directory}/dkms.conf <<EOF
PACKAGE_NAME="permatest"
PACKAGE_VERSION="%{version}"
AUTOINSTALL="yes"

BUILT_MODULE_NAME[0]="permatest"
DEST_MODULE_LOCATION[0]="/kernel/drivers/block/"
STRIP[0]="no"
EOF

# Add the requirement that the 'permatest' module is loaded at boot
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/modules-load.d
cat > $RPM_BUILD_ROOT/%{_sysconfdir}/modules-load.d/permatest.conf <<EOF
permatest
EOF

%post
set -x
/usr/sbin/dkms --rpm_safe_upgrade add -m %{name} -v %{version}
/usr/sbin/dkms --rpm_safe_upgrade build -m %{name} -v %{version}
/usr/sbin/dkms --rpm_safe_upgrade install -m %{name} -v %{version}

%preun
# Check whether permatest is loaded, and if so attempt to remove it.  A failure
# here means there is still something using the module, which should be cleared
# up before attempting to remove again.
if grep -q "^permatest" /proc/modules; then
  modprobe -r permatest
fi
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{name} -v %{version} --all || :

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%{_usr}/src/%{name}-%{version}
%{_sysconfdir}/modules-load.d/permatest.conf

%changelog
* Wed Jan 12 2022 Andy Walsh <awalsh@permabit.com> 1-1
- Initial implementation
