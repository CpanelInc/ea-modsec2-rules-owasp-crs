#!/usr/local/cpanel/3rdparty/bin/perl

#                                      Copyright 2025 WebPros International, LLC
#                                                           All rights reserved.
# copyright@cpanel.net                                         http://cpanel.net
# This code is subject to the cPanel license. Unauthorized copying is prohibited.

use strict;
use warnings;

use YAML::Syck;

## no critic qw(TestingAndDebugging::RequireUseStrict TestingAndDebugging::RequireUseWarnings)
use Test::Spec;    # automatically turns on strict and warnings
use Test::FailWarnings;

use FindBin;
use Path::Tiny;

my %conf = (
    require => "$FindBin::Bin/../ea4-tool-post-update",
    package => "ea_modsec2_rules_owasp_crs::ea4_tool_post_update",
);
require $conf{require};

use Test::Fatal qw( dies_ok lives_ok );

describe "getcorerulesets" => sub {
    share my %mi;
    around {
        yield;
    };

    it 'should return a list of releases' => sub {
        my @releases = ea_modsec2_rules_owasp_crs::ea4_tool_post_update::getcorerulesets( "3.3.4", "3.3.7" );

        my $expected_ar = [
            {
                'name'    => '3.3.4.tar.gz',
                'version' => '3.3.4',
                'url'     => 'https://api.github.com/repos/coreruleset/coreruleset/tarball/v3.3.4'
            },
            {
                'name'    => '3.3.7.tar.gz',
                'version' => '3.3.7',
                'url'     => 'https://api.github.com/repos/coreruleset/coreruleset/tarball/v3.3.7'
            },
        ];

        cmp_deeply( \@releases, $expected_ar );
    };
};

describe "get_rules_from_ruleset" => sub {
    share my %mi;
    around {
        no warnings 'once';

        local *ea_modsec2_rules_owasp_crs::ea4_tool_post_update::get_tar_contents = sub {
            my ( $url, $name ) = @_;

            my $cwd        = $FindBin::Bin;
            my $data_fname = "$cwd/data/contents_$name";

            return map { chomp($_); $_ } path($data_fname)->lines;
        };

        yield;
    };

    it 'should return an hr of rules' => sub {
        my $release = {
            'name'    => '3.3.7.tar.gz',
            'version' => '3.3.7',
            'url'     => 'https://api.github.com/repos/coreruleset/coreruleset/tarball/v3.3.7'
        };

        my $rules_hr = ea_modsec2_rules_owasp_crs::ea4_tool_post_update::get_rules_from_ruleset($release);

        my $expected_hr = {
            'REQUEST-903.9002-WORDPRESS-EXCLUSION-RULES'      => 1,
            'REQUEST-920-PROTOCOL-ENFORCEMENT'                => 1,
            'REQUEST-921-PROTOCOL-ATTACK'                     => 1,
            'REQUEST-922-MULTIPART-ATTACK'                    => 1,
            'REQUEST-903.9001-DRUPAL-EXCLUSION-RULES'         => 1,
            'REQUEST-932-APPLICATION-ATTACK-RCE'              => 1,
            'REQUEST-903.9004-DOKUWIKI-EXCLUSION-RULES'       => 1,
            'RESPONSE-954-DATA-LEAKAGES-IIS'                  => 1,
            'REQUEST-911-METHOD-ENFORCEMENT'                  => 1,
            'REQUEST-901-INITIALIZATION'                      => 1,
            'REQUEST-913-SCANNER-DETECTION'                   => 1,
            'REQUEST-905-COMMON-EXCEPTIONS'                   => 1,
            'REQUEST-944-APPLICATION-ATTACK-JAVA'             => 1,
            'REQUEST-934-APPLICATION-ATTACK-NODEJS'           => 1,
            'REQUEST-930-APPLICATION-ATTACK-LFI'              => 1,
            'REQUEST-933-APPLICATION-ATTACK-PHP'              => 1,
            'REQUEST-942-APPLICATION-ATTACK-SQLI'             => 1,
            'REQUEST-912-DOS-PROTECTION'                      => 1,
            'RESPONSE-950-DATA-LEAKAGES'                      => 1,
            'RESPONSE-953-DATA-LEAKAGES-PHP'                  => 1,
            'REQUEST-903.9005-CPANEL-EXCLUSION-RULES'         => 1,
            'RESPONSE-959-BLOCKING-EVALUATION'                => 1,
            'REQUEST-941-APPLICATION-ATTACK-XSS'              => 1,
            'RESPONSE-952-DATA-LEAKAGES-JAVA'                 => 1,
            'RESPONSE-951-DATA-LEAKAGES-SQL'                  => 1,
            'RESPONSE-980-CORRELATION'                        => 1,
            'REQUEST-943-APPLICATION-ATTACK-SESSION-FIXATION' => 1,
            'REQUEST-910-IP-REPUTATION'                       => 1,
            'REQUEST-903.9003-NEXTCLOUD-EXCLUSION-RULES'      => 1,
            'REQUEST-949-BLOCKING-EVALUATION'                 => 1,
            'REQUEST-931-APPLICATION-ATTACK-RFI'              => 1,
            'REQUEST-903.9006-XENFORO-EXCLUSION-RULES'        => 1
        };

        cmp_deeply( $rules_hr, $expected_hr );
    };
};

describe "update_meta_OWASP3" => sub {
    share my %mi;
    around {
        # Maybe needed in the future
        yield;
    };

    it 'should return undef when 3.3.7 is already in the description' => sub {
        my $cwd = $FindBin::Bin;

        my $output_hr = ea_modsec2_rules_owasp_crs::ea4_tool_post_update::update_meta_OWASP3( "3.3.7", "$cwd/data/meta_OWASP3_02.yaml" );

        is( $output_hr, undef );
    };

    it 'should return the correct hr when 3.3.7 is not in the description' => sub {
        my $cwd = $FindBin::Bin;

        my $output_hr   = ea_modsec2_rules_owasp_crs::ea4_tool_post_update::update_meta_OWASP3( "3.3.7", "$cwd/data/meta_OWASP3_01.yaml" );
        my $expected_hr = YAML::Syck::LoadFile("$cwd/data/meta_OWASP3_02.yaml");

        cmp_deeply( $output_hr, $expected_hr );
    };

};

runtests unless caller;
