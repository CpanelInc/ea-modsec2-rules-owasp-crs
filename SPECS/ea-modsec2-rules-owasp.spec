Name: ea-modsec2-rules-owasp-crs
Summary: OWASP ModSecurity Core Rule Set (CRS)
Version: 3.3.4
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4544 for more details
%define release_prefix 1
Release: %{release_prefix}%{?dist}.cpanel
Vendor: cPanel, Inc.
Group: System Environment/Libraries
License: Apache v2
URL: https://github.com/coreruleset/coreruleset

Provides: ea-modsec-rules-owasp-crs
Conflicts: ea-modsec-rules-owasp-crs
Requires: ea-apache24-mod_security2

Source0: https://github.com/coreruleset/coreruleset/archive/%{version}.tar.gz
Source1: new_includes.yaml
Source2: meta_OWASP3.yaml
Source3: pkg.prerm
Source4: pkg.postinst
Source5: pkg.preinst

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

mkdir -p $RPM_BUILD_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3
/bin/cp -rf ./* $RPM_BUILD_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3

# the system will pull these into to the list of rule sets unless they are renamed
for conf in $(ls $RPM_BUILD_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3/util/honeypot-sensor/*.conf)
do
    /bin/mv -f $conf $conf.example
done

/bin/cp -f ./crs-setup.conf.example $RPM_BUILD_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3/crs-setup.conf

mkdir -p $RPM_BUILD_ROOT/opt/cpanel/ea-modsec2-rules-owasp-crs/
/bin/cp -f %{SOURCE1} $RPM_BUILD_ROOT/opt/cpanel/ea-modsec2-rules-owasp-crs/

mkdir -p $RPM_BUILD_ROOT/var/cpanel/modsec_vendors/
/bin/cp -f %{SOURCE2} $RPM_BUILD_ROOT/var/cpanel/modsec_vendors/meta_OWASP3.yaml
/bin/cp -f %{SOURCE2} $RPM_BUILD_ROOT/opt/cpanel/ea-modsec2-rules-owasp-crs/

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%include %{SOURCE5}

%post
%include %{SOURCE4}

%preun
%include %{SOURCE3}

%posttrans

PERL=/usr/local/cpanel/3rdparty/bin/perl
$PERL -MWhostmgr::ModSecurity::ModsecCpanelConf -e 'Whostmgr::ModSecurity::ModsecCpanelConf->new->manipulate(sub {})'

%files
%defattr(-, root, root, -)
/opt/cpanel/ea-modsec2-rules-owasp-crs
/etc/apache2/conf.d/modsec_vendor_configs/OWASP3
/var/cpanel/modsec_vendors/meta_OWASP3.yaml
/opt/cpanel/ea-modsec2-rules-owasp-crs/meta_OWASP3.yaml

%changelog
* Wed Sep 21 2022 Cory McIntire <cory@cpanel.net> - 3.3.4-1
- EA-10944: Update ea-modsec2-rules-owasp-crs from v3.3.2 to v3.3.4

* Wed Mar 16 2022 Travis Holloway <t.holloway@cpanel.net> - 3.3.2-4
- EA-10394: Update version in meta_OWASP3.yaml

* Wed Nov 03 2021 Travis Holloway <t.holloway@cpanel.net> - 3.3.2-3
- EA-10240: Update verbiage to be OS neutral

* Wed Oct 20 2021 Dan Muey <dan@cpanel.net> - 3.3.2-2
- ZC-9412: Add `is_pkg` for 102 and beyond

* Wed Jun 30 2021 Cory McIntire <cory@cpanel.net> - 3.3.2-1
- EA-9921: Update ea-modsec2-rules-owasp-crs from v3.3.0 to v3.3.2

* Tue Jun 29 2021 Cory McIntire <cory@cpanel.net> - 3.3.0-9
- EA-9913: Update DRUPAL ruleset for CVE-2021-35368

* Tue May 18 2021 Cory McIntire <cory@cpanel.net> - 3.3.0-8
-EA-9785: Revert non-working https fix from EA-9773

* Thu May 13 2021 Cory McIntire <cory@cpanel.net> - 3.3.0-7
- EA-9773: Update unsupported https to http in meta_OWASP3.yaml file

* Tue Apr 13 2021 Daniel Muey <dan@cpanel.net> - 3.3.0-6
- ZC-8756: Update for upstream ULC changes

* Mon Feb 22 2021 Daniel Muey <dan@cpanel.net> - 3.3.0-5
- ZC-8471: conflict w/ modsec 3 not ea-nginx

* Tue Oct 06 2020 Daniel Muey <dan@cpanel.net> - 3.3.0-4
- ZC-7710: If already disabled, re-disable to get the yum.conf to match reality

* Tue Sep 29 2020 Daniel Muey <dan@cpanel.net> - 3.3.0-3
- ZC-7337: Changes to support ULC enabling/disabling updates for an RPM based vendor

* Wed Sep 02 2020 Daniel Muey <dan@cpanel.net> - 3.3.0-2
- ZC-7376: Bump release_prefix to work around OBS event

* Tue Jul 28 2020 Daniel Muey <dan@cpanel.net> - 3.3.0-1
- EA-9202: Update ea-modsec2-rules-owasp-crs from v3.0.2 to v3.3.0

* Tue Jul 28 2020 Dan Muey <dan@cpanel.net> - 3.0.2-1
- ZC-5711: initial release to match version in internal system
