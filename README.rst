======
pycmus
======
A python library for sending commands to the cmus music player:

https://cmus.github.io/

It uses the same socket interface as the cmus-remote command.

Complete documentation is here: http://pycmus.readthedocs.io/en/latest/

Usage
=====

Using pycmus is pretty straightforward you just need to init a PyCmus object
and then issue commands to it. For example::

  from pycmus import remote

  cmus = remote.PyCmus()
  print(cmus.status())

will connect to a running cmus instance (with the socket file in the default
location) and print the player status.

For a complete API documentation see: :ref:`pycmus_api`.
