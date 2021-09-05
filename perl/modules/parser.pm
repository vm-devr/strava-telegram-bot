package StravaParser;

use warnings;
use strict;
use v5.10;
use WWW::Mechanize ();
use WWW::Mechanize::TreeBuilder;
use HTTP::CookieJar::LWP ();
use Time::Piece;
use Date::Manip;
use POSIX qw(strftime);
use POSIX;
use Try::Tiny;
use List::Util();
use Data::Dumper;

binmode(STDOUT, ":utf8");
BEGIN{ $| = 1; }

sub openDB {
	my $database = "grc.db";
	my $dsn = "DBI:SQLite:dbname=$database";
	our $dbh = DBI->connect($dsn, "", "")
	   or die $DBI::errstr;
}

sub createTables {
	my @ddl = (
	# create athletes table
	"CREATE TABLE IF NOT EXISTS athletes (
		id int(11) NOT NULL PRIMARY KEY,
		name varchar(255) NOT NULL,
		img_path varchar(255),
		epb_1km int(11),
		epb_1ml int(11),
		epb_5km int(11),
		epb_10km int(11),
		epb_hm int(11),
		epb_m int(11),
		dst_all real,
		dst_2019 real,
		dst_2020 real);",

	# create athletes_stats table
	"CREATE TABLE IF NOT EXISTS athletes_stats (
		processed varchar(30) NOT NULL,
		athlete_id int(11) NOT NULL,
		distance int(11) NOT NULL);"
	);


	# execute all create table statements
	our $dbh;
	for my $sql(@ddl){
		$dbh->do($sql);
	}
}

sub insertAthlete {
	my ($id, $name) = @_;

	if (checkAthlete($id)) {
		return;
	}

	print "Inserting athlete: $id $name\n";

	# insert athlete
	our $dbh;
	$name = escapeForSQL($name);
	my $sql = "INSERT INTO athletes (id, name) VALUES ($id, '$name');";
	$dbh->do($sql);
}

sub updateAthlete {
	my ($id, $epb_1km, $epb_1ml, $epb_5km, $epb_10km, $epb_hm, $epb_m, $dst_all, $dst_2020) = @_;

	# insert athlete
	our $dbh;
	my $sql = "UPDATE athletes SET epb_1km=$epb_1km, epb_1ml=$epb_1ml, epb_5km=$epb_5km, epb_10km=$epb_10km, epb_hm=$epb_hm, epb_m=$epb_m, dst_all=$dst_all, dst_2020=$dst_2020 WHERE id=$id;";
	$dbh->do($sql);
}

sub checkAthleteStatsStart {
	my ($id) = @_;

	our $dbh;
	my $sql = "SELECT * FROM athletes_stats WHERE processed='2021-01-01 00:00:00' AND athlete_id=$id";
	my $sth = $dbh->prepare($sql);
	my $found = 0;
	if ($sth) {
		if ($sth->execute()) {
			if(my @row = $sth->fetchrow_array) {
				return 1;
			}
		}
		$sth->finish();
	}

	return 0;
}

sub insertAthleteStats {
	my ($id, $dst_all, $dst_2020) = @_;

	# insert athlete
	our $dbh;
	my $dttm = strftime("%Y-%m-%d %H:%M:%S", localtime);
	my $sql = "INSERT INTO athletes_stats (processed, athlete_id, distance) VALUES ('$dttm', $id, $dst_all)";
	$dbh->do($sql);
	print "$dttm $id $dst_all";

	# update start year data
	if (!checkAthleteStatsStart($id)) {
		my $dt2020start = "2021-01-01 00:00:00";
		my $dst = $dst_all - $dst_2020;
		$sql = "INSERT INTO athletes_stats (processed, athlete_id, distance) VALUES ('$dt2020start', $id, $dst)";
		$dbh->do($sql);
	}
}

sub getAllAthletes {
	my $maxresults = shift;
	my @res = ();

	our $dbh;
	my $sql = "SELECT * FROM athletes";
	if (defined $maxresults and $maxresults > 0) {
		$sql = "SELECT athlete_id FROM activities GROUP BY athlete_id ORDER BY SUM(distance) DESC LIMIT $maxresults";
	}
	my $sth = $dbh->prepare($sql);
	my $found = 0;
	if ($sth) {
		if ($sth->execute()) {
			while(my @row = $sth->fetchrow_array) {
				push @res, $row[0];
			}
		}
		$sth->finish();
	}

	return @res;

}

sub execSQL {
	my $sql = shift;
	my @res = ();

	our $dbh;
	my $sth = $dbh->prepare($sql);
	if ($sth) {
		if ($sth->execute()) {
			while(my $row = $sth->fetchrow_hashref) {
				push @res, $row;
			}
		}
		$sth->finish();
	}

	return \@res;
}

sub escapeForSQL {
	my ($str) = @_;
	$str =~ s/([\\"'])/ /g;
	return $str;
}

sub insertActivity {
	my ($id, $name, $idAthlete, $start, $year, $month, $day, $distance, $time, $pace, $elevation, $calories, $kudos, $comments) = @_;

	# escape data
	$name = escapeForSQL($name);

	# insert activity if not found
	our $dbh;
	my $sql = "INSERT INTO activities (id, name, athlete_id, start, year, month, week, day, distance, time, pace, elevation, calories, kudos, comments)
		VALUES ($id, '$name', $idAthlete, '$start', $year, $month, 100, $day, $distance, $time, $pace, '$elevation', '$calories', $kudos, $comments);";

	$dbh->do($sql);
}

sub getTimestamp {
	my ($timeonly) = @_;

	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime(time);
	my $timestamp = "";
	if ($timeonly) {
		$timestamp = sprintf("%02d:%02d:%02d", $hour, $min, $sec);
	}
	else {
		$year += 1900;
		$mday = sprintf("%02d", $mday);
		$mon = sprintf("%02d", $mon + 1);
		$timestamp = $year.".".$mon.".".$mday;
	}
	return $timestamp;
}

sub getCurYearWeek {
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $curYear = 1900 + $year;
	my $curWeek = ceil($yday / 7);
	return ($curYear, $curWeek);
}

sub getCurYearMonth {
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my $curYear = 1900 + $year;
	my $curMonth = 1 + $mon;
	return ($curYear, $curMonth);
}

sub insertTask {
	my ($year, $week, $idAthlete) = @_;

	# delete task
	our $dbh;
	my $sql = "DELETE FROM tasks WHERE year=$year AND week=$week AND athlete_id=$idAthlete;";
	$dbh->do($sql);

	# insert a new task
	my $timestamp = getTimestamp(0);
	$sql = "INSERT INTO tasks (year, week, athlete_id, timestamp)
		VALUES ($year, $week, $idAthlete, '$timestamp');";
	$dbh->do($sql);
}

sub checkTask {
	my ($year, $week, $idAthlete) = @_;

	our $dbh;
	my $sql = "SELECT * FROM tasks WHERE year=$year AND week=$week AND athlete_id=$idAthlete";
	my $sth = $dbh->prepare($sql);
	my $found = 0;
	if ($sth) {
		if ($sth->execute()) {
			if(my @row = $sth->fetchrow_array) {
				return 1;
			}
		}
		$sth->finish();
	}

	return 0;
}

sub checkActivity{
	my ($idActivity, $kudos, $comments) = @_;

	my $sql = "SELECT * FROM activities WHERE id=$idActivity";
	my $res = checkExists($sql);

	if ($res) {
		my $sqlUpdate = "UPDATE activities SET kudos=$kudos, comments=$comments WHERE id=$idActivity";
		execSQL($sqlUpdate);
	}

	return $res;
}

sub checkAthlete{
	my ($idAthlete) = @_;

	my $sql = "SELECT * FROM athletes WHERE id=$idAthlete";
	return checkExists($sql);
}

sub checkExists {
	my ($sql) = @_;

	our $dbh;
	my $sth = $dbh->prepare($sql);
	if ($sth) {
		if ($sth->execute()) {
			if(my @row = $sth->fetchrow_array) {
				return 1;
			}
		}
		$sth->finish();
	}

	return 0;
}

sub clearTask {
	my ($year, $week, $idAthlete) = @_;

	# delete task
	our $dbh;
	my $sql = "DELETE FROM tasks WHERE year=$year AND week=$week AND athlete_id=$idAthlete;";
	$dbh->do($sql);
}

sub login {
	#Setup hidden browser
	my $jar = HTTP::CookieJar::LWP->new;
	our $mech = WWW::Mechanize->new(cookie_jar => $jar, strict_forms => 1, autocheck => 1);
	WWW::Mechanize::TreeBuilder->meta->apply($mech);

	$mech->get('https://www.strava.com/login');

	#Login
	my $response = $mech->submit_form(
		form_id => 'login_form',
		fields    => {
			email  => '<account email>',
			password  => '<account pass>'
		}
	);
	print "Login error: $response->status_line\n" unless $response->is_success;
	return $response->is_success;
}

sub parseAthleteId {
	my $strava = shift;
	my ($tmp1, $tmp2, $id) = split '/', $strava;

	$id =~ s/^\s+//;

	return $id;
}

sub parseActivityId {
	my $stravaActivity = shift;
	my ($tmp, $id) = split '-', $stravaActivity;

	$id =~ s/^\s+//;

	return $id;
}

sub parseActivityKudos {
	my $div = shift;

	my $kudos = $div->look_down(_tag => 'span', class => 'count count-kudos');
	return ($kudos ? $kudos->as_trimmed_text : '0');
}

sub parseActivityComments {
	my $div = shift;

	my $comments = $div->look_down(_tag => 'span', class => 'count count-comments');
	return ($comments ? $comments->as_trimmed_text : '0');
}

sub parseDate {
	my $date = shift;

	my @months = qw(January February March April May June July August September October November December);
	my $nextisday = 0;
	my $month = -1;
	my $day = -1;
	my @arsplit = split ' ', $date;
	for my $curdata(@arsplit) {
		if ($nextisday) {
			$nextisday = 0;
			my ($daystr) = split ',', $curdata;
			$day = int($daystr);
		}
		else {
			for (0..11) {
				if ($curdata eq $months[$_]) {
					$month = $_ + 1;
					$nextisday = 1;
				}
			}
		}
	}

	return ($arsplit[-1], $month, $day);
}

sub parseTimeName {
	my ($stravaTimeName, $year) = @_;
	my ($tmp, $stravatime) = split '  ', $stravaTimeName;

	$stravatime =~ s/^\s+//;

	my ($readyear, $month, $day) = parseDate($stravatime);
	if ($month eq -1 or $day eq -1) {
	  if (index($stravatime, "Yesterday") >= 0) {
			($readyear, $month, $day) = parseDate(UnixDate("yesterday", "%B %e, %Y"));
	  }
	  elsif(index($stravatime, "Today") >= 0) {
			($readyear, $month, $day) = parseDate(UnixDate("today", "%B %e, %Y"));
	  }
	}
	$readyear = $year if ($readyear < 2010 || $readyear < 2020);

	my $dateLocal = new Date::Manip::Date;
	return ($stravatime, $month, $day) if $dateLocal->parse($stravatime);

	return ($dateLocal->printf("%s"), $readyear, $month, $day);
}

sub parseDistance {
	my $stravaDist = shift;
	my ($dist) = split 'km', $stravaDist;

	return $dist;
}

sub parsePace {
	my $stravaPace = shift;

	my $res = 0;
	my ($stravaPaceSpl) = split '/km', $stravaPace;

	my @arTime = split ':', $stravaPaceSpl;
	if (scalar @arTime == 2) {
		$res = $arTime[0] * 60 + $arTime[1];
	}
	else {
		$res = $arTime[0];
		$res = substr($res, 0, -1) if (substr($res, -1, 1) eq 's');
	}

	return $res;
}

sub parseTime {
	my $stravaTime = shift;

	my $res = 0;
	my ($stravaTimeSpl) = split ' ', $stravaTime;
	my @arTime = split ':', $stravaTimeSpl;
	if (scalar @arTime == 3) {
		$res = $arTime[0] * 3600 + $arTime[1] * 60 + $arTime[2];
	}
	elsif (scalar @arTime == 2) {
		$res = $arTime[0] * 60 + $arTime[1];
	}
	else {
		$res = $arTime[0];
		$res = substr($res, 0, -1) if (substr($res, -1, 1) eq 's');
	}

	return $res;
}

sub readActivity {
	my ($activityId, $year, $ath) = @_;

	my $request = "https://www.strava.com/activities/$activityId";
	print "$request";

	our $mech;

	my $response = eval { $mech->get($request); };
	while (not defined $response or not $response->is_success) {
		# wait for 1 hour and 5 minutes and try again
		my $time = getTimestamp(1);
		print "\nRead error, waiting for one hour before trying one more time ($time)\n";
		sleep 65 * 60;
		$response = eval { $mech->get($request); };
	}
	print " ... ok\n";

	try {
		my @names = $mech->look_down(_tag => 'h1');
		my $name = $names[-1]->as_trimmed_text;
		my $idAthlete = parseAthleteId($mech->look_down(_tag => 'span', class => 'title')->look_down(_tag => 'a')->attr('href'));
		my ($start, $readyear, $month, $day) = parseTimeName($mech->look_down(_tag => 'div', class => 'details')->as_text, $year);
		my @distancetimepace = $mech->look_down(_tag => 'ul', class => 'inline-stats section')->look_down(_tag => 'li');
		my $distance = parseDistance($distancetimepace[0]->as_trimmed_text);
		my $time = parseTime($distancetimepace[1]->look_down(_tag => 'strong')->as_trimmed_text);
		my $pace = parsePace($distancetimepace[2]->as_trimmed_text);
		my $additionalStatsRoot = $mech->look_down(_tag => 'div', class => 'section more-stats');
		my $elevation = 0;
		my $calories = 0;
		if (defined $additionalStatsRoot) {
			my @additionalStats = $additionalStatsRoot->look_down(_tag => 'div');
			my $nextelev = 0;
			my $nextcalor = 0;
			for (@additionalStats) {
				my $text = $_->as_trimmed_text;
				if ($text eq 'Elevation') {
					$nextelev = 1;
				}
				elsif ($text eq 'Calories') {
					$nextcalor = 1;
				}
				else {
					if ($nextelev) {
						$elevation = $text;
						$elevation =~ s/m//g;
						$elevation =~ s/,//g;
					}
					elsif ($nextcalor) {
						$calories = $text;
						$calories =~ s/,//g;
					}

					$nextelev = 0;
					$nextcalor = 0;
				}
			}
		}
		my $kudos = $mech->look_down(_tag => 'div', id => 'kudos')->as_trimmed_text;
		my $comments = $mech->look_down(_tag => 'a', id => 'comments')->as_trimmed_text;

		insertActivity($activityId, $name, $idAthlete, $start, $readyear, $month, $day, $distance, $time, $pace, $elevation, $calories, $kudos, $comments);
		print "     $year.$month.$day | dist: $distance | time: $time | pace: $pace | elev: $elevation | cal: $calories | kudos: $kudos | cmnt: $comments | $name\n";
	}
	catch {
		insertActivity($activityId, "ERROR", $ath, "", 0, 0, 0, 0, 0, 0, "", "", 0, 0);
		print "Error reading activity $activityId: $_\n";
	};
}

sub parseDivs {
	my $divs = shift;
	my @res = ();
	for my $div (@$divs) {
		my @types = $div->look_down(_tag => 'span', class => 'app-icon icon-run icon-dark icon-lg');
		if (@types) {
			my $id = parseActivityId($div->attr('id'));
			my $kudos = parseActivityKudos($div);
			my $comments = parseActivityComments($div);
			push @res, [$id, $kudos, $comments];
		}
	}

	return @res;
}

sub parseGroupDivs {
	my $athleteId = shift;
	$athleteId = "/athletes/".$athleteId;
	my $divs = shift;
	my @res = ();
	for my $grdiv (@$divs) {
		my @elems = $grdiv->look_down(_tag => 'li', class => 'entity-details feed-entry');
		for my $div (@elems) {
			my $athleteCur = $div->look_down(_tag => 'a')->attr('href');
			if ($athleteId eq $athleteCur) {
				my @types = $div->look_down(_tag => 'span', class => 'app-icon icon-run icon-dark icon-md');
				if (@types) {
					my $id = parseActivityId($div->attr('id'));
					my $kudos = parseActivityKudos($div);
					my $comments = parseActivityComments($div);
					push @res, [$id, $kudos, $comments];
				}
			}
		}
	}

	return @res;
}

sub updatePRRegStr {
	my ($content, $type_src, $type_db) = @_;

	my $src_str = '<td>' . $type_src . '<\/td>\s*<td>\s*<a href="\/activities\/\d*#\d*">\s*(\S*)?\s*<\/a>\s*<\/td>';
	my ($res) = $content =~ /$src_str/;
	if ($res) {
		return parseTime($res);
	}
	return 0;
}

sub updateDstAllRegStr {
	my ($content, $type_src) = @_;

	my $src_str = '<th>All-Time<\/th>\s*<th class=\'viewing\'><\/th>\s*<th class=\'viewer\'><\/th>\s*<\/tr>\s*<tr>\s*<td>Distance<\/td>\s*<td>(\S*)? km<\/td>\s*<td>0 km<\/td>\s*<\/tr>\s*<tr>\s*<td>Runs<\/td>';
	my ($res) = $content =~ /$src_str/;
	if ($res) {
		$res = ($res =~ s/,//r);
		return $res;
	}
	return 0;
}

sub updateDst2020RegStr {
	my ($content, $type_src) = @_;

	my $src_str = '<li class=\'clickable\' data-value=\'2020\'>2020<\/li>\s*<li class=\'clickable\' data-value=\'2019\'>2019<\/li>\s*<\/ul>\s*<\/div>\s*<\/th>\s*<th class=\'viewing\'><\/th>\s*<th class=\'viewer\'><\/th>\s*<\/tr>\s*<tbody id=\'running-ytd\'>\s*<tr>\s*<td>Distance<\/td>\s*<td>(\S*)? km<\/td>\s*<td>0 km<\/td>';
	my ($res) = $content =~ /$src_str/;
	if ($res) {
		$res = ($res =~ s/,//r);
		return $res;
	}
	return 0;
}

sub updateAthletePBs {
	my ($athleteId) = @_;

	my $request = "https://www.strava.com/athletes/$athleteId/profile_sidebar_comparison?hl=en-US";
	print "$request";
	our $mech;
	$mech->add_header('X-Requested-With' => 'XMLHttpRequest');

	my $response = eval { $mech->get($request); };
	while (not defined $response or not $response->is_success) {
		# wait for 5 minutes and try again
		my $time = getTimestamp(1);
		print "\nRead error, waiting for 5 minutes before trying one more time ($time)\n";
		sleep 5 * 60;
		$response = eval { $mech->get($request); };
	}
	print " ... ok: ";

	my $epb_1km = updatePRRegStr($mech->content, '1k', 'epb_1km');
	my $epb_1ml = updatePRRegStr($mech->content, '1 mile', 'epb_1ml');
	my $epb_5km = updatePRRegStr($mech->content, '5k', 'epb_5km');
	my $epb_10km = updatePRRegStr($mech->content, '10k', 'epb_10km');
	my $epb_hm = updatePRRegStr($mech->content, 'Half-Marathon', 'epb_hm');
	my $epb_m = updatePRRegStr($mech->content, 'Marathon', 'epb_m');
	my $distance_all = updateDstAllRegStr($mech->content, 'Distance');
	my $distance_2020 = updateDst2020RegStr($mech->content, 'Distance');

	updateAthlete($athleteId, $epb_1km, $epb_1ml, $epb_5km, $epb_10km, $epb_hm, $epb_m, $distance_all, $distance_2020);
}

sub updateAthleteStats {
	my ($athleteId) = @_;

	my $request = "https://www.strava.com/athletes/$athleteId/profile_sidebar_comparison?hl=en-US";
	print "$request";
	our $mech;
	$mech->add_header('X-Requested-With' => 'XMLHttpRequest');

	my $response = eval { $mech->get($request); };
	while (not defined $response or not $response->is_success) {
		# wait for 5 minutes and try again
		my $time = getTimestamp(1);
		print "\nRead error, waiting for 5 minutes before trying one more time ($time)\n";
		sleep 5 * 60;
		$response = eval { $mech->get($request); };
	}
	print " ... ok: ";

	my $epb_1km = updatePRRegStr($mech->content, '1k', 'epb_1km');
	my $epb_1ml = updatePRRegStr($mech->content, '1 mile', 'epb_1ml');
	my $epb_5km = updatePRRegStr($mech->content, '5k', 'epb_5km');
	my $epb_10km = updatePRRegStr($mech->content, '10k', 'epb_10km');
	my $epb_hm = updatePRRegStr($mech->content, 'Half-Marathon', 'epb_hm');
	my $epb_m = updatePRRegStr($mech->content, 'Marathon', 'epb_m');
	my $distance_all = updateDstAllRegStr($mech->content, 'Distance');
	my $distance_2020 = updateDst2020RegStr($mech->content, 'Distance');

	insertAthleteStats($athleteId, $distance_all, $distance_2020);
}

sub testRead {
	my ($date) = @_;

	my $request = "https://kurs.com.ua/?app=kurs&module=archive&controller=ajax&do=board&currencies=1%2F491&date=" . $date;
	#print "$request";

	our $mech;
	$mech->add_header('X-Requested-With' => 'XMLHttpRequest');

	my $response = eval { $mech->get($request); };
	while (not defined $response or not $response->is_success) {
		# wait for 5 minutes and try again
		my $time = getTimestamp(1);
		print "\nRead error, waiting for 5 minutes before trying one more time ($time)\n";
		sleep 5 * 60;
		$response = eval { $mech->get($request); };
	}
	my $content = $mech->content;
	$content =~ tr/'/!/;
	my ($res) = $content =~ /data-rate-type=!retail! data-rate=!(.*)! data-ipsKursTextFill/;
	#return $res;
#	my $epb_1km = updatePRRegStr($mech->content, '1k', 'epb_1km');
#	my $epb_1ml = updatePRRegStr($mech->content, '1 mile', 'epb_1ml');
#	my $epb_5km = updatePRRegStr($mech->content, '5k', 'epb_5km');
#	my $epb_10km = updatePRRegStr($mech->content, '10k', 'epb_10km');
#	my $epb_hm = updatePRRegStr($mech->content, 'Half-Marathon', 'epb_hm');
#	my $epb_m = updatePRRegStr($mech->content, 'Marathon', 'epb_m');

#	updateAthlete($athleteId, $epb_1km, $epb_1ml, $epb_5km, $epb_10km, $epb_hm, $epb_m);
}

sub readAthletePage {
	my ($athleteId, $year, $month) = @_;
	$month = sprintf("%02d", $month);

	my $request = "https://www.strava.com/athletes/$athleteId?interval=$year$month&interval_type=month&chart_type=miles&year_offset=0";
	print "$request";

	our $mech;
	my $response = eval { $mech->get($request); };
	while (not defined $response or not $response->is_success) {
		# wait for 5 minutes and try again
		my $time = getTimestamp(1);
		print "\nRead error, waiting for 5 minutes before trying one more time ($time)\n";
		sleep 5 * 60;
		$response = eval { $mech->get($request); };
	}
	print " ... ok: ";

	my $cntActivities = 0;

	my @divsSingle1 = $mech->look_down(_tag => 'div', class => 'activity entity-details feed-entry');
	my @res1 = parseDivs(\@divsSingle1);
	my @divsSingle2 = $mech->look_down(_tag => 'div', class => 'activity entity-details feed-entry min-view');
	my @res2 = parseDivs(\@divsSingle2);
	my @divsGroup = $mech->look_down(_tag => 'div', class => 'feed-entry group-activity');
	my @res3 = parseGroupDivs($athleteId, \@divsGroup);

	my @res;
	push @res, @res1, @res2, @res3;
	print scalar @res, "\n";

	return @res;
}

sub readAthletePages {
	my ($athleteId) = @_;

	my $request = "https://www.strava.com/athletes/$athleteId";
	print "$request";

	our $mech;
	my $response = $mech->get($request);
	die "Read error: $response->status_line\n" unless $response->is_success;
	print " ... ok\n";

	my $cntActivities = 0;

	my @intervals = $mech->look_down(_tag => 'ul', class => 'intervals')->look_down(_tag => 'li');
	print scalar @intervals;
	#for $interval(@intervals) {

	#}
}

sub readAthletes {
	my ($groupId, $page) = @_;

	my $request = "https://www.strava.com/clubs/$groupId/members?page=$page";
	print "$request";

	our $mech;
	my $response = $mech->get($request);
	die "Read error: $response->status_line\n" unless $response->is_success;
	print " ... ok\n";

	my @divs = $mech->look_down(_tag => 'div', class => 'text-headline');
	my @imgs = $mech->look_down(_tag => 'img', class => 'avatar-img');

	print scalar @divs, " ", scalar @imgs, "\n";

	my $cntAthletes = 0;
	for my $div (@divs) {
		my @links = $div->look_down(_tag => 'a');
		if (@links) {
			my $nameAthlete = $links[0]->as_trimmed_text;
			my $linkAthlete = $links[0]->attr('href');
			my @spl = split("/", $linkAthlete);
			my $idAthlete = $spl[2];

			insertAthlete($idAthlete, $nameAthlete);
			$cntAthletes ++;
		}
	}

	return $cntAthletes;
}

sub readAllAthletes {
	my ($groupId) = @_;

	my $page = 1;
	while (StravaParser::readAthletes($groupId, $page) > 2) {
		$page++;
	}
}

1;
