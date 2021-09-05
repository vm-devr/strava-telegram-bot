#!/usr/bin/perl -wImodules
use warnings;
use strict;
use DBI;
use List::Util();
use Data::Dumper qw(Dumper);

#use modules 'modules';
use parser;

if (!@ARGV) {
	print ("Invalid input parameters, pass athletes ids");
	exit;
}

StravaParser::openDB();
StravaParser::createTables();
if (StravaParser::login()) {
	my $athlnum = 0;
	while (1) {
		for my $athlete (@ARGV) {
			$athlnum ++;
			print "$athlnum | ";
			eval { StravaParser::updateAthleteStats($athlete); };
			warn $@ if $@;
			my $wait = int(rand(60));
			print " waiting for $wait minutes\n";

			#sleep $wait * 60;
		}
		last;
		sleep 4 * 60 * 60;
	}
}
