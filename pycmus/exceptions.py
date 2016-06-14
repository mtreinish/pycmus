# Copyright 2016 Matthew Treinish
#
# This file is part of pycmus
#
# pycmus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pycmus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pycmus.  If not, see <http://www.gnu.org/licenses/>.


class CmusException(Exception):
    message = "An unknown exception occurred"

    def __init__(self, *args, **kwargs):
        super(CmusException, self).__init__()
        try:
            self._error_string = self.message % kwargs
        except Exception:
            # at least get the core message out if something happened
            self._error_string = self.message
        if len(args) > 0:
            # If there is a non-kwarg parameter, assume it's the error
            # message or reason description and tack it on to the end
            # of the exception message
            # Convert all arguments into their string representations...
            args = ["%s" % arg for arg in args]
            self._error_string = (self._error_string +
                                  "\nDetails: %s" % '\n'.join(args))

    def __str__(self):
        return self._error_string


class ConfigurationError(CmusException):
    message = "A configuration error occured"


class CmusNotRunning(CmusException):
    message = "CMUS doesn't appear to be running, please ensure it is"


class InvalidPassword(CmusException):
    message = "The provided password is incorrect/invalid"
