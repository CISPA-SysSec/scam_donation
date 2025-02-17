from constants import COLLECTIONS, API_KEY
from db_util import MongoDBActor

import json
import requests
import shared_util
import argparse
import time

"""
    Fetch Fraud Analysis of Email and Phone Numbers
    reference: 
        https://www.ipqualityscore.com/documentation/email-validation-api/overview
        https://www.ipqualityscore.com/documentation/phone-number-validation-api/overview
"""


class Validate(object):
    """
    Class for interacting with the IPQualityScore API.

    Attributes:
        key (str): Your IPQS API key.
        format (str): The format of the response. Default is 'json', but you can also use 'xml'.
        base_url (str): The base URL for the IPQS API.

    Methods:
        email_validation_api(email: str, timeout: int = 1, fast: str = 'false', abuse_strictness: int = 0) -> str:
            Returns the response from the IPQS Email Validation API.
    """

    key = None
    format = None
    base_url = None

    def __init__(self, key, format="json") -> None:
        self.key = key
        self.format = format
        self.base_url = f"https://www.ipqualityscore.com/api/{self.format}/"

    def email_validation_api(self, email: str, timeout: int = 7, fast: str = 'false', abuse_strictness: int = 0) -> str:
        """
        Returns the response from the IPQS Email Validation API.

        Args:
            email (str):
                The email you wish to validate.
            timeout (int):
                Set the maximum number of seconds to wait for a reply from an email service provider.
                If speed is not a concern or you want higher accuracy we recommend setting this in the 20 - 40 second range in some cases.
                Any results which experience a connection timeout will return the "timed_out" variable as true. Default value is 7 seconds.
            fast (str):
                If speed is your major concern set this to true, but results will be less accurate.
            abuse_strictness (int):
                Adjusts abusive email patterns and detection rates higher levels may cause false-positives (0 - 2).

        Returns:
            str: The response from the IPQS Email Validation API.
        """

        url = f"{self.base_url}email/{self.key}/{email}"

        params = {
            "timeout": timeout,
            "fast": fast,
            "abuse_strictness": abuse_strictness
        }

        response = requests.get(url, params=params)
        return response.json()

    def phone_number_api(self, phonenumber, vars: dict = {}) -> dict:
        url = 'https://www.ipqualityscore.com/api/json/phone/%s/%s' % (self.key, phonenumber)
        x = requests.get(url, params=vars)
        print(x.text)
        _res = json.loads(x.text)
        print(_res)
        return _res


class ProcessEmailVerification:
    def __init__(self, function, api_key, social_media):
        self.function = function
        self.api_key = int(api_key)
        self.social_media = social_media
        self.vt_urls = shared_util.get_vt_positive_url_from_social_media(self.social_media)

    def process(self):
        # start email process
        if self.function == "process_twitter_posts_emails":
            self.process_twitter_posts_keys('may_be_email')
        elif self.function == "process_instagram_posts_emails":
            self.process_instagram_posts_keys('may_be_email')
        elif self.function == "process_facebook_posts_emails":
            self.process_facebook_posts_keys('may_be_email')
        elif self.function == "process_facebook_profile_emails":
            self.process_facebook_profile_keys('email')
        elif self.function == "process_telegram_posts_emails":
            self.process_telegram_posts_keys('may_be_email')
        elif self.function == "process_you_tube_posts_emails":
            self.process_you_tube_posts_keys('may_be_email')
        # end email process

        # start phone number process
        elif self.function == "process_twitter_posts_phone_number":
            self.process_twitter_posts_keys('may_be_phone_number')
        elif self.function == "process_instagram_posts_phone_number":
            self.process_instagram_posts_keys('may_be_phone_number')
        elif self.function == "process_facebook_posts_phone_number":
            self.process_facebook_posts_keys('may_be_phone_number')
        elif self.function == "process_facebook_profile_phone_number":
            self.process_facebook_profile_keys('phone')
        elif self.function == "process_telegram_posts_phone_number":
            self.process_telegram_posts_keys('may_be_phone_number')
        elif self.function == "process_you_tube_posts_phone_number":
            self.process_you_tube_posts_keys('may_be_phone_number')
        # end phone number process

        # Note the free version  has 200 limit per day
        elif self.function == "process_email_requests":
            self.process_email_requests()
        elif self.function == "process_ipquality_score_phone_number_requests":
            self.process_ipquality_score_phone_number_requests()
        elif self.function == "get_abstract_api_phone_number_evaluation":
            self.get_abstract_api_phone_number_evaluation()

    def process_twitter_posts_keys(self, process_key):
        _all_keys = set()
        for item in MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find({
            process_key: {"$exists": True},
            "is_donation_context_text": True
        }):
            if process_key in item:
                _all_keys.add(item[process_key])
        if None in _all_keys:
            _all_keys.remove(None)
        if process_key == "may_be_email":
            for _e in _all_keys:
                MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).insert_data({"email": _e,
                                                                     "social_media": "twitter",
                                                                     "key": process_key,
                                                                     "collection": COLLECTIONS.DONATION_TEXT_SEARCH
                                                                     })
        elif process_key == "may_be_phone_number":
            for _e in _all_keys:
                MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).insert_data({"phone_number": _e,
                                                                            "social_media": "twitter",
                                                                            "key": process_key,
                                                                            "collection": COLLECTIONS.DONATION_TEXT_SEARCH
                                                                            })

    def process_instagram_posts_keys(self, process_key):
        _all_keys = set()
        for item in MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).find({
            process_key: {"$exists": True},
            "is_donation_context_text": True
        }):
            if process_key in item:
                _found = item[process_key]
                if _found:
                    for each in _found:
                        _all_keys.add(each)
        if None in _all_keys:
            _all_keys.remove(None)
        if process_key == "may_be_email":
            _already_processed = set(MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).distinct(key="email",
                                                                                      filter={
                                                                                          "social_media": "instagram"}))
            _all_keys = _all_keys.difference(_already_processed)
            for _e in _all_keys:
                MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).insert_data({"email": _e,
                                                                     "social_media": "instagram",
                                                                     "key": "may_be_email",
                                                                     "collection": COLLECTIONS.INSTAGRAM_SINGLE_POST
                                                                     })
        elif process_key == "may_be_phone_number":
            _already_processed = set(MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).distinct(key="phone_number",
                                                                                             filter={
                                                                                                 "social_media": "instagram"}))
            _all_keys = _all_keys.difference(_already_processed)
            for _e in _all_keys:
                MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).insert_data({"phone_number": _e,
                                                                            "social_media": "instagram",
                                                                            "key": process_key,
                                                                            "collection": COLLECTIONS.INSTAGRAM_SINGLE_POST
                                                                            })

    def process_facebook_posts_keys(self, process_key):
        _all_keys = set()
        for item in MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find({
            process_key: {"$exists": True},
            "is_donation_context_text": True
        }):
            if process_key in item:
                _all_keys.add(item[process_key])
        if None in _all_keys:
            _all_keys.remove(None)
        if process_key == "may_be_email":
            for _e in _all_keys:
                MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).insert_data({"email": _e,
                                                                     "social_media": "facebook",
                                                                     "key": process_key,
                                                                     "collection": COLLECTIONS.FACEBOOK_SINGLE_POST
                                                                     })
        elif process_key == "may_be_phone_number":
            for _e in _all_keys:
                MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).insert_data({"phone_number": _e,
                                                                            "social_media": "facebook",
                                                                            "key": process_key,
                                                                            "collection": COLLECTIONS.FACEBOOK_SINGLE_POST
                                                                            })

    def process_facebook_profile_keys(self, process_key):
        _all_keys = set()
        for item in MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).find({
            process_key: {"$exists": True}
        }):
            if process_key in item:
                _all_keys.add(item[process_key])
        if None in _all_keys:
            _all_keys.remove(None)
        if process_key == "email":
            for _e in _all_keys:
                MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).insert_data({"email": _e,
                                                                     "social_media": "facebook",
                                                                     "key": process_key,
                                                                     "collection": COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE
                                                                     })
        elif process_key == "phone":
            for _e in _all_keys:
                MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).insert_data({"phone": _e,
                                                                            "social_media": "facebook",
                                                                            "key": process_key,
                                                                            "collection": COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE
                                                                            })

    def process_telegram_posts_keys(self, process_key):
        _all_keys = set()
        for item in MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).find({
            process_key: {"$exists": True},
            "is_donation_context_text": True
        }):
            if process_key in item:
                _all_keys.add(item[process_key])
        if None in _all_keys:
            _all_keys.remove(None)
        if process_key == "may_be_email":
            for _e in _all_keys:
                MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).insert_data({"email": _e,
                                                                     "social_media": "telegram",
                                                                     "key": process_key,
                                                                     "collection": COLLECTIONS.TELEGRAM_SINGLE_POST
                                                                     })
        elif process_key == "may_be_phone_number":
            for _e in _all_keys:
                MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).insert_data({"phone_number": _e,
                                                                            "social_media": "telegram",
                                                                            "key": process_key,
                                                                            "collection": COLLECTIONS.TELEGRAM_SINGLE_POST
                                                                            })

    def process_you_tube_posts_keys(self, process_key):
        _all_keys = set()
        for item in MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find({
            process_key: {"$exists": True},
            "is_donation_context_text": True
        }):
            if process_key in item:
                _all_keys.add(item[process_key])
        if None in _all_keys:
            _all_keys.remove(None)
        if process_key == "may_be_email":
            for _e in _all_keys:
                MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).insert_data({"email": _e,
                                                                     "social_media": "youtube",
                                                                     "key": process_key,
                                                                     "collection": COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH
                                                                     })
        elif process_key == "may_be_phone_number":
            for _e in _all_keys:
                MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).insert_data({"phone_number": _e,
                                                                            "social_media": "youtube",
                                                                            "key": process_key,
                                                                            "collection": COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH
                                                                            })

    def process_email_requests(self):
        _emails = set(
            MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).distinct(key="email", filter={
                "output": {"$exists": False},
                "social_media": self.social_media}

                                                             ))
        if None in _emails:
            _emails.remove(None)
        processed_count = 1
        for cnt, _email in enumerate(_emails):

            if processed_count == 199:
                print("Free API Limit exceeding, stopping at count {}".format(cnt))
                break

            print("Processing {}/{}, email: {}".format(cnt, len(_emails), _email))

            is_found = len(
                set(MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).distinct(key="output.fraud_score",
                                                                     filter={"email": _email}))) > 0
            if is_found:
                print("Escaping already done .. {}".format(_email))
                continue

            try:
                _request_ = Validate(API_KEY.IP_QUALITY_SCORE)
                _response_ = _request_.email_validation_api(_email)

                if 'message' in _response_:
                    if 'You have insufficient credits to make this query' in _response_['message']:
                        print("Breaking from insufficient credits ... ")
                        break
                    if 'You have exceeded your request quota of 200 per day' in _response_['message']:
                        print("Breaking from quota exceeded ... ")
                        break

                MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).find_and_modify(key={"email": _email}, data={
                    "output": _response_
                })
                print("Data inserted: input:{}, output:{}".format(_email, _response_))
                time.sleep(1)  # graceful wait
                processed_count = processed_count + 1
            except Exception as ex:
                print("Exception {}".format(ex))

    def get_clean_phone_number(self, _process_number):
        _process_number = _process_number.replace("(", "")
        _process_number = _process_number.replace(")", "")
        _process_number = _process_number.replace("-", "")
        _process_number = _process_number.replace(" ", "")
        _process_number = _process_number.replace("+", "")
        _process_number = _process_number.strip()
        return _process_number

    def process_ipquality_score_phone_number_requests(self):
        _phone_numbers = set(
            MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).distinct(
                key="phone_number",
                filter={"social_media": self.social_media,
                        "output": {"$exists": False}}))
        print("Found total phone number:{}, f:{}, a:{}, s:{}".format(
            len(_phone_numbers),
            self.function,
            self.api_key,
            self.social_media
        ))
        if None in _phone_numbers:
            _phone_numbers.remove(None)

        processed_count = 1
        for cnt, _phone in enumerate(_phone_numbers):
            print("Processing {}/{}, phone: {}".format(cnt, len(_phone_numbers), _phone))
            if not _phone:
                continue
            if processed_count == 19:
                print("Free API Limit exceeding, stopping at count {}, 20 per day".format(cnt))
                break

            try:
                _request_ = Validate(API_KEY[self.api_key])
                countries = {'US', 'CA'}
                additional_params = {'country': countries}
                _process_number = self.get_clean_phone_number(_phone)
                _response_ = _request_.phone_number_api(_process_number, additional_params)

                if 'message' in _response_:
                    if 'You have insufficient credits to make this query' in _response_['message']:
                        print("Breaking from insufficient credits ... ")
                        break
                    if 'You have exceeded your request quota' in _response_['message']:
                        print("Breaking from quota exceeded ... ")
                        break

                MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).find_and_modify(
                    key={"phone_number": _phone},
                    data={
                        "processed_phone_number": _process_number,
                        "output": _response_
                    })
                print("Data inserted: input:{}, processed:{}, output:{}".format(_phone, _process_number, _response_))
                time.sleep(1)  # graceful wait
                processed_count = processed_count + 1
            except Exception as ex:
                print("Exception {}".format(ex))

    def get_abstract_api_phone_number_evaluation(self):
        _db_phone_number = MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).distinct(key="phone_number",
                                                                                   filter={
                                                                                       "output_abstract_api": {
                                                                                           "$exists": False}})
        if None in _db_phone_number:
            _db_phone_number.remove(None)

        for cnt, each_phone in enumerate(_db_phone_number):
            print("Processing, abstract api: {}/{}, {}".format(cnt, len(_db_phone_number), each_phone))
            is_found = len(set(MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).distinct(key='output_abstract_api.phone',
                                                                                       filter={
                                                                                           "phone_number": each_phone}))) > 0
            if is_found:
                print("Already processed, escaping ...{}".format(each_phone))
                continue
            self.process_each_phone_number_abstract_api(each_phone)

    def process_each_phone_number_abstract_api(self, phone_number):
        try:
            processed_phone_number = self.get_clean_phone_number(phone_number)
            response = requests.get(
                "https://phonevalidation.abstractapi.com/v1/?api_key=ab79e53d53474425a916c4eb6c600a42&phone={}".format(
                    phone_number))
            _data = response.json()
            print(_data)
            MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).find_and_modify(
                key={"phone_number": phone_number},
                data={
                    "processed_phone_number_with_plus": "+{}".format(processed_phone_number),
                    "output_abstract_api": _data
                })

        except Exception as ex:
            _error = "{}".format(ex)
            MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).find_and_modify(
                key={"phone_number": phone_number},
                data={
                    "output_abstract_api": {'error': _error, 'has_error': True}
                })


if __name__ == "__main__":
    _arg_parser = argparse.ArgumentParser(description="Email and Phone processor")
    _arg_parser.add_argument("-f", "--function_name",
                             action="store",
                             required=True,
                             help="function_name")

    _arg_parser.add_argument("-a", "--api_key",
                             action="store",
                             required=False,
                             help="function_name")

    _arg_parser.add_argument("-s", "--social_media",
                             action="store",
                             required=False,
                             help="function_name")

    _arg_value = _arg_parser.parse_args()

    _dc = ProcessEmailVerification(_arg_value.function_name, _arg_value.api_key, _arg_value.social_media)
    _dc.process()
