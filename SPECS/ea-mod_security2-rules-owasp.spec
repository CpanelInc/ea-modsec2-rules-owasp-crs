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
Source1: new_includes.yaml
Source2: meta_OWASP3.yaml

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

/usr/local/cpanel/3rdparty/bin/perl -MCpanel::CachedDataStore -e \
  'my $hr=Cpanel::CachedDataStore::loaddatastore($ARGV[0]);$hr->{data}{OWASP3} = { distribution => "ea-modsec2-rules-owasp-crs", url => "N/A, it is done via RPM"};Cpanel::CachedDataStore::savedatastore($ARGV[0], { data => $hr->{data} })' \
  /var/cpanel/modsec_vendors/installed_from.yaml

/usr/local/cpanel/scripts/modsec_vendor enable OWASP3
/usr/local/cpanel/scripts/modsec_vendor disable-updates OWASP3 # RPM will be doing the updates not this system

DID_DEFAULTS=0
if [ $1 -eq 1 ] ; then
    if [ ! -f "%{_localstatedir}/lib/rpm-state/ea-modsec2-rules-owasp-crs/had_old" ] ; then
        grep --silent '  modsec_vendor_configs/OWASP3/' /var/cpanel/modsec_cpanel_conf_datastore
        if [ "$?" -ne "0" ] ; then
            DID_DEFAULTS=1
            /usr/local/cpanel/scripts/modsec_vendor enable-configs OWASP3
        fi
    fi
fi

if [ "$DID_DEFAULTS" -eq "0" ] ; then
    echo "Checking new rules"
    ADDED_NEW_RULE=0
    NEWRULES_PATH=/opt/cpanel/ea-modsec2-rules-owasp-crs/new_includes.yaml
    NEWRULES_REL=/etc/apache2/conf.d/modsec_vendor_configs/OWASP3/rules
    CONFIG_REL=modsec_vendor_configs/OWASP3/rules
    PERL=/usr/local/cpanel/3rdparty/bin/perl


    for RULE in $($PERL -MYAML::Syck -e 'my $h=YAML::Syck::LoadFile($ARGV[0]);if (exists $h->{$ARGV[1]}) { print "$_\n" for @{ $h->{$ARGV[1]} } }' $NEWRULES_PATH %{version})
    do
        $PERL -MYAML::Syck -e 'my $h=YAML::Syck::LoadFile($ARGV[0]);exit( $h->{active_configs}{$ARGV[1]} ? 0 : 1)' /var/cpanel/modsec_cpanel_conf_datastore $CONFIG_REL/$RULE
        if [ "$?" -eq "1" ] ; then
            SYNTAX_CHECK=$(/usr/sbin/httpd -DSSL -e error -t -f /etc/apache2/conf/httpd.conf -C "Include '$NEWRULES_REL/$RULE'" 2>&1)
            if [ "$?" -eq "0" ] ; then
                ADDED_NEW_RULE=1
                echo "Adding new rule set: $RULE"
                $PERL -MYAML::Syck -e 'my $h=YAML::Syck::LoadFile($ARGV[0]);$h->{active_configs}{$ARGV[1]} = 1;YAML::Syck::DumpFile($ARGV[0], $h)' /var/cpanel/modsec_cpanel_conf_datastore $CONFIG_REL/$RULE
            else
                MSG="New rule set ($RULE) could not be added due to this error:\n$SYNTAX_CHECK\n"
                echo -e $MSG
                echo -e "[%{name} v%{version}-%{release}]\n$MSG[/%{name}]\n" >> /usr/local/cpanel/logs/error_log
            fi
        fi
    done

    if [ "$ADDED_NEW_RULE" -eq "1" ] ; then
        echo "Rebuilding /etc/apache2/conf.d/modsec/modsec2.cpanel.conf with new rules"
        $PERL -MWhostmgr::ModSecurity::ModsecCpanelConf -e 'Whostmgr::ModSecurity::ModsecCpanelConf->new->manipulate(sub {})'
    fi
fi

%preun

if [ $1 -eq 0 ] ; then
    echo "Removing OWASP3 config"
    PERL=/usr/local/cpanel/3rdparty/bin/perl

    # We can't `/usr/local/cpanel/scripts/modsec_vendor remove OWASP3`
    #   because it also removes the RPM owned files creating many warnings later
    #   so we emulate the bits we need

    # 1. update installed_from.yaml
    $PERL -MCpanel::CachedDataStore -e \
      'my $hr=Cpanel::CachedDataStore::loaddatastore($ARGV[0]);delete $hr->{data}{OWASP3};Cpanel::CachedDataStore::savedatastore($ARGV[0], { data => $hr->{data} })' \
      /var/cpanel/modsec_vendors/installed_from.yaml

    # 2. update modsec_cpanel_conf_datastore
    $PERL -MYAML::Syck -e 'my $h=YAML::Syck::LoadFile($ARGV[0]);delete $h->{active_vendors}{OWASP3};delete $h->{vendor_updates}{OWASP3};for my $rid (keys %{$h->{disabled_rules}}) { delete $h->{disabled_rules}{$rid} if $h->{disabled_rules}{$rid} eq "OWASP3" } for my $pth (keys %{$h->{active_configs}}) { delete $h->{active_configs}{$pth} if $pth =~ m{^modsec_vendor_configs/OWASP3/} } YAML::Syck::DumpFile($ARGV[0], $h)' /var/cpanel/modsec_cpanel_conf_datastore

    #. 3 kill caches
    rm -rf /var/cpanel/modsec_vendors/meta_OWASP3.cache /var/cpanel/modsec_vendors/installed_from.cache /var/cpanel/modsec_cpanel_c    onf_datastore.cache

    # 4. rebuild modsec2.cpanel.conf based on new modsec_cpanel_conf_datastore
    $PERL -MWhostmgr::ModSecurity::ModsecCpanelConf -e 'Whostmgr::ModSecurity::ModsecCpanelConf->new->manipulate(sub {})'
fi

%files
%defattr(-, root, root, -)
/opt/cpanel/ea-modsec2-rules-owasp-crs
/etc/apache2/conf.d/modsec_vendor_configs/OWASP3
/var/cpanel/modsec_vendors/meta_OWASP3.yaml

%changelog
* Tue Jul 28 2020 Daniel Muey <dan@cpanel.net> - 3.3.0-1
- EA-9202: Update ea-modsec2-rules-owasp-crs from v3.0.2 to v3.3.0

* Tue Jul 28 2020 Dan Muey <dan@cpanel.net> - 3.0.2-1
- ZC-5711: initial release to match version in internal system
