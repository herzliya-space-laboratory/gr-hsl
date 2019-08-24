#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2019 Ido.
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
from gnuradio import gr
import pmt
import collections
import array

FEND = numpy.uint8(0xc0)
FESC = numpy.uint8(0xdb)
TFEND = numpy.uint8(0xdc)
TFESC = numpy.uint8(0xdd)

class kiss_encoder(gr.basic_block):
    """
    KISS Encoder
    Applies the KISS protocol to a packet:
    https://en.wikipedia.org/wiki/KISS_(TNC)
    Impolmentation taken from gr-satellites:
    https://github.com/daniestevez/gr-satellites/blob/master/python/pdu_to_kiss.py
    """
    def __init__(self):
        gr.basic_block.__init__(self,
            name="kiss_encoder",
            in_sig=None,
            out_sig=None)

        self.message_port_register_in(pmt.intern("packet"))
        self.message_port_register_out(pmt.intern("encoded_packet"))
        self.set_msg_handler(pmt.intern("packet"), self.encode)
    
    def encode(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print "[ERROR] Received invalid message type. Expected u8vector"
            return

        buff = list()
        buff.append(FEND)
        buff.append(numpy.uint8(0))
        for byte in pmt.u8vector_elements(msg):
            if byte == FESC:
                buff.append(FESC)
                buff.append(TFESC)
            elif byte == FEND:
                buff.append(FESC)
                buff.append(TFEND)
            else:
                buff.append(numpy.uint8(byte))

            buff = array.array('B', buff)

            self.message_port_pub(pmt.intern("encoded_packet"), pmt.cons(pmt.PMT_NIL, pmt.init_u8vector(len(buff), buff)))
        
        
