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

from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.filter import pfb
import hsl
import math

class bpsk_ax25_demod(gr.hier_block2):
    """
    Hierarchical block for decoding BPSK AX.25 packets
    Input: complex stream at $rf_samp_rate
    Output: KISS encoded packets
    """
    def __init__(self, baudrate=9600, costas_loop_bw=2*math.pi/200, excess_bw=0.5, fll_loop_bw=2*math.pi/350, max_cfo=4e3, rf_samp_rate=2.4e6, symbol_Sync_loop_bw=2*math.pi/100):
        gr.hier_block2.__init__(self,
            "bpsk_ax25_demod",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),  # Input signature
            gr.io_signaturev(3, 3, [gr.sizeof_gr_complex*1, gr.sizeof_gr_complex*1, gr.sizeof_gr_complex*1])
            ) # Output signature

        self.message_port_register_hier_out("out")
        
        ##################################################
        # Parameters
        ##################################################
        self.baudrate = baudrate
        self.costas_loop_bw = costas_loop_bw
        self.excess_bw = excess_bw
        self.fll_loop_bw = fll_loop_bw
        self.max_cfo = max_cfo
        self.rf_samp_rate = rf_samp_rate
        self.symbol_Sync_loop_bw = symbol_Sync_loop_bw

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 9600*20
        self.sps = sps = int(samp_rate/baudrate)
        self.nfilts = nfilts = 64
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(nfilts, nfilts, 1.0/float(sps), excess_bw, 11*sps*nfilts)

        self.bpsk_constellation = bpsk_constellation = digital.constellation_bpsk().base()

        ##################################################
        # Blocks
        ##################################################
        self.pfb_arb_resampler_xxx_0 = pfb.arb_resampler_ccf(
        	  samp_rate/rf_samp_rate,
                  taps=None,
        	  flt_size=32)
        self.pfb_arb_resampler_xxx_0.declare_sample_delay(0)

        self.low_pass_filter_0_0_0 = filter.interp_fir_filter_ccf(1, firdes.low_pass(
        	1, samp_rate, ((1.0 + excess_bw) * baudrate/2.0) + min(baudrate, abs(1000*1.2)), baudrate / 10.0, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0 = filter.interp_fir_filter_ccf(1, firdes.low_pass(
        	1, samp_rate, (max_cfo+baudrate/2), baudrate / 10.0, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0 = filter.interp_fir_filter_ccf(1, firdes.low_pass(
        	1, samp_rate, (max_cfo+baudrate/2), baudrate / 10.0, firdes.WIN_HAMMING, 6.76))
        self.hsl_rms_agc_0 = hsl.rms_agc(alpha=1e-2, reference=0.5, )
        self.hsl_kiss_encoder_0 = hsl.kiss_encoder()
        self.digital_symbol_sync_xx_0_0 = digital.symbol_sync_cc(digital.TED_SIGNUM_TIMES_SLOPE_ML, sps, symbol_Sync_loop_bw, 1/math.sqrt(2.0), 1, 2*math.pi/100, 1, digital.constellation_bpsk().base(), digital.IR_PFB_MF, nfilts, (rrc_taps))
        self.digital_hdlc_deframer_bp_0_0 = digital.hdlc_deframer_bp(15, 500)
        self.digital_hdlc_deframer_bp_0 = digital.hdlc_deframer_bp(15, 500)
        self.digital_fll_band_edge_cc_0 = digital.fll_band_edge_cc(sps, excess_bw, 300, fll_loop_bw)
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2)
        self.digital_descrambler_bb_0 = digital.descrambler_bb(0x21, 0, 16)
        self.digital_costas_loop_cc_0 = digital.costas_loop_cc(costas_loop_bw, 2, False)
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(bpsk_constellation)
        self.blocks_not_xx_0_0_0 = blocks.not_bb()
        self.blocks_message_debug_0 = blocks.message_debug()
        self.blocks_and_const_xx_0_0_0 = blocks.and_const_bb(1)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.digital_hdlc_deframer_bp_0, 'out'), (self.blocks_message_debug_0, 'print_pdu'))
        self.msg_connect((self.digital_hdlc_deframer_bp_0, 'out'), (self.hsl_kiss_encoder_0, 'packet'))
        self.msg_connect((self.digital_hdlc_deframer_bp_0_0, 'out'), (self.blocks_message_debug_0, 'print_pdu'))
        self.msg_connect((self.digital_hdlc_deframer_bp_0_0, 'out'), (self.hsl_kiss_encoder_0, 'packet'))
        self.msg_connect((self.hsl_kiss_encoder_0, 'encoded_packet'), (self, 'out'))
        self.connect((self.blocks_and_const_xx_0_0_0, 0), (self.digital_descrambler_bb_0, 0))
        self.connect((self.blocks_and_const_xx_0_0_0, 0), (self.digital_hdlc_deframer_bp_0_0, 0))
        self.connect((self.blocks_not_xx_0_0_0, 0), (self.blocks_and_const_xx_0_0_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.digital_costas_loop_cc_0, 0), (self.digital_symbol_sync_xx_0_0, 0))
        self.connect((self.digital_costas_loop_cc_0, 0), (self, 1))
        self.connect((self.digital_descrambler_bb_0, 0), (self.digital_hdlc_deframer_bp_0, 0))
        self.connect((self.digital_diff_decoder_bb_0, 0), (self.blocks_not_xx_0_0_0, 0))
        self.connect((self.digital_fll_band_edge_cc_0, 0), (self.low_pass_filter_0_0_0, 0))
        self.connect((self.digital_fll_band_edge_cc_0, 0), (self, 2))
        self.connect((self.digital_symbol_sync_xx_0_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.digital_symbol_sync_xx_0_0, 0), (self, 0))
        self.connect((self.hsl_rms_agc_0, 0), (self.low_pass_filter_0_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.hsl_rms_agc_0, 0))
        self.connect((self.low_pass_filter_0_0, 0), (self.digital_fll_band_edge_cc_0, 0))
        self.connect((self.low_pass_filter_0_0_0, 0), (self.digital_costas_loop_cc_0, 0))
        self.connect((self, 0), (self.pfb_arb_resampler_xxx_0, 0))
        self.connect((self.pfb_arb_resampler_xxx_0, 0), (self.low_pass_filter_0, 0))

    def get_baudrate(self):
        return self.baudrate

    def set_baudrate(self, baudrate):
        self.baudrate = baudrate
        self.set_sps(int(self.samp_rate/self.baudrate))
        self.low_pass_filter_0_0_0.set_taps(firdes.low_pass(1, self.samp_rate, ((1.0 + self.excess_bw) * self.baudrate/2.0) + min(self.baudrate, abs(1000*1.2)), self.baudrate / 10.0, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.max_cfo+self.baudrate/2), self.baudrate / 10.0, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.max_cfo+self.baudrate/2), self.baudrate / 10.0, firdes.WIN_HAMMING, 6.76))

    def get_costas_loop_bw(self):
        return self.costas_loop_bw

    def set_costas_loop_bw(self, costas_loop_bw):
        self.costas_loop_bw = costas_loop_bw
        self.digital_costas_loop_cc_0.set_loop_bandwidth(self.costas_loop_bw)

    def get_excess_bw(self):
        return self.excess_bw

    def set_excess_bw(self, excess_bw):
        self.excess_bw = excess_bw
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1.0/float(self.sps), self.excess_bw, 11*self.sps*self.nfilts))
        self.low_pass_filter_0_0_0.set_taps(firdes.low_pass(1, self.samp_rate, ((1.0 + self.excess_bw) * self.baudrate/2.0) + min(self.baudrate, abs(1000*1.2)), self.baudrate / 10.0, firdes.WIN_HAMMING, 6.76))

    def get_fll_loop_bw(self):
        return self.fll_loop_bw

    def set_fll_loop_bw(self, fll_loop_bw):
        self.fll_loop_bw = fll_loop_bw
        self.digital_fll_band_edge_cc_0.set_loop_bandwidth(self.fll_loop_bw)

    def get_max_cfo(self):
        return self.max_cfo

    def set_max_cfo(self, max_cfo):
        self.max_cfo = max_cfo
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.max_cfo+self.baudrate/2), self.baudrate / 10.0, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.max_cfo+self.baudrate/2), self.baudrate / 10.0, firdes.WIN_HAMMING, 6.76))

    def get_rf_samp_rate(self):
        return self.rf_samp_rate

    def set_rf_samp_rate(self, rf_samp_rate):
        self.rf_samp_rate = rf_samp_rate
        self.pfb_arb_resampler_xxx_0.set_rate(self.samp_rate/self.rf_samp_rate)

    def get_symbol_Sync_loop_bw(self):
        return self.symbol_Sync_loop_bw

    def set_symbol_Sync_loop_bw(self, symbol_Sync_loop_bw):
        self.symbol_Sync_loop_bw = symbol_Sync_loop_bw
        self.digital_symbol_sync_xx_0_0.set_loop_bandwidth(self.symbol_Sync_loop_bw)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_sps(int(self.samp_rate/self.baudrate))
        self.pfb_arb_resampler_xxx_0.set_rate(self.samp_rate/self.rf_samp_rate)
        self.low_pass_filter_0_0_0.set_taps(firdes.low_pass(1, self.samp_rate, ((1.0 + self.excess_bw) * self.baudrate/2.0) + min(self.baudrate, abs(1000*1.2)), self.baudrate / 10.0, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.max_cfo+self.baudrate/2), self.baudrate / 10.0, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.max_cfo+self.baudrate/2), self.baudrate / 10.0, firdes.WIN_HAMMING, 6.76))

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1.0/float(self.sps), self.excess_bw, 11*self.sps*self.nfilts))

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts
        self.set_rrc_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts, 1.0/float(self.sps), self.excess_bw, 11*self.sps*self.nfilts))

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps

    def get_bpsk_constellation(self):
        return self.bpsk_constellation

    def set_bpsk_constellation(self, bpsk_constellation):
        self.bpsk_constellation = bpsk_constellation
