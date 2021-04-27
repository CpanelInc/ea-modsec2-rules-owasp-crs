Name: ea-modsec2-rules-owasp-crs
Summary: OWASP ModSecurity Core Rule Set (CRS)
Version: 3.3.1rc1
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4544 for more details
%define release_prefix 3
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

    # v2 is not compatible w/ EA4's mod sec version. We only want to back it up
    if [ -d "/etc/apache2/conf.d/modsec_vendor_configs/OWASP" ] ; then
        mkdir -p ~/old-cpanel-modsec2-rules-from-vendor-system/$DATE_SUBDIR
        touch ~/old-cpanel-modsec2-rules-from-vendor-system/$DATE_SUBDIR/had_OWASP-v2
        /usr/local/cpanel/scripts/modsec_vendor remove OWASP
    fi
fi

%post

/usr/local/cpanel/3rdparty/bin/perl -MCpanel::CachedDataStore -e \
  'my $hr=Cpanel::CachedDataStore::loaddatastore($ARGV[0]);$hr->{data}{OWASP3} = { distribution => "ea-modsec2-rules-owasp-crs", url => "N/A, it is done via RPM"};Cpanel::CachedDataStore::savedatastore($ARGV[0], { data => $hr->{data} })' \
  /var/cpanel/modsec_vendors/installed_from.yaml

UPDATES_DISABLED=0
if [ ! -f "%{_localstatedir}/lib/rpm-state/ea-modsec2-rules-owasp-crs/had_old" ] ; then
    /usr/local/cpanel/scripts/modsec_vendor enable OWASP3
    /usr/local/cpanel/scripts/modsec_vendor enable-updates OWASP3
else
   PERL=/usr/local/cpanel/3rdparty/bin/perl

   $PERL -MYAML::Syck -E 'my $h=YAML::Syck::LoadFile($ARGV[0]);exit(exists $h->{vendor_updates}{$ARGV[1]} ? 0 : 1);' /var/cpanel/modsec_cpanel_conf_datastore OWASP3
   if [ "$?" -ne "0" ] ; then
      UPDATES_DISABLED=1
      # this will add the yum.conf exclude if it is missing
      /usr/local/cpanel/scripts/modsec_vendor disable-updates OWASP3
   fi
fi

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

if [ "$DID_DEFAULTS" -eq "0" -a "$UPDATES_DISABLED" -eq "0" ] ; then
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
    rm -rf /var/cpanel/modsec_vendors/meta_OWASP3.cache /var/cpanel/modsec_vendors/installed_from.cache /var/cpanel/modsec_cpanel_conf_datastore.cache

    # 4. rebuild modsec2.cpanel.conf based on new modsec_cpanel_conf_datastore
    $PERL -MWhostmgr::ModSecurity::ModsecCpanelConf -e 'Whostmgr::ModSecurity::ModsecCpanelConf->new->manipulate(sub {})'

    # 5. remove updates-disabled from yum.conf
    $PERL -MCpanel::SysPkgs -e 'my $pkg = "ea-modsec2-rules-owasp-crs";my $sp = Cpanel::SysPkgs->new;$sp->parse_yum_conf;if ( grep { $_ eq $pkg } split /\s+/, $sp->{original_exclude_string} ) {$sp->{exclude_string} =~ s/(?:^$pkg$|^$pkg\s+|\s+$pkg\s+|\s+$pkg$)//g; $sp->write_yum_conf;}'
fi

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
* Tue Apr 27 2021 Daniel Muey <dan@cpanel.net> - 3.3.1rc1-3
- ZC-8787: Rolling “ea-modsec2-rules-owasp-crs” back to “3998949”: Need to get ZC-8756 out and do not want to publish an RC version

* Tue Apr 13 2021 Daniel Muey <dan@cpanel.net> - 3.3.1rc1-2
- ZC-8756: Update for upstream ULC changes

* Thu Feb 25 2021 Cory McIntire <cory@cpanel.net> - 3.3.1-rc-1
- EA-9606: Update ea-modsec2-rules-owasp-crs from v3.3.0 to v3.3.1-rc1

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
