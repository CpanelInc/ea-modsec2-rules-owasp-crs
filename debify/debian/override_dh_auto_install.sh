#!/bin/bash

source debian/vars.sh

set -x

mkdir -p $DEB_INSTALL_ROOT/opt/cpanel/ea-modsec2-rules-owasp-crs
    perl -pi -e 's{#!/usr/bin/env python}{#!/usr/bin/env python3}' util/crs2-renumbering/update.py tests/regression/tests/base_positive_rules.py util/regexp-assemble/regexp-cmdline.py util/join-multiline-rules/join.py
mkdir -p $DEB_INSTALL_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3
/bin/cp -rf ./* $DEB_INSTALL_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3
# the system will pull these into to the list of rule sets unless they are renamed
for conf in $(ls $DEB_INSTALL_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3/util/honeypot-sensor/*.conf)
do
    /bin/mv -f $conf $conf.example
done
/bin/cp -f ./crs-setup.conf.example $DEB_INSTALL_ROOT/etc/apache2/conf.d/modsec_vendor_configs/OWASP3/crs-setup.conf
mkdir -p $DEB_INSTALL_ROOT/opt/cpanel/ea-modsec2-rules-owasp-crs/
/bin/cp -f $SOURCE1 $DEB_INSTALL_ROOT/opt/cpanel/ea-modsec2-rules-owasp-crs/
mkdir -p $DEB_INSTALL_ROOT/var/cpanel/modsec_vendors/
/bin/cp -f $SOURCE2 $DEB_INSTALL_ROOT/var/cpanel/modsec_vendors/meta_OWASP3.yaml
/bin/cp -f $SOURCE2 $DEB_INSTALL_ROOT/opt/cpanel/ea-modsec2-rules-owasp-crs/
