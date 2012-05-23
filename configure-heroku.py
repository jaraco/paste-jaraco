import urllib2
import json
import pprint

import keyring.http
import jaraco.net.http

class FixedUserKeyringPasswordManager(keyring.http.PasswordMgr):
	def __init__(self, username):
		self.username = username

	def get_username(self, realm, authuri):
		print 'realm is', realm
		print 'authuri is', authuri
		return self.username

	# provide clear_password until delete_password is officially
	#  implemented.
	def clear_password(self, realm, authuri):
		user = self.get_username(realm, authuri)
		# this call will only succeed on WinVault for now
		keyring.get_keyring().delete_password(realm, user)

def install_opener():
	auth_manager = FixedUserKeyringPasswordManager(username='')
	auth_handler = urllib2.HTTPBasicAuthHandler(auth_manager)
	# build a new opener
	opener = urllib2.build_opener(auth_handler)
	# install it
	urllib2.install_opener(opener)


def add_MongoHQ():
	headers = {
		'Accept': 'application/json',
	}
	req = jaraco.net.http.MethodRequest(
		url = 'https://api.heroku.com/apps/paste-jaraco/addons/mongohq',
		method = 'POST', headers=headers,
	)
	install_opener()
	res = urllib2.urlopen(req)
	assert res.code == 200
	pprint.pprint(json.loads(res.read()))

if __name__ == '__main__':
	add_MongoHQ()
