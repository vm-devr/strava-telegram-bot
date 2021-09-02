import requests
import json
import logging
import urllib3
import re
import Storage
from LeaderBoard import LeaderBoard

class Strava(LeaderBoard):
	session = requests.Session()
	group = '252700'
	user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'

	def __init__(self, storage):
		self.storage = storage

	def getLeaderboard(self, prevWeek, elements):
		print('Reading latest leaderboard')
		def provideName(ath):
			ath['name'] = self.getName(ath['id'])
			return ath

		if elements > 99:
			elements = 99
		members = self.storage.getMembers()
		raw_board = self.__getLeaderboard(self.group, prevWeek)
		filtered_board = list(filter(lambda ath: ath['id'] in members, raw_board))
		board = list(map(provideName, filtered_board[:elements]))

		return self.printable(board)


	def getName(self, id):
		idstr = str(id)
		name = self.storage.getName(idstr)
		if name is None:
			print('Reading name for ' + idstr)
			name = self.__getName(idstr)
			self.storage.setName(idstr, name)
		return name

	def __getLeaderboard(self, group, prevWeek):
		url_fmt = 'https://www.strava.com/clubs/{}/leaderboard{}'
		addition = '?week_offset=1' if prevWeek else ''
		url = url_fmt.format(group, addition)

		headers = {
			'User-Agent': self.user_agent,
			'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript',
			'X-Requested-With': 'XMLHttpRequest',
			'Referer': url
		}

		r = self.session.get(url, headers=headers)
		if r.status_code != 200:
			print('Error reading leaderboard for ' + group)
			return []

		data = json.loads(r.text)
		return list(sorted(map(lambda ath: {
			'id': ath['athlete_id'],
			'rank': ath['rank'],
			'distance': round(ath['distance'] / 1000)
		}, data['data']), key = lambda ath: ath['rank']))

	def __getName(self, id):
		url_fmt = 'https://www.strava.com/athletes/{}'
		url = url_fmt.format(id)

		headers = {
			'User-Agent': self.user_agent,
			'Referer': url
		}

		r = self.session.get(url, headers=headers)
		if r.status_code != 200:
			print('Error reading name for ' + id)
			return ''

		match = re.search(r'<title>Strava [A-Za-z]* Profile \| (.*)</title>', r.text)
		try:
			return match.group(1)
		except:
			print('Error parsing name for ' + id)
		return ""

	def enableLogging(self):
		try:
			import http.client as http_client
		except ImportError:
			# Python 2
			import httplib as http_client
		http_client.HTTPConnection.debuglevel = 1

		# You must initialize logging, otherwise you'll not see debug output.
		logging.basicConfig()
		logging.getLogger().setLevel(logging.DEBUG)
		requests_log = logging.getLogger("requests.packages.urllib3")
		requests_log.setLevel(logging.DEBUG)
		requests_log.propagate = True

