import json
import os

class Storage(object):
	path = 'dtb'
	storage = {}

	def __init__(self):
		if os.path.exists(self.path):
			with open(self.path) as json_file:
				self.storage = json.load(json_file)

	def __del__(self):
		self.save()

	def getName(self, id):
		if ('names' in self.storage.keys()) and (id in self.storage['names'].keys()) and ('name' in self.storage['names'][id].keys()):
			return self.storage['names'][id]['name']

	def setName(self, id, name):
		if 'names' not in self.storage.keys():
			self.storage['names'] = {}
		if id not in self.storage['names'].keys():
			self.storage['names'][id] = {}
		self.storage['names'][id]['name'] = name

	def getMembers(self):
		if ('members' in self.storage.keys()):
			return self.storage['members']
		return []

	def save(self):
		with open(self.path, "w") as json_file:
			json.dump(self.storage, json_file, indent = 4)
