Name: ea-modsec2-rules-owasp-crs
Summary: OWASP ModSecurity Core Rule Set (CRS)
Version: 3.3.0
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4544 for more details
%define release_prefix 1
Release: %{release_prefix}%{?dist}.cpanel
Vendor: cPanel, Inc.
Group: System Environment/Libraries
License: Apache v2
URL: https://github.com/coreruleset/coreruleset

Source0: https://github.com/coreruleset/coreruleset/archive/%{version}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
AutoReq:   no

%description
The OWASP ModSecurity Core Rule Set (CRS) is a set of generic attack detection
 rules for use with ModSecurity or compatible web application firewalls.
 The CRS aims to protect web applications from a wide range of attacks,
 including the OWASP Top Ten, with a minimum of false alerts.

%prep

# the tarball’s root dir is `coreruleset-coreruleset-<SHA>/`
#   - maintaining that SHA would be tedious and prone to forgetting to do it until the first build failed
#   - we can’t use `coreruleset-coreruleset-*` because it is executed as `cd 'coreruleset-coreruleset-*'`
%setup -q -n %(tar tzf %{SOURCE0} | head -n 1)

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/opt/cpanel/ea-modsec2-rules-owasp-crs

%if 0%{?rhel} >= 8
    perl -pi -e 's{#!/usr/bin/env python}{#!/usr/bin/env python3}' util/crs2-renumbering/update.py tests/regression/tests/base_positive_rules.py util/regexp-assemble/regexp-cmdline.py util/join-multiline-rules/join.py
%endif

/bin/cp -rf ./* $RPM_BUILD_ROOT/opt/cpanel/ea-modsec2-rules-owasp-crs
/bin/cp -f ./crs-setup.conf.example $RPM_BUILD_ROOT/opt/cpanel/ea-modsec2-rules-owasp-crs/crs-setup.conf

mkdir -p $RPM_BUILD_ROOT/etc/apache2/conf.d/modsec_vendor_configs/
ln -sf /opt/cpanel/ea-modsec2-rules-owasp-crs $RPM_BUILD_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ $1 -eq 1 ] ; then

    # on install move voodoo dir and conf file (and its cache) out of the way
    if [ -d "/etc/apache2/conf.d/modsec_vendor_configs/OWASP3" ] ; then
        mkdir -p ~/old-cpanel-modsec2-rules-from-vendor-system
        mv /etc/apache2/conf.d/modsec_vendor_configs/OWASP3 ~/old-cpanel-modsec2-rules-from-vendor-system/
    fi

    if [ -f "/var/cpanel/modsec_vendors/meta_OWASP3.yaml" ] ; then
        mkdir -p ~/old-cpanel-modsec2-rules-from-vendor-system
        mv -f /var/cpanel/modsec_vendors/meta_OWASP3.yaml ~/old-cpanel-modsec2-rules-from-vendor-system/
    fi

    if [ -f "/var/cpanel/modsec_vendors/meta_OWASP3.cache" ] ; then
        mkdir -p ~/old-cpanel-modsec2-rules-from-vendor-system
        mv -f /var/cpanel/modsec_vendors/meta_OWASP3.cache ~/old-cpanel-modsec2-rules-from-vendor-system/
    fi
fi

%files
%defattr(-, root, root, -)
/opt/cpanel/ea-modsec2-rules-owasp-crs
/etc/apache2/conf.d/modsec_vendor_configs/OWASP3

%changelog
* Tue Jul 28 2020 Daniel Muey <dan@cpanel.net> - 3.3.0-1
- EA-9202: Update ea-modsec2-rules-owasp-crs from v3.0.2 to v3.3.0

* Tue Jul 28 2020 Dan Muey <dan@cpanel.net> - 3.0.2-1
- ZC-5711: initial release to match version in internal system
