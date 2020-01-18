# cython: language_level=3
#  Drakkar-Software OctoBot-Backtesting
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.

from octobot_backtesting.collectors.data_collector cimport DataCollector


cdef class ExchangeDataCollector(DataCollector):
    cdef public str exchange_name

    cdef public list symbols
    cdef public list time_frames

    cdef bint use_all_available_timeframes

    cdef void _load_timeframes_if_necessary(self)
    cdef void _load_all_available_timeframes(self)
