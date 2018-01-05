import logging
import asyncio
import concurrent.futures
import re
import os
import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError, RequestException


class VariantApiException(Exception):
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
            self.ERROR_CODES.get(self.status, 'Unknown error.') if self.response is None else self.response)

    def __repr__(self):
        return "%s(status=%s)" % (self.__class__.__name__, self.status)


class VariantAPIClientBase(object):
    _api_url = 'https://api.varsome.com'
    _accepted_methods = ('GET', 'POST')

    def __init__(self, api_key=None, logger=None):
        if logger is None:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch = logging.FileHandler(os.path.join(BASE_DIR, 'output.log'))
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        self.logger = logger
        self.api_key = api_key
        self._headers = {'Accept': 'application/json', 'user-agent': 'VarSomeApiClientPython/2.0'}
        if self.api_key is not None:
            self._headers['Authorization'] = "Token " + self.api_key
        self.session = requests.Session()
        self.session.headers.update(self._headers)

    def _make_request(self, path, method="GET", params=None, json_data=None):
        if method not in self._accepted_methods:
            raise VariantApiException('', "Unsupported method %s" % method)
        try:
            if method == "GET":
                r = self.session.get(self._api_url + path, params=params, stream=True)
            if method == "POST":
                if json_data is None:
                    raise RuntimeError("You need to provide a post request body")
                r = self.session.post(self._api_url + path, params=params, json=json_data,
                                      headers={'Content-Type': 'application/json'}, stream=True)
                self.logger.info('Time between request and response %s' % r.elapsed)
                self.logger.info('Content length %s' % len(r.content))
            r.raise_for_status()
            return r
        except HTTPError as e:
            response = e.response
            if response.status_code in VariantApiException.ERROR_CODES:
                error_message = "Unexpected error"
                if r.headers['Content-Type'] == "application/json":
                    error_message = response.json().get("detail", None)
                raise VariantApiException(response.status_code, error_message)
            raise VariantApiException('', "Unknown http error %s" % e)
        except Timeout as e:
            raise VariantApiException('', "Request timed out %s" % e)
        except ConnectionError as e:
            raise VariantApiException('', "Connection failure or connection refused %s" % e)
        except RequestException as e:
            raise VariantApiException('', "Unknown error %s" % e)

    def get(self, path, params=None):
        response = self._make_request(path, "GET", params=params)
        return response.json()

    def post(self, path, params=None, json_data=None, raise_exceptions=False):
        # handle api errors in batch requests.
        try:
            response = self._make_request(path, "POST", params=params, json_data=json_data)
            return response.json()
        except VariantApiException as e:
            if raise_exceptions:
                raise e
            self.logger.error(e)
            return {'error': str(e)}


class VariantAPIClient(VariantAPIClientBase):
    schema_lookup_path = "/lookup/schema"
    lookup_path = "/lookup/%s"
    ref_genome_lookup_path = lookup_path + "/%s"
    batch_lookup_path = "/lookup/batch/%s"

    def __init__(self, api_key=None, max_variants_per_batch=200):
        super(VariantAPIClient, self).__init__(api_key)
        self.max_variants_per_batch = max_variants_per_batch

    def query_is_variant_id(self, query):
        """
        Query may be a variat identifier developed by Saphetor
        :param query:
        :return:
        """
        return re.search(r'^\d{20}$', str(query))

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

    def batch_lookup(self, variants, params=None, ref_genome='hg19', max_threads=3, raise_exceptions=False):
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
        results = []

        async def batch(executor):
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(
                    executor,
                    self.post,
                    self.batch_lookup_path % ref_genome, params, {'variants': queries}, raise_exceptions
                )
                for queries in [variants[x:x + self.max_variants_per_batch] for x in range(0, len(variants),
                                                                                           self.max_variants_per_batch)]
            ]
            for response in await asyncio.gather(*futures):
                results.extend(response)
        # Create a limited thread pool.
        executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=max_threads,
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(batch(executor))
        return results
