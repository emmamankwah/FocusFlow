"""
repository package
==================

Data-access modules.  Each module owns one aggregate (``user``, later
``task``, ``calendar``, ...) and exposes plain functions that take and return
plain Python values.

Package marker
--------------
This directory previously shipped ``__init_.py`` (one underscore missing).
Python's implicit namespace packages made ``from repository.user import ...``
work anyway, but tooling (mypy, pytest's rootdir detection, wheel building)
treated the directory differently from the other packages.  The file is now
correctly named ``__init__.py``.
"""
