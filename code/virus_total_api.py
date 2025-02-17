from network_info import FetchNetworkInfo
from virus_total_apis import PublicApi as VirusTotalPublicApi
from db_util import MongoDBActor
from constants import COLLECTIONS, API_KEY

import os
import random
import shared_util
import whois
import argparse
import time

"""
    VirusTotal API for evaluating the URLs from each of the social medias that we study.
"""


class VTAPI:
    def __init__(self, _data_, flag):
        self._data_ = _data_
        self.flag = flag
        self.api_key = self._get_random_api_key()
        self.vt_client = VirusTotalPublicApi(self.api_key)

    def _get_random_api_key(self):
        _apis = [
            os.environ[API_KEY.VIRUS_TOTAL]
        ]
        if self.flag:
            if self.flag == 0:
                return _apis[0]
            elif self.flag % 2 == 0:
                return _apis[0]
            else:
                return _apis[1]
        else:
            return random.choice(_apis)

    def get_url_look_up(self):
        response = self.vt_client.get_url_report(self._data_, timeout=10)
        return response

    def get_domain_look_up(self):
        response = self.vt_client.get_domain_report(self._data_, timeout=10)
        return response

    def get_ip_report(self):
        response = self.vt_client.get_ip_report(self._data_, timeout=10)
        return response

    def get_file_look_up(self):
        response = self.vt_client.get_file_report(self._data_, timeout=10)
        return response

    def get_file_scan(self):
        response = self.vt_client.scan_file(self._data_, timeout=10)
        return response

    def get_url_scan(self):
        response = self.vt_client.scan_url(self._data_, timeout=10)
        return response


class APIProcessor:
    def __init__(self, function):
        self.function = function

    def process(self):
        if self.function == "process_twitter_posts_urls":
            self.process_twitter_posts_urls()
        elif self.function == "process_twitter_profile_urls":
            self.process_twitter_profile_urls()
        elif self.function == "process_facebook_profile_urls":
            self.process_facebook_profile_urls()
        elif self.function == "process_facebook_hash_tag_posts_urls":
            self.process_facebook_hash_tag_posts_urls()
        elif self.function == "process_facebook_single_posts_urls":
            self.process_facebook_single_posts_urls()
        elif self.function == "process_instagram_posts_urls":
            self.process_instagram_posts_urls()
        elif self.function == "process_instagram_profile_urls":
            self.process_instagram_profile_urls()
        elif self.function == "process_telegram_posts_urls":
            self.process_telegram_posts_urls()
        elif self.function == "process_telegram_profile_urls":
            self.process_telegram_profile_urls()
        elif self.function == "process_you_tube_posts_urls":
            self.process_you_tube_posts_urls()
        elif self.function == "process_you_tube_descriptive_link_from_profile":
            self.process_you_tube_descriptive_link_from_profile()
        elif self.function == "process_network_information_of_collected_urls":
            self.process_network_information_of_collected_urls()
        elif self.function == "process_who_is_information_of_collected_urls":
            self.process_who_is_information_of_collected_urls()

    def is_url_already_looked_up(self, _url):
        return len(
            set(MongoDBActor(COLLECTIONS.VT_LOOK_UP)
                .distinct(key="look_up_time", filter={"url": _url}))) > 0

    def _get_already_scanned_vt_url(self):
        _urls = set()
        for item in MongoDBActor(COLLECTIONS.VT_LOOK_UP).find():
            if 'url' in item:
                _urls.add(item['url'])
        return _urls

    def do_exclude_lists_of_urls(self, check_url):
        if check_url is None:
            return True
        check_url = check_url.lower()
        _lst = [
            "linktr.ee",
            "twitch.tv",
            "twitch.com",
            "youtube.com",
            "fb.com",
            "facebook.com",
            "twitterslink.com",
            "linkedin.com",
            "instagram.com",
            "youtu.be",
            "twitter.com",
            "telegram",
            "tiktok",
            "medium",
            "github.io",
            "imdb.com",
            "t.me",
            "x.com",
            "buymecoffee",
            "patreon"
        ]
        for _each in _lst:
            if _each in check_url:
                return True
        return False

    def process_twitter_profile_urls(self):
        all_profile_urls = set()
        _author_ids = set()
        for item in MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find({"is_donation_context_text": True}):
            if 'author_id' in item:
                _author_ids.add(item['author_id'])

        _all_found_urls = set()
        for count, author_id in enumerate(_author_ids):
            _expanded_url = set(MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).distinct(
                key="entities.url.urls.expanded_url",
                filter={
                    "author_id": author_id
                }))
            print("Adding {}/{}, {}".format(count, len(_author_ids), author_id))
            _all_found_urls = _all_found_urls.union(_expanded_url)
        if None in _all_found_urls:
            _all_found_urls.remove(None)
        added_cnt = 0
        for cnt, _e in enumerate(_all_found_urls):
            if self.do_exclude_lists_of_urls(_e):
                continue
            print("{}/{} Added after curating: {}".format(added_cnt, len(_all_found_urls), _e))
            all_profile_urls.add(_e)
            added_cnt = added_cnt + 1
        _additional_input = {"key": "entities.url.urls.expanded_url",
                             "collection": COLLECTIONS.TWITTER_USER_DETAIL,
                             "social_media": "twitter"
                             }
        _already_fetched = self._get_already_scanned_vt_url()
        _difference = all_profile_urls.difference(_already_fetched)
        self.process_vt_url_look_up(_difference, _additional_input)

    def process_twitter_posts_urls(self):
        three_keys = [
            "entities.urls.expanded_url",
            "entities.urls.unwound_url"]

        for each_key in three_keys:
            _db_url = set(MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(key=each_key,
                                                                                  filter={
                                                                                      "is_donation_context_text": True
                                                                                  }))
            if None in _db_url:
                _db_url.remove(None)
            _additional_input = {"key": each_key,
                                 "collection": COLLECTIONS.DONATION_TEXT_SEARCH,
                                 "social_media": "twitter"
                                 }
            _already_fetched = self._get_already_scanned_vt_url()
            _difference = _db_url.difference(_already_fetched)
            self.process_vt_url_look_up(_difference, _additional_input)

    def process_facebook_hash_tag_posts_urls(self):
        three_keys = ["may_be_url"]

        for each_key in three_keys:
            _db_url = set(MongoDBActor(COLLECTIONS.FACEBOOK_HASH_TAG_SEARCH).distinct(key=each_key,
                                                                                      filter={
                                                                                          "is_donation_context_text": True
                                                                                      }))
            if None in _db_url:
                _db_url.remove(None)
            _additional_input = {"key": each_key,
                                 "collection": COLLECTIONS.FACEBOOK_HASH_TAG_SEARCH,
                                 "social_media": "facebook"
                                 }
            _already_fetched = self._get_already_scanned_vt_url()
            _difference = _db_url.difference(_already_fetched)
            self.process_vt_url_look_up(_difference, _additional_input)

    def process_facebook_single_posts_urls(self):
        three_keys = ["may_be_url"]

        for each_key in three_keys:
            _db_url = set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).distinct(key=each_key,
                                                                                  filter={
                                                                                      "is_donation_context_text": True
                                                                                  }))
            if None in _db_url:
                _db_url.remove(None)
            _additional_input = {"key": each_key,
                                 "collection": COLLECTIONS.FACEBOOK_SINGLE_POST,
                                 "social_media": "facebook"
                                 }
            _already_fetched = self._get_already_scanned_vt_url()
            _difference = _db_url.difference(_already_fetched)
            self.process_vt_url_look_up(_difference, _additional_input)

    def process_instagram_posts_urls(self):
        three_keys = ["may_be_url"]

        for each_key in three_keys:
            _db_url = set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).distinct(key=each_key))
            if None in _db_url:
                _db_url.remove(None)
            _additional_input = {"key": each_key,
                                 "collection": COLLECTIONS.INSTAGRAM_SINGLE_POST,
                                 "social_media": "instagram"
                                 }
            _already_fetched = self._get_already_scanned_vt_url()
            _difference = _db_url.difference(_already_fetched)
            self.process_vt_url_look_up(_difference, _additional_input)

    def process_instagram_profile_urls(self):
        _already_fetched = self._get_already_scanned_vt_url()
        _db_url = set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).distinct(key="externalUrl"))
        if None in _db_url:
            _db_url.remove(None)
        _len = len(_db_url)
        _additional_input = {"key": "externalUrl",
                             "collection": COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA,
                             "social_media": "instagram"
                             }
        _difference = _db_url.difference(_already_fetched)
        self.process_vt_url_look_up(_difference, _additional_input)

    def process_telegram_posts_urls(self):
        three_keys = ["may_be_url"]

        for each_key in three_keys:
            _db_url = set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(key=each_key,
                                                                                  filter={
                                                                                      "is_donation_context_text": True}))
            if None in _db_url:
                _db_url.remove(None)
            _additional_input = {"key": each_key,
                                 "collection": COLLECTIONS.TELEGRAM_SINGLE_POST,
                                 "social_media": "telegram"
                                 }
            _already_fetched = self._get_already_scanned_vt_url()
            _difference = _db_url.difference(_already_fetched)
            self.process_vt_url_look_up(_difference, _additional_input)

    def process_telegram_profile_urls(self):
        _author_db_url = set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(key="telemtr_url",
                                                                                     filter={
                                                                                         "is_donation_context_text": True}))
        for cnt, each_authr in enumerate(_author_db_url):
            print("Processing {}/{}, {}".format(cnt, len(_author_db_url), each_authr))
            process_vt_urls = set(
                MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).distinct(
                    key="profile_data.channel_description.profile_links",
                    filter={"telemtr_url": each_authr}))

            if None in process_vt_urls:
                process_vt_urls.remove(None)
            if len(process_vt_urls) == 0:
                continue
            print("Before exclude Total URLs found:{}, {}".format(len(process_vt_urls), list(process_vt_urls)))

            _additional_input = {"key": "profile_data.channel_description.profile_links",
                                 "collection": COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH,
                                 "social_media": "telegram"
                                 }
            _already_fetched = self._get_already_scanned_vt_url()
            to_exclude = set()
            for _each in process_vt_urls:
                if self.do_exclude_lists_of_urls(_each):
                    to_exclude.add(_each)
            _difference = process_vt_urls.difference(_already_fetched)
            _difference = _difference.difference(to_exclude)
            print("After exclude Total URLs found:{}, {}".format(len(process_vt_urls), list(process_vt_urls)))
            print("Processing vt after exclude:{}".format(list(_difference)))
            self.process_vt_url_look_up(_difference, _additional_input)

    def process_you_tube_posts_urls(self):
        three_keys = ["may_be_url"]

        for each_key in three_keys:
            _db_url = set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(key=each_key,
                                                                                    filter={
                                                                                        "is_donation_context_text": True}))
            if None in _db_url:
                _db_url.remove(None)
            _additional_input = {"key": each_key,
                                 "collection": COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH,
                                 "social_media": "youtube"
                                 }
            _already_fetched = self._get_already_scanned_vt_url()
            _difference = _db_url.difference(_already_fetched)
            self.process_vt_url_look_up(_difference, _additional_input)

    def process_you_tube_descriptive_link_from_profile(self):
        three_keys = ["descriptionLinks.url"]

        for each_key in three_keys:
            _db_url = set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(key=each_key,
                                                                                    filter={
                                                                                        "is_donation_context_text": True}))
            if None in _db_url:
                _db_url.remove(None)

            _curate = set()

            for _e in _db_url:
                if 'youtube.com' in _e:
                    continue
                _curate.add(_e)

            _additional_input = {"key": each_key,
                                 "collection": COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH,
                                 "social_media": "youtube"
                                 }
            _already_fetched = self._get_already_scanned_vt_url()
            _difference = _curate.difference(_already_fetched)
            self.process_vt_url_look_up(_difference, _additional_input)

    def process_facebook_profile_urls(self):
        three_keys = ["website"]

        for each_key in three_keys:
            _db_url = set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).distinct(key=each_key))
            if None in _db_url:
                _db_url.remove(None)
            _additional_input = {"key": each_key,
                                 "collection": COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE,
                                 "social_media": "facebook"
                                 }
            _already_fetched = self._get_already_scanned_vt_url()
            _difference = _db_url.difference(_already_fetched)

            _curated = set()
            for _d in _difference:
                if 'facebook' in _d.lower() or 'fb.' in _d.lower():
                    continue
                _curated.add(_d)

            self.process_vt_url_look_up(_curated, _additional_input)

    def process_vt_url_look_up(self, _db_url, _additional_input):
        for count, each_url in enumerate(_db_url):
            print("Processing VT request, twitter urls {}/{}, {}".format(count, len(_db_url), each_url))
            if self.is_url_already_looked_up(each_url):
                print("Already processed ... {}".format(each_url))
                continue

            if 'https://twitter.com' in each_url:
                print("Escaping twitter url ... {}".format(each_url))
                continue
            try:
                _look_up_data = VTAPI(each_url, flag=count).get_url_look_up()
                if 'error' in _look_up_data:
                    break
                MongoDBActor(COLLECTIONS.VT_LOOK_UP).find_and_modify(key={"url": each_url}, data={
                    'url': each_url,
                    'look_up_time': int(time.time() * 1000),
                    'results': _look_up_data['results'],
                    'additional_info': _additional_input
                })
                time.sleep(0.25)
            except Exception as ex:
                print("{}".format(ex))

    def process_who_is_information_of_collected_urls(self):
        _domains = []
        for item in MongoDBActor(COLLECTIONS.VT_LOOK_UP).find({"network_info.domain": {"$exists": True}}):
            if 'network_info' not in item:
                continue
            _network_info = item['network_info']
            if 'domain' not in _network_info:
                continue
            if 'tld' not in _network_info:
                continue
            _domains.append((_network_info['domain'], _network_info['tld']))

        for domain in _domains:
            print("Processing {}.{}".format(domain[0], domain[1]))
            try:
                domain_name = "{}.{}".format(domain[0], domain[1])
                who_is = whois.whois(domain_name)
                expiration = str(who_is.w.expiration_date)
                creation_date = str(who_is.creation_date)
                registar = who_is.registrar

                _all_data = {
                    'domain_expiration': expiration,
                    'domain_creation': creation_date,
                    'domain_registar': registar,
                    'domain_full_tld': domain_name
                }
                MongoDBActor(COLLECTIONS.VT_LOOK_UP).find_and_modify(key={"network_info.domain": domain[0]},
                                                                     data=_all_data
                                                                     )
            except Exception as ex:
                print("Exception found {}".format(ex))

    def process_network_information_of_collected_urls(self):
        _mega_tables = shared_util.get_all_collections()
        for each_table in _mega_tables:
            print("Processing {}".format(each_table))
            vt_urls = shared_util.get_mega_collection_fraud_urls(each_table)
            for each_url in vt_urls:
                is_already_processed = len(set(MongoDBActor(COLLECTIONS.VT_LOOK_UP).distinct(key="url",
                                                                                             filter={'host_name': {
                                                                                                 "$exists": True},
                                                                                                 "url": each_url
                                                                                             }
                                                                                             ))) > 0
                if is_already_processed:
                    print("Already processed ... {}".format(each_url))
                    continue

                if "http://" in each_url:
                    protocol = "http://"
                else:
                    protocol = "https://"
                _all_data = {}
                try:
                    network_info = FetchNetworkInfo(each_url, protocol).get_data()
                    if 'ip' not in network_info:
                        _all_data['has_network_error'] = True
                        _all_data['host_name'] = []
                        _all_data['certificate'] = {}
                    else:
                        ip_address = network_info['ip']
                        if not ip_address:
                            continue

                        _all_data['network_info'] = network_info

                    print(_all_data)
                    MongoDBActor(COLLECTIONS.VT_LOOK_UP).find_and_modify(key={"url": each_url},
                                                                         data=_all_data
                                                                         )
                except Exception as ex:
                    print("Exception found {}".format(ex))


if __name__ == "__main__":
    _arg_parser = argparse.ArgumentParser(description="VT Processor")
    _arg_parser.add_argument("-f", "--function_name",
                             action="store",
                             required=True,
                             help="function_name")

    _arg_value = _arg_parser.parse_args()

    _dc = APIProcessor(_arg_value.function_name)
    _dc.process()
