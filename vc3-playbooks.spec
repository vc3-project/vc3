#%define vers %{getenv:BUILDTAG}
Name: vc3-playbooks

Version: 1.1.0
Release: 1
Summary: Pilot and software installer

License: MIT
URL: https://github.com/vc3-project/vc3-playbooks

# tarball generation:
# ------------------- 
# cd ~/rpmbuild/SOURCES
# git clone --depth=1 https://github.com/vc3-project/vc3-playbooks
# rm -rf vc3-builder/.git*
# tar -cvzf vc3-builder-1.1.0-src.tgz vc3-builder
Source0: vc3-playbooks-1.1.0-src.tgz

BuildArch: noarch
# Requires: 

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}

%description


%prep
%setup -q -n vc3-playbooks

%build

%install
mkdir -p %{buildroot}/%{_sysconfdir}/vc3/vc3-playbooks
cp -r * %{buildroot}/%{_sysconfdir}/vc3/vc3-playbooks
rm -f %{buildroot}/%{_sysconfdir}/vc3/vc3-playbooks/vc3-playbooks.spec

%files
%{_sysconfdir}/vc3/vc3-playbooks/login/login-dynamic.yaml
%{_sysconfdir}/vc3/vc3-playbooks/login/login.yaml
%{_sysconfdir}/vc3/vc3-playbooks/login/templates/condor_config.local.j2
%{_sysconfdir}/vc3/vc3-playbooks/login/templates/cvmfs_default_local.j2
%{_sysconfdir}/vc3/vc3-playbooks/login/templates/motd.j2


%changelog
* Wed Oct 03 2018 Lincoln Bryant <lincolnb@uchicago.edu> - 1.1.0-1
- Updated
* Mon May 07 2018 Lincoln Bryant <lincolnb@uchicago.edu> - 1.0.0-1
- Initial package
