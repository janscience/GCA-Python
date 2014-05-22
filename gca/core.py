from __future__ import print_function

import json
import urllib2
import urllib
from cookielib import CookieJar
from urlparse import urlparse


class TransportError(Exception):
    def __init__(self, code, message):
        self.message = message
        self.code = code

    def __str__(self):
        return "[%d] %s" % (self.code, self.message)


class BaseObject(object):
    def __init__(self, data):
        self._data = data

    @property
    def uuid(self):
        return self._data['uuid']

    @property
    def raw_data(self):
        return self._data


class Affiliation(BaseObject):
    def __init__(self, data):
        super(Affiliation, self).__init__(data)

    def format_affiliation(self):
        department = self._data['department']
        section = self._data['section']
        address = self._data['address']
        country = self._data['country']

        components = [department, section, address, country]
        active = filter(bool, components)
        return u', '.join(active)


class Author(BaseObject):
    def __init__(self, data):
        super(Author, self).__init__(data)

    def format_name(self):
        d = self._data
        middle = d['middleName'] + u' ' if d['middleName'] else u""
        return d['firstName'] + u' ' + middle + d['lastName']

    def format_affiliation(self):
        af = self._data['affiliations']
        af_corrected = [str(x + 1) for x in sorted(af)]
        return ', '.join(af_corrected)


class Reference(BaseObject):
    def __init__(self, data):
        super(Reference, self).__init__(data)

    @property
    def text(self):
        return self._data['text']


class Abstract(BaseObject):
    def __init__(self, data):
        super(Abstract, self).__init__(data)
        self.__data = data

    @property
    def title(self):
        return self.__data['title']

    @property
    def text(self):
        return self.__data['text']

    @text.setter
    def text(self, value):
        self.__data['text'] = value

    @property
    def state(self):
        return self.__data['state']

    @property
    def authors(self):
        return [Author(a) for a in self.__data['authors']]

    @property
    def affiliations(self):
        return [Affiliation(a) for a in self.__data['affiliations']]

    @property
    def acknowledgements(self):
        return self.__data['acknowledgements']

    @property
    def references(self):
        return [Reference(r) for r in self.__data['references']]

    @property
    def topic(self):
        return self.__data['topic']


def authenticated(method):
    def wrapper(self, *args, **kwargs):
        if not self.is_authenticated:
            self.authenticate()
        return method(self, *args, **kwargs)
    return wrapper


class Session(object):
    def __init__(self, url, authenticator):
        jar = CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))

        self.__url = url
        self.__cookie_jar = jar
        self.__url_opener = opener
        self.__auth = authenticator
        self.__is_authenticated = False

    @property
    def url(self):
        return self.__url

    @property
    def is_authenticated(self):
        return self.__is_authenticated

    def authenticate(self):
        purl = urlparse(self.url)
        hostname = purl.hostname
        user, password = self.__auth.get_credentials(hostname)
        params = urllib.urlencode({'username': user, 'password': password})
        url_opener = self.__url_opener
        resp = url_opener.open(self.url + "/authenticate/userpass", params)
        code = resp.getcode()
        if code != 200:
            raise TransportError(code, "Could not log in")
        self.__is_authenticated = True
        return code

    @authenticated
    def get_all_abstracts(self, conference, raw=False):
        url = "%s/api/conferences/%s/allAbstracts" % (self.url, conference)
        data = self._fetch(url)
        return [Abstract(abstract) for abstract in data] if not raw else data

    def get_conference(self, conference):
        url = "%s/api/conferences/%s" % (self.url, conference)
        data = self._fetch(url)
        return data

    def _fetch(self, url):
        url_opener = self.__url_opener
        resp = url_opener.open(url)
        if resp.getcode() != 200:
            raise TransportError(resp.getcode(), "Could not fetch data")
        data = resp.read()
        text = data.decode('utf-8')
        return json.loads(text)