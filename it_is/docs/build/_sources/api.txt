JSON Api
==========

*It Is* provides the following data in JSON format:

Statements
-----------

Fetch a list of the last ``n`` statements::

    /api/statements/n/

Fetch a list of the last ``n`` statements by tag ``s``::

    /api/statements/n/?tag=s

You can fetch a list of the last ``n1`` statements offset by ``n2`` (while still restricting by tag)::

    /api/statements/n1/?offset=n2

You can also fetch a list of the last ``n1`` statements offset by ``n2`` while still restricting by tag::

    /api/statements/n/?offset=n2&tag=s
    
    
Returned Data Structure
^^^^^^^^^^^^^^^^^^^^^^^^^

Statements are always returned as an array of JSON objects. A GET request to a URL like ``/statements/5/tag/computer-science/`` would return something like this::

    [
        {id: 345, statement: "It is fun.", tag: ['computer-science', 'Computer Science']},
        {id: 320, statement: "It is often boring.", tag: ['computer-science', 'Computer Science']},
        {id: 278, statement: "It is necessary to know math.", tag: ['computer-science', 'Computer Science']},
        {id: 277, statement: "It is analytic.", tag: ['computer-science', 'Computer Science']},
        {id: 5, statement: "It is all about computers.", tag: ['computer-science', 'Computer Science']},
    
    }
    
Note that tag data is returned as a list of two values: the *slug* for the tag, which can be used to construct a URL or query and the tag *display name*.   

How offsets are handled
^^^^^^^^^^^^^^^^^^^^^^^^^

Any set of statements is necessarily finite. So, if you request an offset which exceeds the size of the set, the API returns a 404 error with the message "offset too large". For example, you are requesting a sets of tagged statements in increments of 10::

    /api/statements/10/?tag=computer-science
    
There are 100 total statements tagged this way. So this call would result in a 404::

    /api/statements/10/?tag=computer-science&offset=11

Item counts
^^^^^^^^^^^^

You can get counts of the number of items in the full set::

    /api/statements/count/
    
    100

And you can get the number of items from a tag subset::

    /api/statements/count/?tag=computer-science
    
    18    

Tags
-----

Searching for tags
^^^^^^^^^^^^^^^^^^^^^

You can retrieve a list of tags which matches a query string ``s``::

    /api/tags/search/s/

This will return an array of matching (``slug``, ``display name``) pairs in alphabetical order::

    [
        ["philology", "philology"],
        ["philosophy", "philosophy"],
        ["philadelphia-flyers", "Philadelphia Flyers"]
    
    ]

All tags
^^^^^^^^^

The following URL returns a list of all tags in the list of (``slug``, ``display name``) pairs format::
        
    /api/tags/
    
Most Used
^^^^^^^^^^^

This URL will return a list of the most-used tags::

    /api/tags/popular/

By default this will return the 20 most used tags, but you can regulate the number with a count parameter::

    api/tags/popular/?count=5