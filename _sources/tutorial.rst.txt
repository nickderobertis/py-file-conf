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
has some limitations on what kinds of objects it can support. Here are
some of the currently known limitations:

* Classes which do not define ``__init__``
* ``dataclasses``

Object Model
==============

``pyfileconf`` is made to work with existing functions and classes
without modification, but it is possible to define certain methods on
the class to modify how ``pyfileconf`` works with the objects. See
:class:`PyfileconfBase` for the available methods and what they
do.
