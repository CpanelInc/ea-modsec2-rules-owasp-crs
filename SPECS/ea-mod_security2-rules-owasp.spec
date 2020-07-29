Name: ea-mod_security2-rules-owasp
Summary: OWASP ModSecurity Core Rule Set (CRS)
Version: 3.3.0
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4544 for more details
%define release_prefix 1
Release: %{release_prefix}%{?dist}.cpanel
Vendor: cPanel, Inc.
Group: System Environment/Libraries
License: Apache v2
URL: https://github.com/coreruleset/coreruleset

Source: https://github.com/coreruleset/coreruleset/archive/%{version}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
AutoReq:   no

%description
The OWASP ModSecurity Core Rule Set (CRS) is a set of generic attack detection
 rules for use with ModSecurity or compatible web application firewalls.
 The CRS aims to protect web applications from a wide range of attacks,
 including the OWASP Top Ten, with a minimum of false alerts.

%prep
%setup -q -n coreruleset-%{version}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/opt/cpanel/ea-mod_security2-rules-owasp

%if 0%{?rhel} >= 8
    perl -pi -e 's{#!/usr/bin/env python}{#!/usr/bin/env python3}' id_renumbering/update.py util/upgrade.py util/regexp-assemble/regexp-cmdline.py util/join-multiline-rules/join.py
%endif

/bin/cp -rf ./* $RPM_BUILD_ROOT/opt/cpanel/ea-mod_security2-rules-owasp

mkdir -p $RPM_BUILD_ROOT/etc/apache2/conf.d/modsec_vendor_configs/
ln -sf /opt/cpanel/ea-mod_security2-rules-owasp $RPM_BUILD_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ $1 -eq 1 ] ; then

    mkdir ~/old-cpanel-modsec2-rules-from-vendor-system
    # on install move voodoo dir and conf file (and its cache) out of the way
    if [ -d "/etc/apache2/conf.d/modsec_vendor_configs/OWASP3" ] ; then
        mv /etc/apache2/conf.d/modsec_vendor_configs/OWASP3 ~/old-cpanel-modsec2-rules-from-vendor-system/
    fi

    mv -f /var/cpanel/modsec_vendors/meta_OWASP3.yaml ~/old-cpanel-modsec2-rules-from-vendor-system/
    mv -f /var/cpanel/modsec_vendors/meta_OWASP3.cache ~/old-cpanel-modsec2-rules-from-vendor-system/
fi

%files
%defattr(-, root, root, -)
/opt/cpanel/ea-mod_security2-rules-owasp
/etc/apache2/conf.d/modsec_vendor_configs/OWASP3

%changelog
* Tue Jul 28 2020 Daniel Muey <dan@cpanel.net> - 3.3.0-1
- EA-9202: Update ea-mod_security2-rules-owasp from v3.0.2 to v3.3.0

* Tue Jul 28 2020 Dan Muey <dan@cpanel.net> - 3.0.2-1
- ZC-5711: initial release to match version in internal system
