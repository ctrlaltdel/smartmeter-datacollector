#
# Copyright (C) 2024 Supercomputing Systems AG
# This file is part of smartmeter-datacollector.
#
# SPDX-License-Identifier: GPL-2.0-only
# See LICENSES/README.md for more information.
#
from dataclasses import dataclass
from typing import Callable
import asyncio
import socket

from .reader import Reader, ReaderError


@dataclass
class TCPConfig:
    host: str
    port: int
    buffer_size: int = 1024
    termination: bytes = b'\n'
    reconnect_delay: int = 5  # Delay in seconds before attempting to reconnect


# pylint: disable=too-few-public-methods
class TCPReader(Reader):
    def __init__(self, tcp_config: TCPConfig, callback: Callable[[bytes], None]) -> None:
        super().__init__(callback)
        self._termination = tcp_config.termination
        self._host = tcp_config.host
        self._port = tcp_config.port
        self._buffer_size = tcp_config.buffer_size
        self._reconnect_delay = tcp_config.reconnect_delay

    async def start_and_listen(self) -> None:
        while True:
            try:
                # Attempt to establish a connection
                reader, writer = await asyncio.open_connection(self._host, self._port)
                while True:
                    data = await reader.readuntil(self._termination)
                    self._callback(data)
            except (OSError, ConnectionError) as ex:
                # Handle connection errors and attempt to reconnect
                print(f"Connection error: {ex}. Reconnecting in {self._reconnect_delay} seconds...")
                await asyncio.sleep(self._reconnect_delay)
                continue
            except asyncio.IncompleteReadError:
                # Handle read errors and attempt to reconnect
                print("Incomplete read error. Reconnecting...")
                await asyncio.sleep(self._reconnect_delay)
                continue
            finally:
                # Ensure the writer is closed if it was created
                if 'writer' in locals():
                    writer.close()
                    await writer.wait_closed()
