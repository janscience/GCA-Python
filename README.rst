GCA-Python
==========

Python client for the G-Node Conference Application Suite.

Basic usage:

Download all abstracts of a given conference and store in them in abs.json:

    ./gca-client http://abstracts.g-node.org abstracts <Conference> > abs.json
    
Download all figures for a conference:

    ./gca-select abs.json figures.uuid | xargs ./gca-client http://abstracts.g-node.org image --path=images
    
