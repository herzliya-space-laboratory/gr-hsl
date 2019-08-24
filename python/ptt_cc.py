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

class ptt_cc(gr.sync_block):
    """
    "Push To talk".
    Copies "signal" input to output if "ptt" input is not all 0.
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="ptt_cc",
            in_sig=[numpy.complex64, numpy.float32],
            out_sig=[numpy.complex64])


    def work(self, input_items, output_items):
        if(all(input_items[1] <= 0.)):
            output_items[0][:] = numpy.complex64(0)
        else:
            output_items[0][:] = input_items[0]
        return len(output_items[0])

