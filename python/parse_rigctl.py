#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2019 ido.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
import pmt
from gnuradio import gr

class parse_rigctl(gr.basic_block):
    """
    This block parses a rigctl message (usually from Socket PDU).
    Output is the frequency in the message.
    Example:
    Input: F 1000
    Output: 1000
    This is meant to control a Signal Source for doppler correction.
    """
    def __init__(self, base_freq=0, verbose=False):
        gr.basic_block.__init__(self,
            name="parse_rigctl",
            in_sig=None,
            out_sig=None)

        self.base_freq = int(base_freq)
        self.verbose = bool(verbose)

        self.message_port_register_in(pmt.intern("rigctl"))
        self.message_port_register_out(pmt.intern("freq"))
        self.set_msg_handler(pmt.intern("rigctl"), self.handle_rigctl)

    def handle_rigctl(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        x = pmt.u8vector_elements(msg)
        if (chr(x[0]) is not 'F') and (chr(x[0]) is not 'f'):
            print "[ERROR] Not rigctl message."
            print "Example: F 145970000"
            return
        string = ""
        for num in x:
            string += chr(num)
        message_freq = int(string[2:])
        if self.verbose:
            print()
            print("[Doppler Correction] Verbose")
            print()
            print("Recieved frequency command with frequency: " + str(message_freq))
            print("Output is: " + str(self.base_freq-message_freq))
        self.message_port_pub(pmt.intern('freq'), pmt.from_double(self.base_freq-message_freq))

    def get_base_freq(self):
        return self.base_freq

    def set_base_freq(self, base_freq):
        self.base_freq = base_freq
