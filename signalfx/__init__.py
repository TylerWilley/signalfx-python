# Copyright (C) 2015 SignalFx, Inc. All rights reserved.

import json
import logging
import os
import requests

DEFAULT_API_ENDPOINT_URL = 'https://api.signalfx.com/v1'
DEFAULT_INGEST_ENDPOINT_URL = 'https://ingest.signalfx.com/v2'


class __BaseSignalFx(object):

    def __init__(self, api_token=None, api_endpoint=DEFAULT_API_ENDPOINT_URL,
                 ingest_endpoint=DEFAULT_INGEST_ENDPOINT_URL, timeout=1):
        self._api_token = api_token
        self._api_endpoint = api_endpoint
        self._ingest_endpoint = ingest_endpoint
        self._timeout = timeout

    def send(self, gauges=None, counters=None):
        if not gauges and not counters:
            return None

        # TODO: switch to protocol buffers.
        data = {'gauge': gauges, 'counter': counters}
        logging.debug('Sending to SignalFx: %s', data)
        return data

    def send_event(self, event_type, dimensions=None, properties=None):
        data = {'eventType': event_type,
                'dimensions': dimensions or {},
                'properties': properties or {}}
        logging.debug('Sending event to SignalFx: %s', data)
        return data


SignalFxLoggingStub = __BaseSignalFx


class SignalFx(__BaseSignalFx):
    """SignalFx API client.

    This class presents a programmatic interface to SignalFx's metadata and
    ingest APIs. At the time being, only ingest is supported; more will come
    later.
    """

    def __init__(self, api_token, api_endpoint=DEFAULT_API_ENDPOINT_URL,
                 ingest_endpoint=DEFAULT_INGEST_ENDPOINT_URL, timeout=1):
        super(SignalFx, self).__init__(
            api_token, api_endpoint, ingest_endpoint, timeout)
        self._session = requests.Session()
        self._session.headers.update({
            'Content-Type': 'application/json',
            'X-SF-Token': self._api_token
        })
        self._session.verify = True

    def _post(self, endpoint, data):
        return self._session.post(
            endpoint,
            data=json.dumps(data),
            timeout=self._timeout)

    def send(self, gauges=None, counters=None):
        """Send the given metrics to SignalFx.

        Args:
            gauges (list): a list of dictionaries representing the gauges to
                report.
            counters (list): a list of dictionaries representing the counters
                to report.
        """
        data = super(SignalFx, self).send(gauges, counters)
        if not data:
            return None

        return self._post(
            os.path.join(self._ingest_endpoint, 'datapoint'),
            data)

    def send_event(self, event_type, dimensions=None, properties=None):
        """Send an event to SignalFx.

        Args:
            event_type (string): the event type (name of the event time
                series).
            dimensions (dict): a map of event dimensions.
            properties (dict): a map of extra properties on that event.
        """
        data = super(SignalFx, self).send_event(
            event_type, dimensions, properties)
        if not data:
            return None

        return self._post(
            os.path.join(self._api_endpoint, 'event'),
            data)