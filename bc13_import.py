#!/usr/bin/env python
from __future__ import print_function

from gca.core import Abstract, Reference, Author, Affiliation, Session
from gca.auth import UPAuth

import argparse
import sys
import codecs
import json
from nameparser import HumanName


"""
Example usage:

./bc13_import.py "/home/andrey/data/BCCN13/bc13data.js" "2397dc3a-5f2c-41f0-aaea-771daee7382f"

where UUID is the cconferencce ID to upload abstracts.
"""


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

    values = old['epithet'].split(',')
    parse = lambda x: int(x.replace("*", ""))
    author.affiliations = [parse(x) for x in values if x != '*']

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
    convert_field(old, 'doi', abstract)

    abstract.references = convert_refs(old)
    abstract.authors = convert_authors(old)
    abstract.affiliations = convert_affiliations(old)

    abstract.state = 'Accepted'
    return abstract

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GCA - import old BC13 JS')
    parser.add_argument('file', type=str, default='-')
    parser.add_argument('conference', type=str)
    parser.add_argument('host', nargs='?', type=str, default='http://localhost:9000')
    parser.add_argument('user', nargs='?', type=str, default='alice@foo.com')
    parser.add_argument('password', nargs='?', type=str, default='testtest')
    args = parser.parse_args()

    fd = codecs.open(args.file, 'r', encoding='utf-8') if args.file != '-' else sys.stdin

    data = fd.read()
    fd.close()
    bc13 = json.loads(data)

    new = [convert_abstract(old) for old in bc13]

    auth = UPAuth(user=args.user, password=args.password)
    session = Session(args.host, auth)

    for i, to_send in enumerate(new):
        try:
            res = session.upload_abstract(to_send, args.conference, raw=True)
        except:
            print(json.dumps(to_send.to_data()))

        print("Uploaded %d abstracts..\r" % i, end="")

    # test output
    #print(json.dumps(to_send.to_data()))
    #js = Abstract.to_json(new)
    #sys.stdout.write(js.encode('utf-8'))
