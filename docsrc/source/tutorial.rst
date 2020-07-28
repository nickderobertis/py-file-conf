Getting started with pyfileconf
**********************************

Install
=======

Install via::

    pip install pyfileconf

Usage
=========

Some highlighted functionality.

This is a simple example::

    import pyfileconf


Supported Objects
===================

While the goal is to support as many objects as possible, the library
has some limitations on what kinds of objects it can support. Note
that support for all of these items are on the road map. Here are
some of the currently known limitations:

* Classes which do not define ``__init__``
* ``dataclasses``
* Functions or classes ``__init__`` which use variable arguments
  or keyword arguments (``*args, **kwargs``)
* Decorated functions where the wrapper in the decorator uses
  variable arguments or keyword arguments (``*args, **kwargs``)

Object Model
==============

``pyfileconf`` is made to work with existing functions and classes
without modification, but it is possible to define certain methods on
the class to modify how ``pyfileconf`` works with the objects. See
:class:`PyfileconfBase` for the available methods and what they
do.


Other Known Limitations
=========================

There are limitations in the way you one work with ``pyfileconf``
beyond the supported objects. These are also on the road map to
resolve over time so that (nearly) any valid Python is supported.

* Functions and classes cannot be defined in config files (``def``
  and ``class`` statements. Other ways of creating them such as
  ``lambdas`` and using class factory functions work fine.)
* Cannot do multiple inline assignments in config files (``a = b = 5``)