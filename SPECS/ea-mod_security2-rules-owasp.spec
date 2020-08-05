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
Source1: default_includes.conf
Source2: new_includes.conf

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
/bin/cp -f %{SOURCE1} $RPM_BUILD_ROOT/opt/cpanel/ea-modsec2-rules-owasp-crs/
/bin/cp -f %{SOURCE2} $RPM_BUILD_ROOT/opt/cpanel/ea-modsec2-rules-owasp-crs/

mkdir -p $RPM_BUILD_ROOT/etc/apache2/conf.d/modsec_vendor_configs/
ln -sf /opt/cpanel/ea-modsec2-rules-owasp-crs $RPM_BUILD_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ $1 -eq 1 ] ; then
    if [ -e "%{_localstatedir}/lib/rpm-state/ea-modsec2-rules-owasp-crs/had_old" ] ; then
        unlink %{_localstatedir}/lib/rpm-state/ea-modsec2-rules-owasp-crs/had_old
    else
        mkdir -p %{_localstatedir}/lib/rpm-state/ea-modsec2-rules-owasp-crs
    fi

    DATE_SUBDIR=`date --iso-8601=seconds`
    # on install move voodoo dir and conf file (and its cache) out of the way
    if [ -d "/etc/apache2/conf.d/modsec_vendor_configs/OWASP3" ] ; then
        touch %{_localstatedir}/lib/rpm-state/ea-modsec2-rules-owasp-crs/had_old
        mkdir -p ~/old-cpanel-modsec2-rules-from-vendor-system/$DATE_SUBDIR
        mv /etc/apache2/conf.d/modsec_vendor_configs/OWASP3 ~/old-cpanel-modsec2-rules-from-vendor-system/$DATE_SUBDIR/
    fi

    if [ -f "/var/cpanel/modsec_vendors/meta_OWASP3.yaml" ] ; then
        touch %{_localstatedir}/lib/rpm-state/ea-modsec2-rules-owasp-crs/had_old
        mkdir -p ~/old-cpanel-modsec2-rules-from-vendor-system/$DATE_SUBDIR
        mv -f /var/cpanel/modsec_vendors/meta_OWASP3.yaml ~/old-cpanel-modsec2-rules-from-vendor-system/$DATE_SUBDIR/
    fi

    # this file is left behind when removing the vendor so it is not an indicator of if they have the old vendor or not
    if [ -f "/var/cpanel/modsec_vendors/meta_OWASP3.cache" ] ; then
        mkdir -p ~/old-cpanel-modsec2-rules-from-vendor-system/$DATE_SUBDIR
        mv -f /var/cpanel/modsec_vendors/meta_OWASP3.cache ~/old-cpanel-modsec2-rules-from-vendor-system/$DATE_SUBDIR/
    fi
fi

%post

DID_DEFAULTS=0
if [ $1 -eq 1 ] ; then
    if [ ! -f "%{_localstatedir}/lib/rpm-state/ea-modsec2-rules-owasp-crs/had_old" ] ; then
        grep --silent '^Include "/etc/apache2/conf.d/modsec_vendor_configs/OWASP3/' /etc/apache2/conf.d/modsec/modsec2.cpanel.conf
        if [ "$?" -ne "0" ] ; then
            grep --silent '## ModSecurity configuration file includes:' /etc/apache2/conf.d/modsec/modsec2.cpanel.conf
            if [ "$?" -eq "0" ] ; then
                DID_DEFAULTS=1
                sed -i '/## ModSecurity configuration file includes:/r /opt/cpanel/ea-modsec2-rules-owasp-crs/default_includes.conf' /etc/apache2/conf.d/modsec/modsec2.cpanel.conf
            else
                DID_DEFAULTS=1
                cat /opt/cpanel/ea-modsec2-rules-owasp-crs/default_includes.conf >> /etc/apache2/conf.d/modsec/modsec2.cpanel.conf
            fi
        fi
    fi
fi

if [ "$DID_DEFAULTS" -eq "0" ] ; then
    echo "Checking new rules"
    NEWRULES_PATH=/opt/cpanel/ea-modsec2-rules-owasp-crs/new_includes.conf

    SYNTAX_CHECK=$(/usr/sbin/httpd -DSSL -e error -t -f /etc/apache2/conf/httpd.conf -C "Include '$NEWRULES_PATH'" 2>&1)
    if [ "$?" -eq "0" ] ; then
        echo "Adding new rules from $NEWRULES_PATH"
        cat $NEWRULES_PATH >> /etc/apache2/conf.d/modsec/modsec2.cpanel.conf
    else
        MSG="New rules ($NEWRULES_PATH) could not be added due to this error:\n$SYNTAX_CHECK\n"
        echo -e $MSG
        echo -e "[%{name} v%{version}-%{release}]\n$MSG[/%{name}]\n" >> /usr/local/cpanel/logs/error_log
    fi
fi

%postun

if [ $1 -eq 0 ] ; then
    sed -i '/^Include "\/etc\/apache2\/conf\.d\/modsec_vendor_configs\/OWASP3\//d' /etc/apache2/conf.d/modsec/modsec2.cpanel.conf
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
