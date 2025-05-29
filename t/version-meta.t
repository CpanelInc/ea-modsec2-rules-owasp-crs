#!/usr/local/cpanel/3rdparty/bin/perl

#                                      Copyright 2025 WebPros International, LLC
#                                                           All rights reserved.
# copyright@cpanel.net                                         http://cpanel.net
# This code is subject to the cPanel license. Unauthorized copying is prohibited.

## no critic qw(TestingAndDebugging::RequireUseStrict TestingAndDebugging::RequireUseWarnings)
use Test::Spec;    # automatically turns on strict and warnings

use FindBin;
use File::chdir;
use YAML::Syck;

use lib "$FindBin::Bin/../../ea-tools/lib/ea4_tool/";
use ea4_tool::util;
my $v2dir = "$FindBin::Bin/..";
my $cur_ver;

describe "post update" => sub {
    around {
        if ( !$cur_ver ) {
            local $CWD = $v2dir;
            my $specfile = ea4_tool::util::specfile($CWD);
            $cur_ver = ea4_tool::util::spec_get_version($specfile);
        }

        yield;
    };

    it 'should have updated meta description w/ new version' => sub {
        local $CWD = $v2dir;
        my $meta = YAML::Syck::LoadFile("SOURCES/meta_OWASP3.yaml");

        like $meta->{attributes}{description}, qr/ v\Q$cur_ver\E$/;
    };

    it 'should have added a new-rule list for new version' => sub {
        local $CWD = $v2dir;
        my $new = YAML::Syck::LoadFile("SOURCES/new_includes.yaml");

        is ref( $new->{$cur_ver} ), "ARRAY";
    };

    it 'should have updated v3.0 to new version' => sub {
        local $CWD = ea4_tool::util::get_path_of_repo("ea-modsec30-rules-owasp-crs");
        my $specfile = ea4_tool::util::specfile($CWD);
        my $version  = ea4_tool::util::spec_get_version($specfile);

        is $version, $cur_ver;
    };
};

runtests unless caller;
