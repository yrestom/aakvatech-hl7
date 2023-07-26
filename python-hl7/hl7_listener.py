# Using the third party `aiorun` instead of the `asyncio.run()` to avoid
# boilerplate.
import aiorun
import asyncio
import local_config as config
import requests
from datetime import datetime
import json
import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
import pickledb

import hl7
from hl7.mllp import start_hl7_server


async def process_hl7_messages(hl7_reader, hl7_writer):
    """This will be called every time a socket connects
    with us.
    """

    peername = hl7_writer.get_extra_info("peername")
    print(f"Connection established {peername}")

    # Retrieve the identifier associated with this server instance.
    identifier = hl7_writer.get_extra_info("identifier")

    try:

        # We're going to keep listening until the writer
        # is closed. Only writers have closed status.
        while not hl7_writer.is_closing():
            hl7_message = await hl7_reader.readmessage()
            str_hl7_message = str(hl7_message).replace('\r', '\n')
            msg_lines = str_hl7_message.splitlines()
            message = {
                "machine_make": msg_lines[0].split('|')[3],
                "machine_model": msg_lines[0].split('|')[2],
                "lab_test_name": msg_lines[3].split('|')[3],
                "message": str_hl7_message,
                "machine_id": identifier
            }
            send_to_erpnext(message, str(datetime.now()))
            # Now let's send the ACK and wait for the
            # writer to drain
            hl7_writer.writemessage(hl7_message.create_ack())

            await hl7_writer.drain()
    except asyncio.IncompleteReadError:
        # Oops, something went wrong, if the writer is not
        # closed or closing, close it.
        if not hl7_writer.is_closing():
            hl7_writer.close()
            await hl7_writer.wait_closed()
    print(f"Connection closed {peername}")


async def main():
    try:
        # Define a list of ports and identifiers.
        # Each tuple contains (port, identifier) pairs.
        ports_and_identifiers = [(5600, "Port_1"), (5601, "Port_2"), (5602, "Port_3")]

        # Create a list of tasks for each port.
        tasks = [start_hl7_server(process_hl7_messages, port=port) for port, _ in ports_and_identifiers]

        # Start all the servers concurrently.
        async with asyncio.gather(*tasks) as hl7_servers:
            # Associate each server instance with its identifier using a closure.
            for server, (_, identifier) in zip(hl7_servers, ports_and_identifiers):
                server.identifier = identifier

            # And now we serve forever. Or until we are cancelled...
            await asyncio.gather(*[server.serve_forever() for server in hl7_servers])
    except asyncio.CancelledError:
        # Cancelled errors are expected
        pass
    except Exception:
        print("Error occurred in main")


def send_to_erpnext(message, timestamp):
    """
    Example: send_to_erpnext(<<messge object with hl7 message>>,datetime.datetime.now())
    """
    url = config.ERPNEXT_URL + "/api/resource/Lab Machine Message"
    headers = {
        "Authorization": "token " + config.ERPNEXT_API_KEY + ":" + config.ERPNEXT_API_SECRET,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    data = {
        "date_and_time": timestamp,
        "machine_make": message.get("machine_make"),
        "machine_model": message.get("machine_model"),
        "lab_test_name": message.get("lab_test_name"),
        "message": message.get("message")
    }
    print(data)
    response = requests.request("POST", url, headers=headers, data=json.dumps(data))

    EMPLOYEE_NOT_FOUND_ERROR_MESSAGE = "No Employee found for the given employee field value."
    error_logger = setup_logger('error_logger', '/'.join([config.LOGS_DIRECTORY, 'error.log']), logging.ERROR)

    if response.status_code == 200:
        return 200, json.loads(response._content)['data']['name']
    else:
        error_str = _safe_get_error_str(response)
        if EMPLOYEE_NOT_FOUND_ERROR_MESSAGE in error_str:
            error_logger.error('\t'.join(['Error during ERPNext API Call.', str(message.get("machine_model")), timestamp, str(message.get("lab_test_name")), error_str]))
            # TODO: send email?
        else:
            error_logger.error('\t'.join(['Error during ERPNext API Call.', str(message.get("machine_model")), timestamp, str(message.get("lab_test_name")), error_str]))
        return response.status_code, error_str


def _safe_get_error_str(res):
    try:
        error_json = json.loads(res._content)
        if 'exc' in error_json:  # this means traceback is available
            error_str = json.loads(error_json['exc'])[0]
        else:
            error_str = json.dumps(error_json)
    except:
        error_str = str(res.__dict__)
    return error_str


def setup_logger(name, log_file, level=logging.INFO, formatter=None):

    if not formatter:
        formatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=50)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger


aiorun.run(main(), stop_on_unhandled_errors=True)
