QuickStart
==========

Installation
------------

To install baidupcs, simply:

.. code-block:: bash

    $ pip install baidupcs


Basic Usage
-----------

.. code-block:: python

    >>> from baidupcs import PCS
    >>> pcs = PCS('access_token')
    >>> response = pcs.info()
    >>> response
    <Response [200]>
    >>> response.ok
    True
    >>> response.status_code
    200
    >>> response.content
    '{"quota":6442450944,"used":5138887,"request_id":1216061570}'
    >>>
    >>> response.json()
    {u'used': 5138887, u'quota': 6442450944L, u'request_id': 1216061570}
