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

import logging
import os
import socket
import time

import six

from pycmus import exceptions

LOG = logging.getLogger(__name__)

class PyCmus(object):

    def __init__(self, server=None, socket_path=None, password=None):
        super(PyCmus, self).__init__()
        if server:
            self.server = server
            if not password:
                raise exceptions.ConfigurationError(
                    "A password is required if using a remote connection")
            self.password = password
            self.socket_file = None
        else:
            self.socket_file = self._get_socket_path(socket_path)
            self.server = None
            self.password = None
            if password:
                LOG.warning("Provided password is ignored in the local case")
        if not self.server:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)
        else:
            # TODO(mtreinish: Add support for ipv6
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        server = self.server or self.socket_file
        self.socket.connect(server)
        self.socket.setblocking(0)

    def _get_cmus_conf_dir(self):
        if socket_path:
            return socket_path
        if "CMUS_HOME" in os.environ:
            conf_dir = os.environ["CMUS_HOME"]
        elif os.path.isdir(os.path.join(os.path.expanduser('~'), '.cmus')):
            conf_dir = os.path.join(os.path.expanduser('~'), '.cmus')
        elif "XDG_CONFIG_HOME" in os.environ:
            if os.path.isdir(os.path.join(os.environ['XDG_CONFIG_HOME'],
                                          'cmus')):
                conf_dir = os.path.join(os.environ["XDG_CONFIG_HOME"], 'cmus')
        elif os.path.isdir(os.path.join(os.path.expanduser('~'), '.config',
                                        'cmus')):
            conf_dir = os.path.join(os.path.expanduser('~'), '.config', 'cmus')

        else:
            os.mkdir(os.path.join(os.path.expanduser('~'), '.cmus'))
            conf_dir = os.path.join(os.path.expanduser('~'), '.cmus') 
        return conf_dir

    def _get_socket_path(self, socket_path=None):
        if "CMUS_SOCKET" in os.environ:
            return os.environ["CMUS_SOCKET"]
        else:
            if "XDG_RUNTIME_DIR" in os.environ:
                return os.path.join(os.environ["XDG_RUNTIME_DIR"],
                                    "cmus-socket")
            else:
                conf_dir = self._get_cmus_conf_dir()
                return os.path.join(conf_dir, 'socket')

    def send_cmd(self, cmd):
        if self.password:
            self.socket.sendall('passwd %s\n' % self.password)
            resp = self._read_response()
            print(resp)
            if resp != 1:
                raise exceptions.InvalidPassword()
        self.socket.sendall(six.binary_type(cmd.encode('utf8')))
        resp = self._read_response()
        print(resp)

    def _read_response(self):
        total_data = []
        while True:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                total_data.append(six.text_type(data))
                line_break = six.binary_type('\n'.encode('utf8'))
                if data.endswith(line_break):
                    break
            except socket.error as e:
                if e.errno == socket.errno.EWOULDBLOCK:
                    time.sleep(1)
                    continue
                else:
                    raise
        return ''.join(total_data)

    def toggle_repeat(self):
        self.send_cmd('toggle repeat\n')

    def toggle_shuffle(self):
        self.send_cmd('toggle shuffle\n')

    def player_stop(self):
        self.send_cmd('player-stop\n')

    def player_next(self):
        self.send_cmd('player-next\n')

    def player_prev(self):
        self.send_cmd('player-prev\n')

    def player_play(self):
        self.send_cmd('player-play\n')

    def player_pause(self):
        self.send_cmd('player-pause\n')

    def player_pause_playback(self):
        self.send_cmd('player-pause-playback\n')

    def player_play(self, play_file):
        self.send_cmd('player-play %s\n' % os.path.abspath(play_file))

    def set_volume(self, volume):
        self.send_cmd('vol %s\n' % volume)

    def seek(self, seek):
        self.send_cmd('seek %s\n' % seek)

    def status(self):
        return self.send_cmd('status\n')
