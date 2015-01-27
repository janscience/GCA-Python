#!/usr/bin/env python
from __future__ import print_function

from gca.core import Abstract, Reference, Author, Affiliation, Session
from gca.auth import UPAuth

import argparse
import sys
import codecs
import json
from nameparser import HumanName


def convert_field(obj, old_name, abstract, new_name=None, def_value=None):
    if new_name is None:
        new_name = old_name
    if old_name in obj and obj[old_name]:
        data = obj[old_name]
        if type(data) == unicode or type(data) == str:
            data = data.strip()
        setattr(abstract, new_name, data)
    elif def_value is not None:
        setattr(abstract, new_name, def_value)


def convert_ref1(data):
    ref = Reference()
    ref.text = data
    return ref


def convert_refs(old):
    data = old['refs']
    lines = data.split('\n')
    clean = filter(bool, lines)
    refs = [convert_ref1(x) for x in clean]
    return refs


def convert_author1(old):
    data = old['name']
    h_name = HumanName(data)
    author = Author()
    author.first_name = h_name.first
    author.middle_name = h_name.middle
    author.last_name = h_name.last
    return author


def convert_affiliation1(old):
    data = old['address']
    c = list(reversed(data.split(',')))
    k = len(c)
    af = Affiliation()
    if k > 3:
        af.department = ", ".join(c[3:])

    if k > 2:
        af.section = c[2].strip()

    if k > 1:
        af.address = c[1].strip()

    af.country = c[0].strip()
    return af


def convert_affiliations(old):
    return [convert_affiliation1(o) for o in old['affiliations']]


def convert_authors(old):
    return [convert_author1(o) for o in old['authors']]


def convert_abstract(old):
    abstract = Abstract()
    convert_field(old, 'title', abstract)
    convert_field(old, 'abstract', abstract, 'text')
    convert_field(old, 'acknowledgements', abstract, 'acknowledgements')
    convert_field(old, 'topic', abstract)

    abstract.references = convert_refs(old)
    abstract.authors = convert_authors(old)
    abstract.affiliations = convert_affiliations(old)

    abstract.state = 'Published'
    return abstract

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GCA - import old BC13 JS')
    parser.add_argument('file', type=str, default='-')
    parser.add_argument('user', type=str, default='alice@foo.com')
    parser.add_argument('password', type=str, default='testtest')
    parser.add_argument('host', type=str, default='http://localhost:9000')
    parser.add_argument('conference', type=str, default='8e8fc1f4-7843-418a-b0b8-c8f0d7fc7f89')
    args = parser.parse_args()

    fd = codecs.open(args.file, 'r', encoding='utf-8') if args.file != '-' else sys.stdin

    data = fd.read()
    fd.close()
    bc13 = json.loads(data)

    new = [convert_abstract(old) for old in bc13]

    auth = UPAuth(user=args.user, password=args.password)
    session = Session(args.host, auth)

    # upload single abstract
    res = session.upload_abstract(new[0], conference, raw=True)

    # test output 
    #js = Abstract.to_json(new)
    #sys.stdout.write(js.encode('utf-8'))
