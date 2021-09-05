package StravaReport;

use warnings;
use strict;
use v5.10;
use Time::Piece;
use Date::Manip;
use POSIX;
use Try::Tiny;
use List::Util();
use Data::Dumper;
use POSIX qw(strftime);
use parser;

binmode(STDOUT, ":utf8");

sub getReportConfig {
    my ($reportdir) = @_;

    # Opening the config file
    my $file = $reportdir . '/config.dat';
    open(FH, $file) or return undef;

    my $report_pattern = <FH>;
    my $sql_query = '';
    while(<FH>) {
        $sql_query .= $_;
    }

    chomp $report_pattern;
    chomp $sql_query;

    return {pattern => $reportdir . '/' . $report_pattern, sql => $sql_query };
}

sub getLastReport {
    my ($pattern) = @_;

    # Search for last report
    my ($last_report) = sort {$b cmp $a}  glob($pattern);
    if (!$last_report) {
        return { };
    }

    # Read last report
    open(FH, $last_report) or return undef;
    my %report = ();
    while(<FH>) {
        my $row = $_;
        my %record = ();
        while($row =~ /<td data='(\w+)'>(.*?)<\/td>/g) {
            $record{$1} = $2;
        }
        if (%record && $record{ID}) {
            $report{$record{ID}} = \%record;
        }
    }

    return \%report;
}

sub buildRankField {
    my ($rank, $name, $rec, $rec_old) = @_;

    if (defined $rec_old) {
        my ($rank_old) = split(/ /, $rec_old->{$name});
        my $diff = $rank_old - $rank;
        if ($diff > 1) {
            $rank .= " <span style = 'color:#008000'> ▲$diff</span>";
        }
        elsif ($diff > 0) {
            $rank .= " <span style = 'color:#008000'> ▲</span>";
        }
        elsif ($diff < -1) {
            $diff *= -1;
            $rank .= " <span style = 'color:#ff0000'> ▼$diff</span>";
        }
        elsif ($diff < 0) {
            $rank .= " <span style = 'color:#ff0000'> ▼</span>";
        }
    }
    return $rank;
}

sub buildNameField {
    my ($rank, $name, $rec, $rec_old) = @_;

    return $rec->{$name};
}

sub buildDistanceField {
    my ($rank, $name, $rec, $rec_old) = @_;

    if (defined $rec_old) {
        my ($dist_old) = split(/ /, $rec_old->{$name});
        my $diff = $rec->{$name} - $dist_old;

        if ($diff > 0) {
            return $rec->{$name} . " (+$diff) km";
        }
    }

    return $rec->{$name} . " km";
}

sub buildNewReport {
    my ($report_new, $report_last, $output_dir) = @_;

    #Build fields order
    my $field_name = 'Name';
    my $field_dist = 'Distance';
    my $field_debug = 'Debug';
    my $field_id = 'ID';
    my $field_rank = 'Rank';
    my %field_builder = (
        $field_rank => \&buildRankField,
        $field_name => \&buildNameField,
        $field_dist => \&buildDistanceField,
    );

    my $first_rec = $report_new->[0];
    my @fields = ($field_rank, $field_name, $field_dist);
    my @rec_fields = keys %$first_rec;
    foreach my $key (@rec_fields) {
        if (!grep /$key/, ($field_rank, $field_name, $field_dist, $field_debug, $field_id)) {
            push @fields, $key;
        }
    }

    if (!grep /$field_dist/, @rec_fields) {
        splice @fields, 2, 1;
    }

    push @fields, $field_id;
    if (defined $first_rec->{$field_debug}) {
        push @fields, $field_debug;
    }

    my $report_data =
        "<!DOCTYPE html>\n<html lang='uk'>\n" .
        "<head>\n\t<meta charset='utf-8'>" .
        "<style>table {border-collapse: collapse} th, td {border: 1px solid #ccc;} td {padding-left: 5px;padding-right: 5px;padding-top: 3px;padding-bottom: 3px} th {background:#ccc} tr:nth-child(even) {background:#f9f9f9} tr:nth-child(odd){background:#ddd}</style>" .
        "</head><body>\n\t<table>\n\t\t<tr>" .
        join('', map { "<th>$_</th>" } @fields) .
        "</tr>\n";
    my $rank = 1;

    foreach my $rec (@$report_new) {
        $report_data .= "\t\t<tr>";

        foreach my $field (@fields) {
            $report_data .= "<td data='$field'>";
            if (defined $field_builder{$field}) {
                $report_data .= $field_builder{$field}($rank, $field, $rec, $report_last ? $report_last->{$rec->{$field_id}} : "");
            } else {
                $report_data .= $rec->{$field};
            }
            $report_data .= "</td>";
        }

        $report_data .= "</tr>\n";
        $rank += 1;
    }
    $report_data .= "\t</table>\n</body></html>";

    my $report_file = $output_dir . "/" . strftime("%Y-%m-%d-%H-%M-%S", localtime) . ".html";
    open my $out, '>', $report_file;
    print {$out} $report_data;
    close $out;
}