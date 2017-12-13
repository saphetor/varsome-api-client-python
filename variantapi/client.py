import logging

import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError, RequestException

# Set DEBUG variable to affect certain parameters
_debug = False


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
    _api_url = 'https://api.varsome.com' if not _debug else 'https://dev-api.varsome.com'
    _accepted_methods = ('GET', 'POST')

    def __init__(self, api_key=None):
        self.api_key = api_key
        self._headers = {'Accept': 'application/json'}
        if self.api_key is not None:
            self._headers['Authorization'] = "Token " + self.api_key
        self.session = requests.Session()
        self.session.headers.update(self._headers)

    def _make_request(self, path, method="GET", params=None, json_data=None):
        if method not in self._accepted_methods:
            raise VariantApiException('', "Unsupported method %s" % method)
        try:
            if method == "GET":
                r = self.session.get(self._api_url + path, params=params)
            if method == "POST":
                r = self.session.post(self._api_url + path, params=params, json=json_data,
                                      headers={'Content-Type': 'application/json'} if json_data is not None else None)
                logging.debug('Time between request and response %s' % r.elapsed)
                logging.debug('Content length %s' % len(r.content))
            if r.status_code in VariantApiException.ERROR_CODES:
                raise VariantApiException(
                    r.status_code,
                    r.json()['detail']
                    if r.headers['Content-Type'] == "application/json" else None)
            return r
        except HTTPError as e:
            raise VariantApiException('', "Unknown http error %s" % e)
        except Timeout as e:
            raise VariantApiException('', "Request timed out %s" % e)
        except ConnectionError as e:
            raise VariantApiException('', "Connection failure or connection refused %s" % e)
        except RequestException as e:
            raise VariantApiException('', "Unknown error %s" % e.response)

    def get(self, path, params=None):
        response = self._make_request(path, "GET", params=params)
        return response.json()

    def post(self, path, params=None, json_data=None):
        response = self._make_request(path, "POST", params=params, json_data=json_data)
        return response.json()


class VariantAPIClient(VariantAPIClientBase):
    schema_lookup_path = "/lookup/schema/"
    lookup_path = "/lookup/%s/%s"
    batch_lookup_path = "/lookup/batch/%s"

    def __init__(self, api_key=None, max_variants_per_batch=200):
        super(VariantAPIClient, self).__init__(api_key)
        self.max_variants_per_batch = max_variants_per_batch

    def schema(self):
        return self.get(self.schema_lookup_path)

    def lookup(self, query, params=None, ref_genome='hg19'):
        """

        :param query: variant representation
        :param params: dictionary of key value pairs for http GET parameters. Refer to the api documentation
        of https://api.varsome.com for examples
        :param ref_genome: reference genome (hg19 or hg38)
        :return:dictionary of annotations. refer to https://api.varsome.com/lookup/schema for dictionary properties
        """
        return self.get(self.lookup_path % (query, ref_genome), params=params)

    def batch_lookup(self, variants, params=None, ref_genome='hg19'):
        """

        :param variants: list of variant representations
        :param params: dictionary of key value pairs for http GET parameters. Refer to the api documentation
        of https://api.varsome.com for examples
        :param ref_genome: reference genome (hg19 or hg38)
        :return: list of dictionaries with annotations per variant refer to https://api.varsome.com/lookup/schema
        for dictionary properties
        """
        results = []
        for queries in [variants[x:x + self.max_variants_per_batch] for x in range(0, len(variants),
                                                                                   self.max_variants_per_batch)]:
            data = self.post(self.batch_lookup_path % ref_genome, params=params, json_data={'variants': queries})
            results.extend(data)
        return results
