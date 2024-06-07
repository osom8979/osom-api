# -*- coding: utf-8 -*-

from typing import Final

MQ_ROOT_PATH: Final[str] = "/osom/api"
"""
Key prefix of message queue used in osom-api project.
"""

MQ_REQUEST_PATH: Final[str] = "/osom/api/request"
"""
This is the base path for sending request commands to a specific worker.
You typically append the worker's name to this path as a subkey.

The final format will look like '/osom/api/request/{worker_name}',
and it uses a FIFO (First In, First Out) Queue.
"""

MQ_RESPONSE_PATH: Final[str] = "/osom/api/response"
"""
This is the base path for sending response commands related to specific requests.
You typically append the unique ID (uuid) of the message to this path as a subkey.

The final format will look like '/osom/api/response/{msg_uuid}',
and the data type is a String.
"""

MQ_BROADCAST_PATH: Final[str] = "/osom/api/broadcast"

MQ_REGISTER_PATH: Final[str] = "/osom/api/register"
MQ_REGISTER_WORKER_PATH: Final[str] = "/osom/api/register/worker"
MQ_REGISTER_WORKER_REQUEST_PATH: Final[str] = "/osom/api/register/worker/request"

MQ_UNREGISTER_PATH: Final[str] = "/osom/api/unregister"
MQ_UNREGISTER_WORKER_PATH: Final[str] = "/osom/api/unregister/worker"
