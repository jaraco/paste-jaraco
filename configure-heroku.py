from __future__ import print_function

import sys
import pprint

try:
	import urllib.parse as urllib_parse
except ImportError:
	import urlparse as urllib_parse

import requests
import keyring.http

def url(subpath):
	return urllib_parse.urljoin('https://api.heroku.com/apps/paste-jaraco/',
		subpath)

def parse_auth_realm(resp):
	"""
	From a 401 response, parse out the realm for basic auth.
	"""
	header = resp.headers['www-authenticate']
	mode, _sep, dict = header.partition(' ')
	assert mode.lower() == 'basic'
	return requests.utils.parse_dict_header(dict)['realm']

def get_auth(username, realm):
	return username, keyring.get_password(realm, username)

def request(*args, **kwargs):
	"""
	Use requests on a resource, but retry with auth
	"""
	resp = requests.request(*args, **kwargs)
	if resp.status_code == 401:
		realm = parse_auth_realm(resp)
		kwargs['auth'] = get_auth('jaraco', realm)
		resp = requests.request(*args, **kwargs)
	return resp

def add_MongoHQ():
	headers = {
		'Accept': 'application/json',
	}
	resp = request(method='POST', url=url('addons/mongohq'), headers=headers)
	resp.raise_for_status()
	pprint.pprint(resp.json())

def add_hostname():
	headers = {
		'Accept': 'application/json',
	}
	data = 'domain_name[domain]=paste.jaraco.com'

	resp = request(url=url('domains'), headers=headers, data=data,
		method='POST')
	result = resp.json()
	if not resp.ok:
		handle_error(result)
		return
	pprint.pprint(result)

def handle_error(errors):
	if isinstance(errors, list):
		for error in errors:
			print(':'.join(error), file=sys.stderr)
	else:
		print(pprint.pformat(errors), file=sys.stderr)


if __name__ == '__main__':
	add_MongoHQ()
	add_hostname()
