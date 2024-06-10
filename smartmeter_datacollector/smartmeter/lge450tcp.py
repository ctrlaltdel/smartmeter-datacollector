#
# Copyright (C) 2024 Supercomputing Systems AG
# This file is part of smartmeter-datacollector.
#
# SPDX-License-Identifier: GPL-2.0-only
# See LICENSES/README.md for more information.
#
import logging
from typing import Optional

from .cosem import Cosem
from .meter import MeterError, TCPHdlcDlmsMeter
from .reader import ReaderError
from .tcp_reader import TCPConfig

LOGGER = logging.getLogger("smartmeter")


class LGE450TCP(TCPHdlcDlmsMeter):
    def __init__(self, host: str, port: str,
                 decryption_key: Optional[str] = None,
                 use_system_time: bool = False) -> None:
        tcp_config = TCPConfig(
            host=host,
            port=port,
            termination=TCPHdlcDlmsMeter.HDLC_FLAG
        )
        cosem = Cosem(fallback_id=port)
        try:
            super().__init__(tcp_config, cosem, decryption_key, use_system_time)
        except ReaderError as ex:
            LOGGER.fatal("Unable to setup TCP reader for L+G E450. '%s'", ex)
            raise MeterError("Failed setting up L+G E450.") from ex

        LOGGER.info("Successfully set up L+G E450 smart meter on '%s:%s'.", host, port)
