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
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
import math

class afsk_ax25(gr.hier_block2):
    """
    Hierarchical block for encoding AFSK (FM Mode) AX.25 packets
    Input: AX.25 packets before HDLC (no CRC, flags & bit stuffing)
    Output: Complex stream of encoded packets at $rf_samp_rate

    Params:
    baud_rate: Data rate
    mark_freq: AFSK mark frequency (represents 0)
    space_freq: AFSK space frequency (represents 1)
    preamble_len: Length of premable in milliseconds (repeating AX.25 flags 01111110)
    postamble_len: Length of postamble in number of bytes (also AX.25 flags)
    """
    def __init__(self, baud_rate=1200, mark_freq=1200, offset=50e3, postamble_len=4, preamble_len=.1, rf_samp_rate=2.4e6, space_freq=2200):
        gr.hier_block2.__init__(self,
            "afsk_ax25",
            gr.io_signature(0, 0, 0),  # Input signature
            gr.io_signature(1, 1, gr.sizeof_gr_complex)) # Output signature

        self.message_port_register_hier_in("packets")

        ##################################################
        # Parameters
        ##################################################
        self.baud_rate = baud_rate
        self.mark_freq = mark_freq
        self.offset = offset
        self.postamble_len = postamble_len
        self.preamble_len = preamble_len
        self.rf_samp_rate = rf_samp_rate
        self.space_freq = space_freq

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 48000
        self.sps = sps = samp_rate/baud_rate

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=int(rf_samp_rate),
                decimation=int(samp_rate),
                taps=None,
                fractional_bw=None,
        )
        self.digital_hdlc_framer_pb_0 = digital.hdlc_framer_pb('packet_len')
        self.digital_diff_encoder_bb_0 = digital.diff_encoder_bb(2)
        self.digital_chunks_to_symbols_xx_1 = digital.chunks_to_symbols_bf(([mark_freq, space_freq]), 1)
        self.dc_blocker_xx_0 = filter.dc_blocker_cc(32, True)
        self.blocks_vector_source_x_0_0 = blocks.vector_source_b([0x7e], True, 1, [])
        self.blocks_vector_source_x_0 = blocks.vector_source_b([0x7e], True, 1, [])
        self.blocks_vco_f_0 = blocks.vco_f(samp_rate, 2*math.pi, .95)
        self.blocks_tagged_stream_mux_0 = blocks.tagged_stream_mux(gr.sizeof_char*1, 'packet_len', 0)
        self.blocks_stream_to_tagged_stream_0_0 = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, postamble_len, "packet_len")
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, int(baud_rate*preamble_len)/8, "packet_len")
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_char*1, sps)
        self.blocks_not_xx_0_0_0_0 = blocks.not_bb()
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_and_const_xx_0_0_0_0 = blocks.and_const_bb(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(rf_samp_rate, analog.GR_COS_WAVE, offset, 1, 0)
        self.analog_nbfm_tx_0 = analog.nbfm_tx(
        	audio_rate=samp_rate,
        	quad_rate=samp_rate,
        	tau=75e-6,
        	max_dev=5e3,
        	fh=-1.0,
                )



        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self, 'packets'), (self.digital_hdlc_framer_pb_0, 'in'))
        self.connect((self.analog_nbfm_tx_0, 0), (self.dc_blocker_xx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_and_const_xx_0_0_0_0, 0), (self.blocks_repeat_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self, 0))
        self.connect((self.blocks_not_xx_0_0_0_0, 0), (self.blocks_and_const_xx_0_0_0_0, 0))
        self.connect((self.blocks_repeat_0, 0), (self.digital_chunks_to_symbols_xx_1, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_tagged_stream_mux_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0_0, 0), (self.blocks_tagged_stream_mux_0, 2))
        self.connect((self.blocks_tagged_stream_mux_0, 0), (self.digital_diff_encoder_bb_0, 0))
        self.connect((self.blocks_vco_f_0, 0), (self.analog_nbfm_tx_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.blocks_vector_source_x_0_0, 0), (self.blocks_stream_to_tagged_stream_0_0, 0))
        self.connect((self.dc_blocker_xx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.digital_chunks_to_symbols_xx_1, 0), (self.blocks_vco_f_0, 0))
        self.connect((self.digital_diff_encoder_bb_0, 0), (self.blocks_not_xx_0_0_0_0, 0))
        self.connect((self.digital_hdlc_framer_pb_0, 0), (self.blocks_tagged_stream_mux_0, 1))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_multiply_xx_0, 1))

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate
        self.set_sps(self.samp_rate/self.baud_rate)
        self.blocks_stream_to_tagged_stream_0.set_packet_len(int(self.baud_rate*self.preamble_len)/8)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(int(self.baud_rate*self.preamble_len)/8)

    def get_mark_freq(self):
        return self.mark_freq

    def set_mark_freq(self, mark_freq):
        self.mark_freq = mark_freq
        self.digital_chunks_to_symbols_xx_1.set_symbol_table(([self.mark_freq, self.space_freq]))

    def get_offset(self):
        return self.offset

    def set_offset(self, offset):
        self.offset = offset
        self.analog_sig_source_x_0.set_frequency(self.offset)

    def get_postamble_len(self):
        return self.postamble_len

    def set_postamble_len(self, postamble_len):
        self.postamble_len = postamble_len
        self.blocks_stream_to_tagged_stream_0_0.set_packet_len(self.postamble_len)
        self.blocks_stream_to_tagged_stream_0_0.set_packet_len_pmt(self.postamble_len)

    def get_preamble_len(self):
        return self.preamble_len

    def set_preamble_len(self, preamble_len):
        self.preamble_len = preamble_len
        self.blocks_stream_to_tagged_stream_0.set_packet_len(int(self.baud_rate*self.preamble_len)/8)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(int(self.baud_rate*self.preamble_len)/8)

    def get_rf_samp_rate(self):
        return self.rf_samp_rate

    def set_rf_samp_rate(self, rf_samp_rate):
        self.rf_samp_rate = rf_samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.rf_samp_rate)

    def get_space_freq(self):
        return self.space_freq

    def set_space_freq(self, space_freq):
        self.space_freq = space_freq
        self.digital_chunks_to_symbols_xx_1.set_symbol_table(([self.mark_freq, self.space_freq]))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_sps(self.samp_rate/self.baud_rate)

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.blocks_repeat_0.set_interpolation(self.sps)