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
    """PyCmus remote class

    This class is used to create a PyCmus remote object that is used to send
    commands to a running cmus. It can be used to connect to either a locally
    running cmus or a cmus on a remote machine that is configured to listen
    over the network. If neither a server or a socket file are provided the
    PyCmus object will look for a running cmus in the default locations and
    try to connect to that.

    :param str server: The remote host to connect to the cmus socket on
    :param str socket_path: The path to the local unix socket for cmus
    :param str password: The password to use when establishing a remote
                         connection. It is a required field if a server is
                         provided. If a socket_path is used this is ignored
    :param int port: The port to use for remote connections. If one is not
                     provided it will just use the default port of 3000.
    """
    def __init__(self, server=None, socket_path=None, password=None,
                 port=3000):
        super(PyCmus, self).__init__()
        self.port = port
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
            self.socket.connect(self.socket_file)
        else:
            for addr in socket.getaddrinfo(self.server, self.port):
                af, socktype, proto, cannonname, sa = addr
                try:
                    self.socket = socket.socket(af, socket.SOCK_STREAM, proto)
                    self.socket.connect(sa)
                except Exception:
                    continue
                break
            else:
                raise exceptions.ConfigurationError(
                    "Unable to connect to server %s" % self.server)
        self.socket.setblocking(0)

    def _get_cmus_conf_dir(self):
        if self.socket_path:
            return self.socket_path
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
        """Send a raw command to cmus

        :param str cmd: The command to send to cmus
        :return resp: The response from cmus from the issued command
        :rtype: str
        """

        if self.password:
            passwd_str = 'passwd %s\n' % self.password
            self.socket.sendall(six.binary_type(passwd_str.encode('utf8')))
            resp = self._read_response()
            if resp.startswith('authentication failed'):
                raise exceptions.InvalidPassword()
        self.socket.sendall(six.binary_type(cmd.encode('utf8')))
        resp = self._read_response()
        return resp

    def _read_response(self):
        total_data = []
        while True:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                total_data.append(six.text_type(data.decode('utf8')))
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
        """Send a toggle repeat command."""
        self.send_cmd('toggle repeat\n')

    def toggle_shuffle(self):
        """Send a toggle shuffle command."""
        self.send_cmd('toggle shuffle\n')

    def player_stop(self):
        """Send a player stop command."""
        self.send_cmd('player-stop\n')

    def player_next(self):
        """Send a player next command."""
        self.send_cmd('player-next\n')

    def player_prev(self):
        """Send a player previous command."""
        self.send_cmd('player-prev\n')

    def player_play(self):
        """Send a player play command."""
        self.send_cmd('player-play\n')

    def player_pause(self):
        """Send a player pause command."""
        self.send_cmd('player-pause\n')

    def player_pause_playback(self):
        """Send a player pause playback command."""
        self.send_cmd('player-pause-playback\n')

    def player_play_file(self, play_file):
        """Send a player play command with a file

        :param str play_file: The path or url to the file to play
        """

        self.send_cmd('player-play %s\n' % play_file)

    def set_volume(self, volume):
        """Send a player set volume command

        :param int volume: the volume to set the volume to
        """
        self.send_cmd('vol %s\n' % volume)

    def seek(self, seek):
        """Send a player seek command

        :param seek: The position to seek the player to. This can either be a
                     raw integer which will be the position in number of secs
                     (where 0 is the start of the file) or it can be an +/- #
                     offset where the position will either either move forward
                     or backwards respectively the number of seconds specified
        """

        self.send_cmd('seek %s\n' % seek)

    def status(self):
        """Send a status command

        :return status: The player status, it is a newline seperated string
                        with the current state of the player.
        :rtype: str
        """
        return self.send_cmd('status\n')

    def get_status_dict(self):
        """Send a status command and format response as a dictionary

        :return status: The player status, it is a newline seperated string
                        with the current state of the player.
        :rtype: dict
        """
        status_str = self.status()
        status_list = status_str.split('\n')
        status_dict = {'tag': {}, 'set': {}}
        for line in status_list:
            line_split = line.split(' ')
            if len(line_split) == 2:
                status_dict[line_split[0]] = line_split[1]
            elif len(line_split) > 2:
                # If there are spaces in the filename handle this case
                if line_split[0] == 'file':
                    status_dict['file'] = ' '.join(line_split[1:])
                else:
                    if line_split[0] not in status_dict:
                        status_dict[line_split[0]] = {}
                    status_dict[line_split[0]][line_split[1]] = ' '.join(
                        line_split[2:])
        if status_dict == {'tag': {}, 'set': {}}:
            return None
        else:
            return status_dict
