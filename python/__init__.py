#
# Copyright 2008,2009 Free Software Foundation, Inc.
#
# This application is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This application is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# The presence of this file turns this directory into a Python package

'''
This is the GNU Radio HSL module. Place your Python package
description here (python/__init__.py).
'''

# import swig generated symbols into the hsl namespace
try:
	# this might fail if the module is python-only
	from hsl_swig import *
except ImportError:
	pass

# import any pure python here
from parse_rigctl import parse_rigctl
from doppler_correction_cc import doppler_correction_cc
from ptt_cc import ptt_cc
from kiss_encoder import kiss_encoder
from rms_agc import rms_agc
from bpsk_ax25 import bpsk_ax25
from afsk_ax25 import afsk_ax25
#
