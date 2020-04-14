#  Drakkar-Software OctoBot
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
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import json
import logging
from abc import abstractmethod

import time

from octobot_commons.constants import CONFIG_TIME_FRAME, CONFIG_CRYPTO_CURRENCIES, CONFIG_CRYPTO_PAIRS

from octobot_backtesting.collectors.data_collector import DataCollector
from octobot_backtesting.enums import ExchangeDataTables, DataTables, DataFormats
from octobot_backtesting.importers.exchanges.exchange_importer import ExchangeDataImporter

try:
    from octobot_trading.constants import CONFIG_EXCHANGES
except ImportError:
    logging.error("ExchangeDataCollector requires OctoBot-Trading package installed")


class ExchangeDataCollector(DataCollector):
    VERSION = "1.0"
    IMPORTER = ExchangeDataImporter

    def __init__(self, config, exchange_name, symbols, time_frames, use_all_available_timeframes=False,
                 data_format=DataFormats.REGULAR_COLLECTOR_DATA):
        super().__init__(config, data_format=data_format)
        self.exchange_name = exchange_name
        self.symbols = symbols if symbols else []
        self.time_frames = time_frames if time_frames else []
        self.use_all_available_timeframes = use_all_available_timeframes
        self.set_file_path()

    @abstractmethod
    def _load_all_available_timeframes(self):
        raise NotImplementedError("_load_all_available_timeframes is not implemented")

    async def initialize(self):
        self.create_database()
        await self.database.initialize()

        # set config from params
        self.config[CONFIG_TIME_FRAME] = self.time_frames
        self.config[CONFIG_EXCHANGES] = {self.exchange_name: {}}
        self.config[CONFIG_CRYPTO_CURRENCIES] = {"Symbols": {CONFIG_CRYPTO_PAIRS: self.symbols}}

    def _load_timeframes_if_necessary(self):
        if self.use_all_available_timeframes:
            self._load_all_available_timeframes()
        self.config[CONFIG_TIME_FRAME] = self.time_frames

    async def _create_description(self):
        await self.database.insert(DataTables.DESCRIPTION,
                                   timestamp=time.time(),
                                   version=self.VERSION,
                                   exchange=self.exchange_name,
                                   symbols=json.dumps(self.symbols),
                                   time_frames=json.dumps([tf.value for tf in self.time_frames]))

    async def save_ticker(self, timestamp, exchange, cryptocurrency, symbol, ticker, multiple=False):
        if not multiple:
            await self.database.insert(ExchangeDataTables.TICKER, timestamp,
                                       exchange_name=exchange, cryptocurrency=cryptocurrency,
                                       symbol=symbol, recent_trades=json.dumps(ticker))
        else:
            await self.database.insert_all(ExchangeDataTables.TICKER, timestamp,
                                           exchange_name=exchange, cryptocurrency=cryptocurrency,
                                           symbol=symbol, recent_trades=[json.dumps(t) for t in ticker])

    async def save_order_book(self, timestamp, exchange, cryptocurrency, symbol, asks, bids, multiple=False):
        if not multiple:
            await self.database.insert(ExchangeDataTables.ORDER_BOOK, timestamp,
                                       exchange_name=exchange, cryptocurrency=cryptocurrency, symbol=symbol,
                                       asks=json.dumps(asks), bids=json.dumps(bids))
        else:
            await self.database.insert_all(ExchangeDataTables.ORDER_BOOK, timestamp,
                                           exchange_name=exchange, cryptocurrency=cryptocurrency, symbol=symbol,
                                           asks=[json.dumps(a) for a in asks],
                                           bids=[json.dumps(b) for b in bids])

    async def save_recent_trades(self, timestamp, exchange, cryptocurrency, symbol, recent_trades, multiple=False):
        if not multiple:
            await self.database.insert(ExchangeDataTables.RECENT_TRADES, timestamp,
                                       exchange_name=exchange, cryptocurrency=cryptocurrency,
                                       symbol=symbol, recent_trades=json.dumps(recent_trades))
        else:
            await self.database.insert_all(ExchangeDataTables.RECENT_TRADES, timestamp,
                                           exchange_name=exchange, cryptocurrency=cryptocurrency,
                                           symbol=symbol, recent_trades=[json.dumps(rt) for rt in recent_trades])

    async def save_ohlcv(self, timestamp, exchange, cryptocurrency, symbol, time_frame, candle, multiple=False):
        if not multiple:
            await self.database.insert(ExchangeDataTables.OHLCV, timestamp,
                                       exchange_name=exchange, cryptocurrency=cryptocurrency,
                                       symbol=symbol, time_frame=time_frame.value,
                                       candle=json.dumps(candle))
        else:
            await self.database.insert_all(ExchangeDataTables.OHLCV, timestamp=timestamp,
                                           exchange_name=exchange, cryptocurrency=cryptocurrency,
                                           symbol=symbol, time_frame=time_frame.value,
                                           candle=[json.dumps(c) for c in candle])

    async def save_kline(self, timestamp, exchange, cryptocurrency, symbol, time_frame, kline, multiple=False):
        if not multiple:
            await self.database.insert(ExchangeDataTables.KLINE, timestamp,
                                       exchange_name=exchange, cryptocurrency=cryptocurrency,
                                       symbol=symbol, time_frame=time_frame.value,
                                       candle=json.dumps(kline))
        else:
            await self.database.insert_all(ExchangeDataTables.KLINE, timestamp=timestamp,
                                           exchange_name=exchange, cryptocurrency=cryptocurrency,
                                           symbol=symbol, time_frame=time_frame.value,
                                           candle=[json.dumps(kl) for kl in kline])
