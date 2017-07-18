import logging

import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError, RequestException

# Set DEBUG variable to affect ceertain parameters
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

    _api_url = 'https://api.varsome.com' if _debug == False else 'https://dev-api.varsome.com'
    _accepted_methods = ('GET', 'POST')

    def __init__(self, api_key=None):
        self.api_key = api_key
        self._headers = {'Accept': 'application/json'}
        if self.api_key is not None:
            self._headers['Authorization'] = "Token " + self.api_key
        self.session = requests.Session()
        self.session.headers.update(self._headers)

    def _make_request(self, path, method="GET", data=None, json_data=None):
        if method not in self._accepted_methods:
            raise VariantApiException('', "Unsupported method %s" % method)
        try:
            if method == "GET":
                r = self.session.get(self._api_url + path, data=data)
            if method == "POST":
                r = self.session.post(self._api_url + path, data=data, json=json_data,
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

    def get(self, path, data=None):
        response = self._make_request(path, "GET", data=data)
        return response.json()

    def post(self, path, data=None, json_data=None):
        response = self._make_request(path, "POST", data=data, json_data=json_data)
        return response.json()


class VariantAPIClient(VariantAPIClientBase):
    schema_lookup_path = "/lookup/schema/"
    lookup_path = "/lookup/%s/%s"
    batch_lookup_path = "/lookup/batch/%s"
    _max_variants_per_batch = 1000

    def __init__(self, api_key=None):
        super(VariantAPIClient, self).__init__(api_key)

    def schema(self):
        return self.get(self.schema_lookup_path)

    def lookup(self, query, ref_genome=1019):
        return self.get(self.lookup_path % (query, ref_genome))

    def batch_lookup(self, variants, ref_genome=1019):
        results = []
        for queries in [variants[x:x + self._max_variants_per_batch] for x in range(0, len(variants),
                                                                                    self._max_variants_per_batch)]:
            data = self.post(self.batch_lookup_path % ref_genome, json_data={'variants': queries})
            results.extend(data)
        return results
