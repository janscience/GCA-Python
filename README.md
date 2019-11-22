# GCA-Python

Python command line client for the [G-Node Conference Application](https://github.com/G-Node/GCA-Web) 
Suite (GCA-Web). The GCA-Python client provides convenience functions for page 
administrators to download conference and abstract information for a conference hosted 
via a GCA-Web application.

## Installation

Fetch all required scripts via git clone. 

    git clone https://github.com/G-Node/GCA-Python.git


## Basic usage

- Download conference information as JSON

    `./gca-client -a [HostURL] [ConfName] > conf.json`

    - [HostURL] ... where the GCA-Web abstract site is hosted
    - [ConfName] ... short name of the conference used by the GCA-Web abstract site.
    
    e.g. conference is hosted at https://abstracts.conferences.org/neuro2019

    `./gca-client -a https://abstracts.conferences.org neuro2019 > conf.json`

- Download abstracts as JSON; the abstracts should be sorted via the web interface 
  before they are downloaded.

    `./gca-client [HostURL] abstracts --full [ConfName] > abstracts.json`

- Download figures associated with the downloaded list of abstracts. The path where the 
  images should be downloaded to can be specified via an optional `--path` flag.

    `./gca-select figures.uuid | xargs ./gca-client [HostURL] image`

- Filter abstracts to include only accepted abstracts items

    `./gca-filter [abstracts.json] "state=accepted" >  [newfile.json]`

- Use the linter script to verify all abstracts are valid

    `./gca-lint [abstracts.json]`

## Authentication

A `.netrc` file with `machine`, `login` and `password` in the users home root is required.
`login` has to be a GCA-Web user with appropriate conference admin privileges to access the 
conferences' information. e.g. content of a .netrc file:

    machine abstracts.conferences.org
    login username@host.com
    password plainPassword
