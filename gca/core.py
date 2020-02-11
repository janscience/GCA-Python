from __future__ import print_function

from .util import getattr_maybelist

import json
import urllib.request as request
import urllib
from http.cookiejar import CookieJar
from urllib import parse
from collections import defaultdict
import os
import sys
from .util import make_fields
import uuid
from six import string_types
import functools


class TransportError(Exception):
    def __init__(self, code, message):
        self.message = message
        self.code = code

    def __str__(self):
        return "[%d] %s" % (self.code, self.message)


class BaseObject(object):
    def __init__(self, data):
        def none_factory():
            return None
        self._data = data if data is not None else defaultdict(none_factory)

    @property
    def raw_data(self):
        return self._data


class Entity(BaseObject):
    def __init__(self, data):
        super(Entity, self).__init__(data)

    @property
    def uuid(self):
        return self._data['uuid']

    @uuid.setter
    def uuid(self, value):
        if 'uuid' in self._data:
            print("[W] overriding UUID", file=sys.stderr)
        if type(value) == uuid.UUID:
            value = str(value)
        self._data['uuid'] = value


class Group(Entity):
    def __init__(self, data=None):
        super(Group, self).__init__(data)

    @property
    def name(self):
        return self._data['name']

    @property
    def prefix(self):
        return self._data['prefix']

    @property
    def brief(self):
        return self._data['short']


class Conference(Entity):
    def __init__(self, data=None):
        super(Conference, self).__init__(data)

    @property
    def name(self):
        return self._data['name']

    @property
    def brief(self):
        return self._data['short']

    @property
    def topics(self):
        return self._data['topics']

    @property
    def is_open(self):
        return self._data['isOpen']

    @property
    def is_published(self):
        return self._data['isPublished']

    def sort_id_to_string(self, sort_id):
        gid = sort_id >> 16
        aid = sort_id & 0x0000FFFF
        groups = [Group(gd) for gd in self._data['groups']]
        group = list(filter(lambda x: x.prefix == gid, groups))[0]
        return "%s %d" % (group.brief, aid)

    def get_group(self, sort_id):
        gid = sort_id >> 16
        groups = [Group(gd) for gd in self._data['groups']]
        group = list(filter(lambda x: x.prefix == gid, groups))[0]
        return group

    def group_for_brief(self, brief):
        groups = [Group(gd) for gd in self._data['groups']]
        selected = list(filter(lambda x: x.brief == brief, groups))
        if len(selected) != 1:
            raise ValueError('Error finding group with brief [%s: %d]' % (brief, len(selected)))
        return selected[0]

    @staticmethod
    def parse_sortid_string(sid):
        for i, x in enumerate(sid):
            if x.isdigit():
                prefix, num = sid[:i], int(sid[i:])
                assert(prefix.isalpha())
                assert(int(num) > -1)
                return prefix, num
        raise ValueError('Invalid sid')

    @staticmethod
    def from_data(data):
        js = json.loads(data)
        return Conference(js)


class Affiliation(Entity):
    def __init__(self, data=None):
        super(Affiliation, self).__init__(data)

    @property
    def department(self):
        return self._data['department']

    @department.setter
    def department(self, value):
        self._data['department'] = value

    @property
    def section(self):
        return self._data['section']

    @section.setter
    def section(self, value):
        self._data['section'] = value

    @property
    def address(self):
        return self._data['address']

    @address.setter
    def address(self, value):
        self._data['address'] = value

    @property
    def country(self):
        return self._data['country']

    @country.setter
    def country(self, value):
        self._data['country'] = value

    def format_affiliation(self):
        department = self._data['department']
        section = self._data['section']
        address = self._data['address']
        country = self._data['country']

        components = [department, section, address, country]
        active = filter(bool, components)
        return u', '.join(active)

    def latex_format_affiliation(self):
        department = self._data['department']
        section = self._data['section']
        address = self._data['address']
        country = self._data['country']
        components = [u', ' + c if c and len(c) else u'' for c in [department, section, address, country]]
        return u'\\affiliation{' + '}{'.join(components) + '}'


class Author(Entity):
    def __init__(self, data=None):
        super(Author, self).__init__(data)

    @property
    def first_name(self):
        return self._data['firstName']

    @first_name.setter
    def first_name(self, value):
        self._data['firstName'] = value

    @property
    def middle_name(self):
        return self._data['middleName']

    @middle_name.setter
    def middle_name(self, value):
        self._data['middleName'] = value

    @property
    def last_name(self):
        return self._data['lastName']

    @last_name.setter
    def last_name(self, value):
        self._data['lastName'] = value

    @property
    def affiliations(self):
        return self._data['affiliations']

    @affiliations.setter
    def affiliations(self, value):
        self._data['affiliations'] = value

    @property
    def full_name(self):
        return self.format_name()

    def format_name(self, inverted=False):
        d = self._data

        first = self.sanitize_name(d['firstName'])

        if inverted:
            middle = self.format_initials(d['middleName'], suffix='.')
            if middle and len(middle):
                middle = u' ' + middle
            return "%s, %s%s" % (d['lastName'], first, middle)

        middle = self.sanitize_name(d['middleName'])
        middle = middle + u' ' if middle else u''
        return first + u' ' + middle + d['lastName']

    def latex_format_name(self):
        d = self._data
        first = ''
        shortfirst = ''
        if d['firstName'] and len(d['firstName']):
            first = self.sanitize_name(d['firstName'], separator=' ', suffix='.')
            shortfirst = self.format_initials(d['firstName'],
                                              separator=' ', suffix='.')
        middle = ''
        shortmiddle = ''
        if d['middleName'] and len(d['middleName']):
            middle = u' ' + self.sanitize_name(d['middleName'], separator=' ',
                                                      suffix='.')
            shortmiddle = u' ' + self.format_initials(d['middleName'],
                                                      separator=' ',
                                                      suffix='.')
        return u"\\authorname{%s}{%s}{%s}{%s}{%s}" % (first, middle, shortfirst, shortmiddle, d['lastName'].strip())

    def format_affiliation(self):
        af = self._data['affiliations']
        af_corrected = [str(x + 1) for x in sorted(af)]
        return ', '.join(af_corrected)

    @property
    def index_name(self):
        return "%s %s%s" % (self.last_name,
                            self.format_initials(self.first_name),
                            self.format_initials(self.middle_name))

    @staticmethod
    def sanitize_name(name, separator='', suffix=''):
        """ Apply to first and middle name to separate initials.
        E.g. 'MS' -> 'M. S.'
        E.g. 'M' -> 'M.'
        """
        if not name:
            return ""
        # make sure name is split after every '.' and around '-':
        name = name.strip().replace('.', '. ')
        name = name.replace('-', ' - ')
        # split into components and also split double and triple initials (e.g. 'HJ'):
        comps = [y for x in name.split() for y in (x if len(x)<=3 and x.isupper() and x.isalpha() else [x] )]
        text = separator.join([a if len(a) > 1 else a[0] + suffix if a[0] != '-' else a[0] for a in comps])
        if separator:
            return text.replace(separator+'-'+separator, '-')
        else:
            return text

    @staticmethod
    def format_initials(name, separator='', suffix=''):
        if not name:
            return ""
        # make sure name is split after every '.' and around '-':
        name = name.strip().replace('.', '. ')
        name = name.replace('-', ' - ')
        # split into components and also split double and triple initials (e.g. 'HJ'):
        comps = [y for x in name.split() for y in (x if len(x)<=3 and x.isupper() and x.isalpha() else [x] )]
        text = separator.join([a[0] + suffix if a[0] != '-' else a[0] for a in comps])
        if separator:
            return text.replace(separator+'-'+separator, '-')
        else:
            return text


class Reference(Entity):
    def __init__(self, data=None):
        super(Reference, self).__init__(data)

    @property
    def text(self):
        return self._data['text']

    @text.setter
    def text(self, value):
        self._data['text'] = value

    @property
    def link(self):
        return self._data['link']

    @link.setter
    def link(self, value):
        self._data['link'] = value

    @property
    def doi(self):
        return self._data['doi']

    @doi.setter
    def doi(self, value):
        self._data['doi'] = value

    @property
    def doi_link(self):
        doi = self.doi
        return doi if doi.startswith('http') else "http://dx.doi.org/%s" % doi

    @property
    def url(self):
        return self.link or self.doi_link

    @property
    def display_text(self):
        return self.text or self.link


class Figure(Entity):
    def __init__(self, data=None):
        super(Figure, self).__init__(data)

    @property
    def caption(self):
        return self._data['caption']


class AbstractType(Entity):
    def __init__(self, data=None, conference=None):
        super(AbstractType, self).__init__(data)
        self.conference = conference

    @property
    def name(self):
        return self._data['name']

    @name.setter
    def name(self, value):
        self._data['name'] = value

    @property
    def short(self):
        return self._data['short']

    @short.setter
    def short(self, value):
        self._data['short'] = value

    @property
    def prefix(self):
        return self._data['prefix']

    @prefix.setter
    def prefix(self, value):
        self._data['prefix'] = value


class Abstract(Entity):
    def __init__(self, data=None, conference=None):
        super(Abstract, self).__init__(data)
        self.conference = conference

    @property
    def title(self):
        return self._data['title']

    @title.setter
    def title(self, value):
        self._data['title'] = value

    @property
    def text(self):
        return self._data['text']

    @text.setter
    def text(self, value):
        self._data['text'] = value

    @property
    def state(self):
        return self._data['state']

    @state.setter
    def state(self, value):
        self._data['state'] = value

    @property
    def authors(self):
        return [Author(a) for a in self._data['authors']]

    @authors.setter
    def authors(self, value):
        self._data['authors'] = [a.raw_data for a in value]

    @property
    def affiliations(self):
        return [Affiliation(a) for a in self._data['affiliations']]

    @affiliations.setter
    def affiliations(self, value):
        self._data['affiliations'] = [a.raw_data for a in value]

    @property
    def acknowledgements(self):
        return self._data['acknowledgements']

    @acknowledgements.setter
    def acknowledgements(self, value):
        self._data['acknowledgements'] = value

    @property
    def references(self):
        if 'references' not in self._data:
            return []
        return [Reference(r) for r in self._data['references']]

    @references.setter
    def references(self, value):
        self._data['references'] = [r.raw_data for r in value]

    @property
    def figures(self):
        if 'figures' not in self._data:
            return []
        return [Figure(f) for f in self._data['figures']]

    @property
    def log(self):
        if 'stateLog' not in self._data:
            return []
        log_data = self._data['stateLog']
        if type(log_data) != list:
            return None
        return [LogEntry(e) for e in log_data]

    @property
    def owners(self):
        if 'owners' not in self._data:
            return []
        owner_data = self._data['owners']
        if type(owner_data) != list:
            return None
        return [Owner(o) for o in owner_data]

    @property
    def topic(self):
        return self._data['topic']

    @topic.setter
    def topic(self, value):
        self._data['topic'] = value

    @property
    def abstypes(self):
        if 'abstrTypes' not in self._data:
            return []
        return [AbstractType(t) for t in self._data['abstrTypes']]

    @property
    def is_talk(self):
        return self._data['isTalk']

    @property
    def reason_for_talk(self):
        return self._data['reasonForTalk']

    @property
    def sort_id(self):
        if 'sortId' not in self._data:
            return 0
        return self._data['sortId']

    @sort_id.setter
    def sort_id(self, value):
        self._data['sortId'] = value

    @property
    def alt_id(self):
        return self._data['altId'] if 'altId' in self._data else 0

    @alt_id.setter
    def alt_id(self, value):
        self._data['altId'] = value

    @property
    def doi(self):
        return self._data['doi']

    @doi.setter
    def doi(self, value):
        self._data['doi'] = value

    @property
    def poster_id(self):
        sid = self.sort_id
        if self.conference is not None:
            return self.conference.sort_id_to_string(sid)
        return str(sid)

    @poster_id.setter
    def poster_id(self, value):
        if self.conference is None:
            raise ValueError('Need conference!')
        brief, num = self.conference.parse_sortid_string(value)
        group = self.conference.group_for_brief(brief)
        sortId = group.prefix << 16
        self._data['sortId'] = sortId + num

    def select_field(self, field, fold=False):
        if isinstance(field, string_types):
            field = make_fields(field)
        val = functools.reduce(getattr_maybelist, field, self)

        if fold:
            if len(val) == 0:
                return None
            if len(val) == 1:
                return val[0]

        return val

    @classmethod
    def from_data(cls, data, conference=None):
        js = json.loads(data)
        return [Abstract(a, conference) for a in js]

    def to_data(self):
        return self._data

    @staticmethod
    def to_json(abstracts):
        js = Session.to_json([a.to_data() for a in abstracts])
        return js


class Owner(Entity):
    def __init__(self, data):
        super(Owner, self).__init__(data)

    @property
    def email(self):
        return self._data['mail']


class LogEntry(object):
    def __init__(self, data):
        self._data = data

    @property
    def timestamp_str(self):
        return self._data['timestamp']

    @property
    def timestamp(self):
        import isodate
        return isodate.parse_datetime(self._data['timestamp'])

    @property
    def state(self):
        return self._data['state']

    @property
    def editor(self):
        return self._data['editor']

    @property
    def note(self):
        return self._data['note']


def authenticated(method):
    def wrapper(self, *args, **kwargs):
        if not self.is_authenticated:
            self.authenticate()
        return method(self, *args, **kwargs)
    return wrapper


class Session(object):
    def __init__(self, url, authenticator):
        jar = CookieJar()
        opener = request.build_opener(request.HTTPCookieProcessor(jar))

        self.__url = url
        self.__cookie_jar = jar
        self.__url_opener = opener
        self.__auth = authenticator
        self.__is_authenticated = False
        self._guess_mime_ext = None

    @property
    def url(self):
        return self.__url

    @property
    def is_authenticated(self):
        return self.__is_authenticated

    def authenticate(self):
        purl = parse.urlparse(self.url)
        hostname = purl.hostname
        user, password = self.__auth.get_credentials(hostname)
        params = urllib.parse.urlencode({'identifier': user, 'password': password})
        url_opener = self.__url_opener
        resp = url_opener.open(self.url + "/authenticate/credentials", params.encode("utf-8"))
        code = resp.getcode()
        if code != 200:
            raise TransportError(code, "Could not log in")
        self.__is_authenticated = True
        return code

    @authenticated
    def get_all_abstracts(self, conference, raw=False, full=False, public=False):
        endpoint = "abstracts" if public else "allAbstracts"
        url = "%s/api/conferences/%s/%s" % (self.url, conference, endpoint)
        data = self._fetch(url)

        if full:
            data = [self._complete_abstract(a) for a in data]

        all_abstracts = [Abstract(abstract) for abstract in data] if not raw else data
        return all_abstracts

    def get_conference(self, conference, raw=False):
        url = "%s/api/conferences/%s" % (self.url, conference)
        data = self._fetch(url)
        return data if raw else Conference(data)

    def get_figure_image(self, uuid, add_ext=True, path=None):
        url = "%s/api/figures/%s/image" % (self.url, uuid)
        data = self._fetch_binary(url)
        if path is not None and not os.path.exists(path):
            os.mkdir(path)

        fn = os.path.join(path, uuid) if path is not None else uuid
        with open(fn, 'w+b') as fd:
            fd.write(data)
        if add_ext:
            ext = self._guess_filetype(fn)
            if ext is None:
                sys.stderr.write('[W] Could not determine image type for %s\n' % uuid)
                return fn
            new_fn = fn + '.' + ext
            os.rename(fn, new_fn)
            fn = new_fn
        return fn

    @authenticated
    def upload_abstract(self, abstract, conference, raw=None):
        #for now only support POST (create), but we should do PUT (update) too
        if isinstance(abstract, Abstract):
            abstract = abstract.to_data()
            if raw is None:
                raw = False

        if 'conference' in abstract:
            del abstract['conference']
        if 'uuid' in abstract and not len(abstract['uuid']):
            del abstract['uuid']

        url = "%s/api/conferences/%s/abstracts" % (self.url, conference)
        data = json.dumps(abstract)
        req = request.Request(url, data, {'Content-Type': 'application/json'})
        js = self._fetch(req)
        return js if raw else Abstract(js)

    @authenticated
    def patch_abstract(self, abstract, fields, raw=None):
        if isinstance(abstract, Abstract):
            abstract = abstract.to_data()
            if raw is None:
                raw = False
        uuid = abstract["uuid"]
        url = "%s/api/abstracts/%s" % (self.url, uuid)
        patches = [{"op": "add", "path": "/%s" % f, "value": abstract[f]} for f in fields]
        data = json.dumps(patches)
        req = request.Request(url, data, {'Content-Type': 'application/json'})
        req.get_method = lambda: 'PATCH'  # monkey see, monkey do
        js = self._fetch(req)
        return js if raw else Abstract(js)

    @authenticated
    def get_owners(self, uuid_or_url, otype='abstracts', raw=False):
        url = self._build_url(uuid_or_url, 'owners', otype=otype)
        data = self._fetch(url)
        return data if raw else [Owner(o) for o in data]

    @authenticated
    def get_state_log(self, uuid_or_url, raw=False):
        url = self._build_url(uuid_or_url, 'stateLog', otype='abstracts')
        data = self._fetch(url)
        return data if raw else [LogEntry(e) for e in data]

    @authenticated
    def set_state(self, uuid_or_url, state, note, raw=False):
        url = self._build_url(uuid_or_url, 'state', otype='abstracts')
        state_change = {'state': state, 'note': note}
        data = json.dumps(state_change)
        req = request.Request(url, data, {'Content-Type': 'application/json'})
        req.get_method = lambda: 'PUT'  # monkey see, monkey do
        data = self._fetch(req)
        return data if raw else [LogEntry(e) for e in data]

    def _build_url(self, uuid_or_url, target, otype='abstracts'):
        if uuid_or_url.startswith('http:') or uuid_or_url.startswith('https:'):
            url = uuid_or_url
        else:
            url = "%s/api/%s/%s/%s" % (self.url, otype, uuid_or_url, target)
        return url

    def _complete_abstract(self, abstract):
        try:
            owners = self.get_owners(abstract['owners'], raw=True)
            abstract.update({'owners': owners})
        except request.HTTPError:
            sys.stderr.write("Could not fetch owners for %s [%s]\n" % (abstract["uuid"], abstract['owners']))
        try:
            log = self.get_state_log(abstract['stateLog'], raw=True)
            abstract.update({'stateLog': log})
        except request.HTTPError:
            sys.stderr.write("Could not fetch state log for %s\n" % abstract["uuid"])

        return abstract

    def _fetch_binary(self, url):
        url_opener = self.__url_opener
        resp = url_opener.open(url)
        if resp.getcode() != 200:
            raise TransportError(resp.getcode(), "Could not fetch data")
        data = resp.read()
        return data

    def _fetch(self, url):
        url_opener = self.__url_opener
        resp = url_opener.open(url)
        if resp.getcode() != 200 and resp.getcode() != 201:
            raise TransportError(resp.getcode(), "Could not fetch data")
        data = resp.read()
        text = data.decode('utf-8')
        return json.loads(text)

    def _guess_filetype(self, path):
        import imghdr
        ext = imghdr.what(path)
        if ext is None:
            import subprocess
            if self._guess_mime_ext is None:
                import mimetypes
                mimetypes.init()
                self._guess_mime_ext = mimetypes.guess_extension
            x = subprocess.check_output(['file', '-b', '--mime-type', path]).strip()
            ext = self._guess_mime_ext(x)
        return ext

    @staticmethod
    def to_json(data):
        js = json.dumps(data, sort_keys=True, indent=4,
                        separators=(',', ': '), ensure_ascii=False)
        return js


if __name__ == "__main__":
    # test author formatting:
    names = [' Hans ', 'Hans', 'H.', 'H',
             ' Hans Juergen ', 'Hans Juergen', 'H. J.', ' H. J. ', 'H.J.', 'H.J', 'HJ',
             ' Hans - Juergen ', 'Hans-Juergen', 'H.-J.', ' H. - J. ', 'H.-J.', 'H-J',
             ' Peter Hans - Juergen ', 'Peter Hans-Juergen', 'P. H.-J.', 'P. H. - J. ', 'P.H.-J.', 'P H-J', 'PH-J', 'PETER', 'PET', 'Pet', 'PETE']
    print('sanitize_name():')
    for n in names:
        print('%-25s: %s' % (n, Author.sanitize_name(n, separator=' ', suffix='.')))
    print()
    print('format_initials():')
    for n in names:
        print('%-25s: %s' % (n, Author.format_initials(n, separator=' ', suffix='.')))
