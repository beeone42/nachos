#!/usr/bin/perl

BEGIN { @k = unpack "C*", pack "H*", "1734516E8BA8C5E2FF1C39567390ADCA" };

$_ = $ARGV[0];
chomp;
s/^(.{8}).*/$1/;
@p = unpack "C*", $_;

foreach (@k) {
    printf "%02X", $_ ^ (shift @p || 0)
};

print "\n"
