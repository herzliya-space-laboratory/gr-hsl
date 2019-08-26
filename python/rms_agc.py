#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2019 Daniel Estevez.
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
# c

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes

class rms_agc(gr.hier_block2):
    """
    AGC using RMS
    Flograph from gr-satellites:
        https://github.com/daniestevez/gr-satellites/blob/master/apps/hierarchical/rms_agc.grc
    By Daniel Estevez:
        https://destevez.net/2017/08/agc-for-gr-satellites/

    """
    def __init__(self, alpha=1e-2, reference=0.5):
        gr.hier_block2.__init__(self,
            "rms_agc",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_gr_complex)) # Output signature

        ##################################################
        # Parameters
        ##################################################
        self.alpha = alpha
        self.reference = reference

        ##################################################
        # Blocks
        ##################################################
        self.blocks_rms_xx_0 = blocks.rms_cf(alpha)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vff((1.0/reference, ))
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_divide_xx_0 = blocks.divide_cc(1)
        self.blocks_add_const_vxx_0 = blocks.add_const_vff((1e-20, ))

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_divide_xx_0, 0), (self, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_divide_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.blocks_rms_xx_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self, 0), (self.blocks_divide_xx_0, 0))
        self.connect((self, 0), (self.blocks_rms_xx_0, 0))

    def get_alpha(self):
        return self.alpha

    def set_alpha(self, alpha):
        self.alpha = alpha
        self.blocks_rms_xx_0.set_alpha(self.alpha)

    def get_reference(self):
        return self.reference

    def set_reference(self, reference):
        self.reference = reference
        self.blocks_multiply_const_vxx_0.set_k((1.0/self.reference, ))
