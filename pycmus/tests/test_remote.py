# Copyright 2018 Matthew Treinish
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

import mock

from pycmus import remote
from pycmus.tests import base


class TestRemote(base.TestCase):

    @mock.patch('socket.socket')
    def test_play(self, socket_mock):
        cmus = remote.PyCmus()
        with mock.patch.object(cmus, 'send_cmd') as send_mock:
            cmus.player_play()
            send_mock.assert_called_once_with('player-play\n')
