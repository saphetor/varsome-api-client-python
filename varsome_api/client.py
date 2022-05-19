# Copyright 2018 Saphetor S.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import concurrent.futures
import logging
import os
import re
from itertools import chain

import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError, RequestException


class VarSomeAPIException(Exception):
    ERROR_CODES = {
        400: "Bad request. A parameter you have passed is not valid, or something in your request is wrong",
        401: "Not Authorized: either you need to provide authentication credentials, or the credentials provided aren't"
        " valid.",
        403: "Bad Request: your request is invalid, and we'll return an error message that tells you why. This is the "
        "status code returned if you've exceeded the rate limit (see below).",
        404: "Not Found: either you're requesting an invalid URI or the resource in question doesn't exist",
        500: "Internal Server Error: we did something wrong.",
        501: "Not implemented.",
        502: "Bad Gateway: returned if VariantAPI is down or being upgraded.",
        503: "Service Unavailable: the VariantAPI servers are up, but are overloaded with requests. Try again later.",
        504: "Gateway Timeout",
    }

    def __init__(self, status, response=None):
        self.status = status
        self.response = response

    def __str__(self):
        return "%s (%s)" % (
            self.status,
            self.ERROR_CODES.get(self.status, "Unknown error.")
            if self.response is None
            else self.response,
        )

    def __repr__(self):
        return "%s(status=%s)" % (self.__class__.__name__, self.status)


class VarSomeAPIClientBase(object):
    _api_url = "https://api.varsome.com"
    _accepted_methods = ("GET", "POST")

    def __init__(self, api_key=None, logger=None, api_url=None):
        if logger is None:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        if api_url is not None:
            self._api_url = api_url
        self.logger = logger
        self.api_key = api_key
        self._headers = {
            "Accept": "application/json",
            "user-agent": "VarSomeApiClientPython/2.0",
        }
        if self.api_key is not None:
            self._headers["Authorization"] = "Token " + self.api_key
        self.session = requests.Session()
        self.session.headers.update(self._headers)

    def _make_request(self, path, method="GET", params=None, json_data=None):
        if method not in self._accepted_methods:
            raise VarSomeAPIException("", "Unsupported method %s" % method)
        try:
            if method == "GET":
                r = self.session.get(self._api_url + path, params=params, stream=True)
            if method == "POST":
                if json_data is None:
                    raise RuntimeError("You need to provide a post request body")
                r = self.session.post(
                    self._api_url + path,
                    params=params,
                    json=json_data,
                    headers={"Content-Type": "application/json"},
                    stream=True,
                )
                self.logger.info("Time between request and response %s" % r.elapsed)
                self.logger.info("Content length %s" % len(r.content))
            r.raise_for_status()
            return r
        except HTTPError as e:
            response = e.response
            if response.status_code in VarSomeAPIException.ERROR_CODES:
                error_message = "Unexpected error"
                if r.headers["Content-Type"] == "application/json":
                    error_message = response.json().get("detail", None)
                raise VarSomeAPIException(response.status_code, error_message)
            raise VarSomeAPIException("", "Unknown http error %s" % e)
        except Timeout as e:
            raise VarSomeAPIException("", "Request timed out %s" % e)
        except ConnectionError as e:
            raise VarSomeAPIException(
                "", "Connection failure or connection refused %s" % e
            )
        except RequestException as e:
            raise VarSomeAPIException("", "Unknown error %s" % e)

    def get(self, path, params=None):
        response = self._make_request(path, "GET", params=params)
        return response.json()

    def post(self, path, params=None, json_data=None, raise_exceptions=True):
        # handle api errors in batch requests.
        try:
            response = self._make_request(
                path, "POST", params=params, json_data=json_data
            )
            return response.json()
        except VarSomeAPIException as e:
            if raise_exceptions:
                raise e
            self.logger.error(e)
            return [
                {
                    "error": "Could not annotate variant %s because "
                    "request failed with %s" % (variant, e)
                }
                for variant in json_data["variants"]
            ]


class VarSomeAPIClient(VarSomeAPIClientBase):
    schema_lookup_path = "/lookup/schema"
    lookup_path = "/lookup/%s"
    ref_genome_lookup_path = lookup_path + "/%s"
    batch_lookup_path = "/lookup/batch/%s"

    def __init__(
        self, api_key=None, logger=None, api_url=None, max_variants_per_batch=200
    ):
        super(VarSomeAPIClient, self).__init__(api_key, logger, api_url)
        self.max_variants_per_batch = max_variants_per_batch

    @staticmethod
    def query_is_variant_id(query):
        """
        Query may be a variat identifier developed by Saphetor
        :param query:
        :return:
        """
        return re.search(r"^\d{20}$", str(query))

    def schema(self):
        return self.get(self.schema_lookup_path)

    def lookup(self, query, params=None, ref_genome=None):
        """

        :param query: variant representation
        :param params: dictionary of key value pairs for http GET parameters. Refer to the api documentation
        of https://api.varsome.com for examples
        :param ref_genome: reference genome (hg19 or hg38 or None) default for requests with no ref genome is hg19
        :return:dictionary of annotations. refer to https://api.varsome.com/lookup/schema for dictionary properties
        """
        url = self.lookup_path % query
        if ref_genome is not None and not self.query_is_variant_id(query):
            url = self.ref_genome_lookup_path % (query, ref_genome)
        return self.get(url, params=params)

    def batch_lookup(
        self,
        variants,
        params=None,
        ref_genome="hg19",
        max_threads=3,
        raise_exceptions=False,
    ):
        """

        :param variants: list of variant representations
        :param params: dictionary of key value pairs for http GET parameters. Refer to the api documentation
        of https://api.varsome.com for examples
        :param ref_genome: reference genome (hg19 or hg38)
        :param max_threads: how many concurrent requests to make
        (max_variants_per_batch has to be less than len(variants) param to have any effect)
        :raise_exceptions: If a post request should raise an exception True, thus terminating the whole process or if it
        should proceed to let the process continue
        :return: list of dictionaries with annotations per variant refer to https://api.varsome.com/lookup/schema
        for dictionary properties
        """

        @asyncio.coroutine
        def batch(batch_executor):
            batch_loop = asyncio.get_event_loop()
            futures = [
                batch_loop.run_in_executor(
                    batch_executor,
                    self.post,
                    self.batch_lookup_path % ref_genome,
                    params,
                    {"variants": queries},
                    raise_exceptions,
                )
                for queries in [
                    variants[x : x + self.max_variants_per_batch]
                    for x in range(0, len(variants), self.max_variants_per_batch)
                ]
            ]
            responses = yield from asyncio.gather(*futures)
            return responses

        # Create a limited thread pool.
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_threads,
        )
        loop = asyncio.get_event_loop()
        return list(chain.from_iterable(loop.run_until_complete(batch(executor))))
