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

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
import hsl

class doppler_correction_cc(gr.hier_block2):
    """
    Doppler correction block.
    Wrapper around Parse Rigctl, multiply signal based on
    Rigctl command (TCP)
    """
    def __init__(self, base_freq=0, port=52001, samp_rate=48000):
        gr.hier_block2.__init__(self,
            "doppler_correction_cc",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_gr_complex)) # Output signature

        ##################################################
        # Parameters
        ##################################################
        self.base_freq = base_freq
        self.port = port
        self.samp_rate = samp_rate

        ##################################################
        # Blocks
        ##################################################
        self.hsl_parse_rigctl_0 = hsl.parse_rigctl(base_freq)
        self.blocks_socket_pdu_0 = blocks.socket_pdu("TCP_SERVER", '', str(port), 10000, False)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 0, 1, 0)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_socket_pdu_0, 'pdus'), (self.hsl_parse_rigctl_0, 'rigctl'))
        self.msg_connect((self.hsl_parse_rigctl_0, 'freq'), (self.analog_sig_source_x_0, 'freq'))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self, 0))
        self.connect((self, 0), (self.blocks_multiply_xx_0, 0))
        
    def get_base_freq(self):
        return self.base_freq

    def set_base_freq(self, base_freq):
        self.base_freq = base_freq
        self.hsl_parse_rigctl_0.set_base_freq(base_freq)

    def get_port(self):
        return self.port
    
    def set_port(self, port):
        self.port = port
    
    def get_samp_rate(self):
        return self.samp_rate
    
    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
