import socket
from tld import get_tld
from cymruwhois import Client

"""
    Fetches website network information
    This class fetches URLs network information such as Cymru/whois information.
"""

class FetchNetworkInfo:
    def __init__(self, candidate, protocol):
        self._cymru_data = {}
        self.protocol = protocol
        self.candidate = self._clean_candidate(candidate)
        self.domain = "{}{}".format(self.protocol, self.candidate)
        self.ip = self._get_ip_from_domain()
        self.cymru = Client()

    def _clean_candidate(self, _candidate):
        if "http://" in _candidate:
            _candidate = _candidate.replace("http://", "")
        if "https://" in _candidate:
            _candidate = _candidate.replace("https://", "")

        if "www." in _candidate:
            _candidate = _candidate.replace("www.", "")

        if "/" in _candidate:
            splitter = _candidate.split("/")
            if len(splitter) > 1:
                return "{}".format(splitter[0])
        return _candidate

    def _get_tld_info(self):
        try:
            res = get_tld(self.domain, as_object=True, fail_silently=True)
            self._cymru_data['domain'] = res.domain
            self._cymru_data['subdomain'] = res.subdomain
            self._cymru_data['tld'] = res.tld

        except Exception as ex:
            print("Unable to fetch tld info .. {}".format(ex))

    def _get_ip_from_domain(self):
        try:
            return socket.gethostbyname(self.candidate)
        except Exception as ex:
            print("Exception occurred in fetching ip from domain {}".format(ex))
        return None

    def _get_cymru_info_from_ip(self):
        if self.ip is None:
            return None

        self._get_tld_info()

        try:
            req = self.cymru.lookup(self.ip)
            self._cymru_data['asn'] = req.asn
            self._cymru_data['ip'] = req.ip
            self._cymru_data['owner'] = req.owner
            self._cymru_data['prefix'] = req.prefix
            self._cymru_data['cc'] = req.cc

        except Exception as ex:
            print("Exception occurred in cymru fetch information {}".format(ex))

        return self._cymru_data

    def get_data(self):
        self._get_cymru_info_from_ip()
        return self._cymru_data
