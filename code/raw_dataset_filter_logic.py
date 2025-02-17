from constants import COLLECTIONS
from db_util import MongoDBActor

import argparse
import json
import shared_util
import random

"""
    ```Raw Data Processor```
    This class processes the raw data, and performs several filtrations including fraud channels, and 
    adding tags in collections to make the easy identification of the various keys-value of the data.
    
    Examples -
        is_donation_context_text - This flag checks whether a given text is related to donation querying ChatGPT
        may_be_email - This flag checks whether a given text contain email addresses
        may_be_phone - This flag checks whether a given text contain phone numbers
        may_be_crypto - This flag checks whether a given text contain crypto address
        may_be_url - This flag checks whether a given text contain URL address
        may_be_verified - This flag checks whether a given account is verified account
"""


class FilterData:
    def __init__(self, function_name):
        self.function_name = function_name

    def update_twitter_assert_context_text(self, assert_context='is_donation_context_text'):
        _author_id_text = shared_util.get_all_author_id_and_twitter_text_tuple()
        random.shuffle(_author_id_text)
        for count, post in enumerate(_author_id_text):
            _author_id = post[0]
            _post_text = post[1]
            print(
                'Processing Twitter ChatGPT update_twitter_assert_context_text .. {}, {}/{}, {}'.format(
                    _author_id, count, len(_author_id_text), assert_context))

            is_already_processed = len(set(MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(
                key=assert_context,
                filter={"author_id": _author_id,
                        "text": _post_text}))) > 0
            if is_already_processed:
                print("Already processed .. escaping ..")
                continue
            if assert_context == "is_donation_context_text":
                _result = self.is_donation_text_assert_via_chat_gpt(_post_text)
            elif assert_context == "is_text_in_english":
                _result = self.is_english_donation_text_assert_via_chat_gpt(_post_text)
            else:
                raise Exception("Unsupported param {}".format(assert_context))

            MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find_and_modify(key={"author_id": _author_id,
                                                                                "text": _post_text},
                                                                           data={
                                                                               assert_context: _result
                                                                           })
            print("Result: input:{}, output:{}".format(_post_text, _result))

    def update_twitter_duplicated_context_text(self, assert_context='is_donation_context_text'):
        _author_text = []
        for item in MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find({assert_context: {"$exists": True}}):
            if assert_context not in item:
                continue
            _found_text = item['text']
            _found_assert_context = item[assert_context]
            _tuple = (item['text'], _found_assert_context)
            if _tuple not in _author_text:
                _author_text.append(_tuple)

        _len = len(_author_text)
        for count, post in enumerate(_author_text):
            print("Processing {}/{}, {}".format(count, _len, post))
            MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find_and_modify(
                key={'text': post[0], assert_context: {"$exists": False}}, data={assert_context: post[1]})

    def update_twitter_found_process_key(self, process_key):
        _author_id_text = []
        _search_key = {process_key: {"$exists": False}}
        for item in MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find(_search_key):
            if 'author_id' in item and 'text' in item:
                _tuple = (item['author_id'], item['text'])
                if _tuple not in _author_id_text:
                    _author_id_text.append(_tuple)
        random.shuffle(_author_id_text)
        for count, post in enumerate(_author_id_text):
            _author_id = post[0]
            _post_text = post[1]
            print(
                'Processing Twitter email update_twitter_found_email_address .. {}, {}/{}'.format(_author_id, count,
                                                                                                  len(_author_id_text)))

            is_already_processed = set(MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(
                key=process_key,
                filter={"author_id": _author_id,
                        "text": _post_text}))
            if None in is_already_processed:
                is_already_processed.remove(None)

            if len(is_already_processed) > 0:
                print("Already processed .. escaping ..")
                continue

            if process_key == "may_be_email":
                _result = shared_util.get_email_address_from_line_item(_post_text)
            elif process_key == "may_be_url":
                _result = shared_util.get_url_from_line(_post_text)
            elif process_key == "may_be_crypto":
                _result = shared_util.get_crypto_address_from_line(_post_text)
            elif process_key == "may_be_phone_number":
                _result = shared_util.get_phone_number_from_line(_post_text)
            elif process_key == "may_be_verified":
                _result = shared_util.is_twitter_verified_author_id(_author_id)
            else:
                raise Exception("Unsupported process key!")

            MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find_and_modify(key={"author_id": _author_id,
                                                                                "text": _post_text},
                                                                           data={
                                                                               process_key: _result
                                                                           })
            print("Result: input:{}, output:{}".format(_post_text, _result))

    def update_facebook_duplicated_context_text(self, assert_context='is_donation_context_text'):
        _author_text = []
        for item in MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find({assert_context: {"$exists": True}}):
            if assert_context not in item:
                continue
            _found_text = item['text']
            _found_assert_context = item[assert_context]
            _tuple = (item['text'], _found_assert_context)
            if _tuple not in _author_text:
                _author_text.append(_tuple)

        _len = len(_author_text)
        for count, post in enumerate(_author_text):
            print("Processing {}/{}, {}".format(count, _len, post))
            MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find_and_modify(
                key={'text': post[0], assert_context: {"$exists": False}}, data={assert_context: post[1]})

    def update_facebook_assert_context_text(self, assert_context='is_donation_context_text'):
        _author_text = set()
        for item in MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find({assert_context: {"$exists": False}}):
            if assert_context in item:
                continue
            _author_text.add(item['text'])

        _len = len(_author_text)
        for count, post in enumerate(_author_text):
            print("Processing {}/{}, {}".format(count, _len, post))
            if assert_context == "is_donation_context_text":
                _result = self.is_donation_text_assert_via_chat_gpt(post)
            elif assert_context == "is_text_in_english":
                _result = self.is_english_donation_text_assert_via_chat_gpt(post)
            else:
                raise Exception("Unsupported param {}".format(assert_context))

            print("Results: {}".format(_result))
            MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find_and_modify(
                key={'text': post}, data={assert_context: _result})

    def update_facebook_found_process_key(self, process_key):
        _author_id_text = []
        _search_key = {process_key: {"$exists": False}}
        for item in MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find(_search_key):
            _tuple = (item['id'], item['text'])
            if _tuple not in _author_id_text:
                _author_id_text.append(_tuple)
        random.shuffle(_author_id_text)
        random.shuffle(_author_id_text)
        for count, post in enumerate(_author_id_text):
            _author_id = post[0]
            _post_text = post[1]
            print(
                'Processing Facebook email update_facebook_found_email_address .. {}, {}/{}'.format(_author_id,
                                                                                                    count,
                                                                                                    len(_author_id_text)))

            is_already_processed = len(set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).distinct(
                key=process_key,
                filter={"id": _author_id,
                        "text": _post_text}))) > 0
            if is_already_processed:
                print("Already processed .. escaping ..")
                continue

            if process_key == "may_be_email":
                _result = shared_util.get_email_address_from_line_item(_post_text)
            elif process_key == "may_be_url":
                _result = shared_util.get_url_from_line(_post_text)
            elif process_key == "may_be_crypto":
                _result = shared_util.get_crypto_address_from_line(_post_text)
            elif process_key == "may_be_verified":
                _result = None  # Information not unavailable
            elif process_key == "may_be_phone_number":
                _result = shared_util.get_phone_number_from_line(_post_text)
            else:
                raise Exception("Unsupported process key!")

            MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find_and_modify(key={"id": _author_id,
                                                                                "text": _post_text},
                                                                           data={
                                                                               process_key: _result
                                                                           })
            print("Result: input:{}, output:{}".format(_post_text, _result))

    def update_instagram_duplicated_text_context(self, assert_context='is_donation_context_text'):
        _author_text = []
        for item in MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).find({assert_context: {"$exists": True}}):
            if assert_context not in item:
                continue
            _found_text = item['text']
            _found_assert_context = item[assert_context]
            _tuple = (item['text'], _found_assert_context)
            if _tuple not in _author_text:
                _author_text.append(_tuple)

        _len = len(_author_text)
        for count, post in enumerate(_author_text):
            print("Processing {}/{}, {}".format(count, _len, post))
            MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).find_and_modify(
                key={'text': post[0], assert_context: {"$exists": False}}, data={assert_context: post[1]})

    def update_instagram_assert_context_text(self, assert_context='is_donation_context_text'):
        _author_text = set()
        for item in MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).find({assert_context: {"$exists": False}}):
            if assert_context in item:
                continue
            _author_text.add(item['text'])

        _len = len(_author_text)
        for count, post in enumerate(_author_text):
            print("Processing {}/{}, {}".format(count, _len, post))
            if assert_context == "is_donation_context_text":
                _result = self.is_donation_text_assert_via_chat_gpt(post)
            elif assert_context == "is_text_in_english":
                _result = self.is_english_donation_text_assert_via_chat_gpt(post)
            else:
                raise Exception("Unsupported param {}".format(assert_context))

            print("Results: {}".format(_result))
            MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).find_and_modify(
                key={'text': post}, data={assert_context: _result})

    def update_instagram_found_process_key(self, process_key):
        _author_id_text = []
        _search_key = {process_key: {"$exists": False}}
        for item in MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).find(_search_key):
            _tuple = (item['ownerId'], item['text'])
            if _tuple not in _author_id_text:
                _author_id_text.append(_tuple)
        random.shuffle(_author_id_text)
        for count, post in enumerate(_author_id_text):
            _author_id = post[0]
            _post_text = post[1]
            print(
                'Processing Instagram found email address update_instagram_found_email_address .. {}, {}/{}'
                .format(_author_id, count, len(_author_id_text)))

            if process_key == "may_be_email":
                _result = shared_util.get_email_address_from_line_item(_post_text)
            elif process_key == "may_be_url":
                _result = shared_util.get_url_from_line(_post_text)
            elif process_key == "may_be_crypto":
                _result = shared_util.get_crypto_address_from_line(_post_text)
            elif process_key == "may_be_phone_number":
                _result = shared_util.get_phone_number_from_line(_post_text)
            elif process_key == "may_be_verified":
                _result = shared_util.is_instagram_verified_author_id(_author_id)
            else:
                raise Exception("Unsupported process key!")

            _key = {'text': _post_text, 'ownerId': _author_id}
            _data_ = {process_key: _result}
            MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).find_and_modify(key=_key, data=_data_)
            print("Result: input:{}, output:{}".format(_post_text, _result))
            print("Result: input:{}, output:{}".format(_post_text, _result))

    def is_donation_text_assert_via_chat_gpt(self, _txt):
        try:
            _input_format = "Your are given a text and asked to identify whether this text asking someone for money or some help with donation or charity."
            _output_format = "The output will be only boolean value true or false compatible with a python boolean value. Do not include any explanation"
            _input_txt = "Input: {} ".format(_txt)

            _gpt_query = "{} {} {} ".format(_input_format, _output_format, _input_txt)

            _data_found = shared_util.get_chat_gpt_queried_data(_gpt_query)
            if not _data_found:
                return None
            _dict = json.loads(_data_found)
            if 'content' not in _dict:
                return None
            _found_flag = _dict['content'].lower()
            return _found_flag == "true"
        except:
            pass
        return None

    def is_english_donation_text_assert_via_chat_gpt(self, _txt):
        try:
            _input_format = "Your are given a text and asked to identify whether this text is English text or not."
            _output_format = "The output will be only boolean value true or false compatible with a python boolean value. Do not include any explanation"
            _input_txt = "Input: {} ".format(_txt)

            _gpt_query = "{} {} {} ".format(_input_format, _output_format, _input_txt)

            _data_found = shared_util.get_chat_gpt_queried_data(_gpt_query)
            if not _data_found:
                return None
            _dict = json.loads(_data_found)
            if 'content' not in _dict:
                return None
            _found_flag = _dict['content'].lower()
            return _found_flag == "true"
        except:
            pass
        return None

    def update_you_tube_assert_context_text(self, assert_context='is_donation_context_text'):
        _author_id_text = shared_util.get_all_author_id_and_youtube_text_tuple()
        random.shuffle(_author_id_text)
        for count, post in enumerate(_author_id_text):
            _author_id = post[0]
            _post_text = post[1]
            print(
                'Processing YouTube ChatGPT update_you_tube_assert_context_text .. {}, {}/{}'.format(
                    _author_id, count, len(_author_id_text), assert_context))

            is_already_processed = len(set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(
                key=assert_context,
                filter={"id": _author_id,
                        "text": _post_text}))) > 0
            if is_already_processed:
                print("Already processed .. escaping ..")
                continue

            if assert_context == "is_donation_context_text":
                _result = self.is_donation_text_assert_via_chat_gpt(_post_text)
            elif assert_context == "is_text_in_english":
                _result = self.is_english_donation_text_assert_via_chat_gpt(_post_text)
            else:
                raise Exception("Unsupported param {}".format(assert_context))

            MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find_and_modify(key={"id": _author_id,
                                                                                  "text": _post_text},
                                                                             data={
                                                                                 assert_context: _result
                                                                             })
            print("Result: input:{}, output:{}".format(_post_text, _result))

    def update_you_tube_duplicated_context_text(self, assert_context):
        _author_text = []
        for item in MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find({assert_context: {"$exists": True}}):
            if assert_context not in item:
                continue
            _found_text = item['text']
            _found_assert_context = item[assert_context]
            _tuple = (item['text'], _found_assert_context)
            if _tuple not in _author_text:
                _author_text.append(_tuple)

        _len = len(_author_text)
        for count, post in enumerate(_author_text):
            print("Processing {}/{}, {}".format(count, _len, post))
            MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find_and_modify(
                key={'text': post[0], assert_context: {"$exists": False}}, data={assert_context: post[1]})

    def update_you_tube_found_process_key(self, process_key):
        _author_id_text = shared_util.get_all_author_id_and_youtube_text_tuple()
        random.shuffle(_author_id_text)
        for count, post in enumerate(_author_id_text):
            _author_id = post[0]
            _post_text = post[1]
            print(
                'Processing YouTube email update_you_tube_found_email_address .. {}, {}/{}'.format(_author_id,
                                                                                                   count,
                                                                                                   len(_author_id_text)))

            is_already_processed = len(set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(
                key=process_key,
                filter={"id": _author_id,
                        "text": _post_text}))) > 0
            if is_already_processed:
                print("Already processed .. escaping ..")
                continue

            if process_key == "may_be_email":
                _result = shared_util.get_email_address_from_line_item(_post_text)
            elif process_key == "may_be_url":
                _result = shared_util.get_url_from_line(_post_text)
            elif process_key == "may_be_crypto":
                _result = shared_util.get_crypto_address_from_line(_post_text)
            elif process_key == "may_be_verified":
                _result = None  # Information not unavailable
            elif process_key == "may_be_phone_number":
                _result = shared_util.get_phone_number_from_line(_post_text)
            else:
                raise Exception("Unsupported process key!")

            MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find_and_modify(key={"id": _author_id,
                                                                                  "text": _post_text},
                                                                             data={
                                                                                 process_key: _result
                                                                             })
            print("Result: input:{}, output:{}".format(_post_text, _result))

    def update_telegram_assert_context_text(self, assert_context="is_donation_context_text"):
        _authors = shared_util.get_all_unique_user_from_telegram()
        random.shuffle(_authors)
        for count, _author_id in enumerate(_authors):
            print('Process Tele GPT assert context_text .. {}, {}/{}, {}'.format(
                _author_id,
                count,
                len(_author_id),
                assert_context
            ))
            is_telemtr_url_already_processed = len(set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(
                key=assert_context,
                filter={"telemtr_url": _author_id}))) > 0
            if is_telemtr_url_already_processed:
                print("Escaping already processed .. {}".format(_author_id))
                continue

            _post_text = set(MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).distinct(key="posts_data.text",
                                                                                        filter={
                                                                                            'telemtr_url': _author_id}))

            if None in _post_text:
                _post_text.remove(None)

            for each_post in _post_text:
                is_already_processed_text = len(set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(
                    key=assert_context,
                    filter={"telemtr_url": _author_id,
                            "text": each_post}))) > 0
                if is_already_processed_text:
                    print("Already processed .. escaping ..")
                    continue

                if assert_context == "is_donation_context_text":
                    _result = self.is_donation_text_assert_via_chat_gpt(_post_text)
                elif assert_context == "is_text_in_english":
                    _result = self.is_english_donation_text_assert_via_chat_gpt(_post_text)
                else:
                    raise Exception("Unsupported param {}".format(assert_context))

                MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).find_and_modify(key={"telemtr_url": _author_id,
                                                                                    "text": each_post}, data={
                    "telemtr_url": _author_id,
                    "text": each_post,
                    assert_context: _result
                })
                print("Result: input:{}, output:{}".format(_post_text, _result))

    def update_telegram_duplicated_context_text(self, assert_context):
        _author_text = []
        for item in MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).find({assert_context: {"$exists": True}}):
            if assert_context not in item:
                continue
            _found_text = item['text']
            _found_assert_context = item[assert_context]
            _tuple = (item['text'], _found_assert_context)
            if _tuple not in _author_text:
                _author_text.append(_tuple)

        _len = len(_author_text)
        for count, post in enumerate(_author_text):
            print("Processing {}/{}, {}".format(count, _len, post))
            MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).find_and_modify(
                key={'text': post[0], assert_context: {"$exists": False}}, data={assert_context: post[1]})

    def update_telegram_found_process_key(self, process_key):
        _authors = []
        _search_key = {process_key: {"$exists": False}}
        for item in MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).find(_search_key):
            if 'telemtr_url' in item:
                _authors.append(item['telemtr_url'])
        _authors = list(set(_authors))
        random.shuffle(_authors)

        telegram_blocked_accounts = list(shared_util.telegram_restricted_account())
        for count, _author_id in enumerate(_authors):
            print(
                'Processing Telegram email update_telegram_email_address_found .. {}, {}/{}'.format(_author_id,
                                                                                                    count,
                                                                                                    len(_authors)))

            _all_texts = set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(
                key="text",
                filter={"telemtr_url": _author_id, process_key: {"$exists": False}
                        }))
            if None in _all_texts:
                _all_texts.remove(None)
            for each_text in _all_texts:
                is_already_processed = len(set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(
                    key=process_key,
                    filter={"telemtr_url": _author_id,
                            "text": each_text
                            }))) > 0
                if is_already_processed:
                    print("Already processed .. escaping ..")
                    continue

                if process_key == "may_be_email":
                    _result = shared_util.get_email_address_from_line_item(each_text)
                elif process_key == "may_be_url":
                    _result = shared_util.get_url_from_line(each_text)
                elif process_key == "may_be_crypto":
                    _result = shared_util.get_crypto_address_from_line(each_text)
                elif process_key == "may_be_verified":
                    _result = None  # Information not unavailable
                elif process_key == "may_be_blocked":
                    _result = _author_id in telegram_blocked_accounts
                elif process_key == "may_be_phone_number":
                    _result = shared_util.get_phone_number_from_line(each_text)
                else:
                    raise Exception("Unsupported process key!")

                _key = {"telemtr_url": _author_id, "text": each_text}
                print(_key)
                MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).find_and_modify(key=_key, data={process_key: _result})
                print("Result: input:{}, output:{}".format(each_text, _result))

    def update_twitter_posts_malicious_positive_key(self, process_key):
        if process_key == "has_malicious_url":
            vt_positive_url = shared_util.get_vt_positive_url_from_social_media('twitter')
            for each_may_be_url in vt_positive_url:
                _key = {"may_be_url": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_email":
            mal_email = shared_util.get_ip_risk_email_by_social_media('twitter')
            for each_may_be_url in mal_email:
                _key = {"may_be_email": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_phone_number":
            mal_phone = shared_util.get_ip_risk_phone_number_by_social_media('twitter')
            for each_may_be_url in mal_phone:
                _key = {"may_be_phone_number": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find_and_modify(key=_key, data={process_key: True})
        else:
            raise Exception('Unsupported request.')

    def update_twitter_profile_malicious_positive_key(self, process_key):
        if process_key == "has_malicious_url":
            vt_positive_url = shared_util.get_vt_positive_url_from_social_media('twitter')
            for each_may_be_url in vt_positive_url:
                _key = {"entities.url.urls.expanded_url": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).distinct(
                    key="author_id", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_email":
            mal_email = shared_util.get_ip_risk_email_by_social_media('twitter')
            for each_may_be_url in mal_email:
                _key = {"may_be_email": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_phone_number":
            mal_phone = shared_util.get_ip_risk_phone_number_by_social_media('twitter')
            for each_may_be_url in mal_phone:
                _key = {"may_be_phone_number": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find_and_modify(key=_key, data={process_key: True})
        else:
            raise Exception('Unsupported request.')

    def update_instagram_posts_malicious_positive_key(self, process_key):
        if process_key == "has_malicious_url":
            vt_positive_url = shared_util.get_vt_positive_url_from_social_media('instagram')
            for each_may_be_url in vt_positive_url:
                _key = {"may_be_url": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_email":
            mal_email = shared_util.get_ip_risk_email_by_social_media('instagram')
            for each_may_be_url in mal_email:
                _key = {"may_be_email": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_phone_number":
            mal_phone = shared_util.get_ip_risk_phone_number_by_social_media('instagram')
            for each_may_be_url in mal_phone:
                _key = {"may_be_phone_number": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        else:
            raise Exception('Unsupported request.')

    def update_facebook_posts_malicious_positive_key(self, process_key):
        if process_key == "has_malicious_url":
            vt_positive_url = shared_util.get_vt_positive_url_from_social_media('facebook')
            for each_may_be_url in vt_positive_url:
                _key = {"may_be_url": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_email":
            mal_email = shared_util.get_ip_risk_email_by_social_media('facebook')
            for each_may_be_url in mal_email:
                _key = {"may_be_email": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_phone_number":
            mal_phone = shared_util.get_ip_risk_phone_number_by_social_media('facebook')
            for each_may_be_url in mal_phone:
                _key = {"may_be_phone_number": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        else:
            raise Exception('Unsupported request.')

    def update_facebook_profile_malicious_positive_key(self, process_key):
        if process_key == "has_malicious_url":
            vt_positive_url = shared_util.get_vt_positive_url_from_social_media('facebook')
            for each_may_be_url in vt_positive_url:
                _key = {"website": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).distinct(
                    key="pageId", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).find_and_modify(key=_key,
                                                                                       data={process_key: True})
        elif process_key == "has_malicious_email":
            mal_email = shared_util.get_ip_risk_email_by_social_media('facebook')
            for each_may_be_url in mal_email:
                _key = {"may_be_email": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_phone_number":
            mal_phone = shared_util.get_ip_risk_phone_number_by_social_media('facebook')
            for each_may_be_url in mal_phone:
                _key = {"may_be_phone_number": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        else:
            raise Exception('Unsupported request.')

    def update_youtube_posts_malicious_positive_key(self, process_key):
        if process_key == "has_malicious_url":
            vt_positive_url = shared_util.get_vt_positive_url_from_social_media('youtube')
            for each_may_be_url in vt_positive_url:
                _key = {"may_be_url": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_email":
            mal_email = shared_util.get_ip_risk_email_by_social_media('youtube')
            for each_may_be_url in mal_email:
                _key = {"may_be_email": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_phone_number":
            mal_phone = shared_util.get_ip_risk_phone_number_by_social_media('youtube')
            for each_may_be_url in mal_phone:
                _key = {"may_be_phone_number": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find_and_modify(key=_key, data={process_key: True})
        else:
            raise Exception('Unsupported request.')

    def update_youtube_profile_malicious_positive_key(self, process_key):
        if process_key == "has_malicious_url":
            vt_positive_url = shared_util.get_vt_positive_url_from_social_media('youtube')
            for each_may_be_url in vt_positive_url:
                _key = {"descriptionLinks.url": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_email":
            mal_email = shared_util.get_ip_risk_email_by_social_media('youtube')
            for each_may_be_url in mal_email:
                _key = {"may_be_email": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_phone_number":
            mal_phone = shared_util.get_ip_risk_phone_number_by_social_media('youtube')
            for each_may_be_url in mal_phone:
                _key = {"may_be_phone_number": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(
                    key="text", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find_and_modify(key=_key, data={process_key: True})
        else:
            raise Exception('Unsupported request.')

    def update_telegram_profile_malicious_positive_key(self, process_key):
        if process_key == "has_malicious_url":
            vt_positive_url = shared_util.get_vt_positive_url_from_social_media('telegram')
            for each_may_be_url in vt_positive_url:
                _key = {"profile_data.channel_description.profile_links": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).distinct(
                    key="telemtr_url", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_email":
            mal_email = shared_util.get_ip_risk_email_by_social_media('telegram')
            for each_may_be_url in mal_email:
                _key = {"may_be_email": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(
                    key="telemtr_url", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_phone_number":
            mal_phone = shared_util.get_ip_risk_phone_number_by_social_media('telegram')
            for each_may_be_url in mal_phone:
                _key = {"may_be_phone_number": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(
                    key="telemtr_url", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        else:
            raise Exception('Unsupported request.')

    def update_telegram_posts_malicious_positive_key(self, process_key):
        if process_key == "has_malicious_url":
            vt_positive_url = shared_util.get_vt_positive_url_from_social_media('telegram')
            for each_may_be_url in vt_positive_url:
                _key = {"may_be_url": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(
                    key="telemtr_url", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_email":
            mal_email = shared_util.get_ip_risk_email_by_social_media('telegram')
            for each_may_be_url in mal_email:
                _key = {"may_be_email": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(
                    key="telemtr_url", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        elif process_key == "has_malicious_phone_number":
            mal_phone = shared_util.get_ip_risk_phone_number_by_social_media('telegram')
            for each_may_be_url in mal_phone:
                _key = {"may_be_phone_number": each_may_be_url}
                is_found = len(set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(
                    key="telemtr_url", filter=_key))) > 0
                if not is_found:
                    continue
                MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).find_and_modify(key=_key, data={process_key: True})
        else:
            raise Exception('Unsupported request.')

    def update_facebook_profile_phone_email(self, process_key):
        if process_key == "has_malicious_email":
            vt_positive_url = shared_util.get_ip_risk_email_by_social_media('facebook')
            if None in vt_positive_url:
                vt_positive_url.remove(None)
            for each_may_be_url in vt_positive_url:
                _key = {"email": each_may_be_url}
                page_urls = set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).distinct(
                    key="pageUrl", filter=_key))

                if None in page_urls:
                    page_urls.remove(None)
                if not page_urls:
                    continue
                for each_page in page_urls:
                    MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).find_and_modify(
                        key={"email": each_may_be_url,
                             "pageUrl": each_page
                             },
                        data={process_key: True})

        if process_key == "has_malicious_phone_number":
            vt_positive_url = shared_util.get_ip_risk_phone_number_by_social_media('facebook')
            for each_may_be_url in vt_positive_url:
                _key = {"phone": each_may_be_url}
                page_urls = set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).distinct(
                    key="pageUrl", filter=_key))

                if None in page_urls:
                    page_urls.remove(None)
                if not page_urls:
                    continue
                for each_page in page_urls:
                    MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).find_and_modify(
                        key={"phone": each_may_be_url,
                             "pageUrl": each_page
                             },
                        data={process_key: True})

    def process(self):
        # start of chatgpt donation based text check #
        if self.function_name == "update_twitter_donation_context_text":
            self.update_twitter_assert_context_text(assert_context='is_donation_context_text')
        elif self.function_name == "update_instagram_donation_context_text":
            self.update_instagram_assert_context_text(assert_context='is_donation_context_text')
        elif self.function_name == "update_facebook_donation_context_text":
            self.update_facebook_assert_context_text(assert_context='is_donation_context_text')
        elif self.function_name == "update_you_tube_donation_context_text":
            self.update_you_tube_assert_context_text(assert_context='is_donation_context_text')
        elif self.function_name == "update_telegram_donation_context_text":
            self.update_telegram_assert_context_text(assert_context='is_donation_context_text')
        # end of chatgpt donation based text check #

        # start of chatgpt english check context
        elif self.function_name == "update_twitter_english_context_text":
            self.update_twitter_assert_context_text(assert_context='is_text_in_english')
        elif self.function_name == "update_instagram_english_context_text":
            self.update_instagram_assert_context_text(assert_context='is_text_in_english')
        elif self.function_name == "update_facebook_english_context_text":
            self.update_facebook_assert_context_text(assert_context='is_text_in_english')
        elif self.function_name == "update_you_tube_english_context_text":
            self.update_you_tube_assert_context_text(assert_context='is_text_in_english')
        elif self.function_name == "update_telegram_english_context_text":
            self.update_telegram_assert_context_text(assert_context='is_text_in_english')
        # end of chatgpt donation based text check #

        # start of found email address in post #
        elif self.function_name == "update_twitter_found_email_address":
            self.update_twitter_found_process_key(process_key='may_be_email')
        elif self.function_name == "update_instagram_found_email_address":
            self.update_instagram_found_process_key(process_key='may_be_email')
        elif self.function_name == "update_facebook_found_email_address":
            self.update_facebook_found_process_key(process_key='may_be_email')
        elif self.function_name == "update_you_tube_found_email_address":
            self.update_you_tube_found_process_key(process_key='may_be_email')
        elif self.function_name == "update_telegram_email_address_found":
            self.update_telegram_found_process_key(process_key='may_be_email')
        # end of found email address in post #

        # update each post verified account post #
        elif self.function_name == "update_twitter_verified_account":
            self.update_twitter_found_process_key(process_key='may_be_verified')
        elif self.function_name == "update_instagram_verified_account":
            self.update_instagram_found_process_key(process_key='may_be_verified')
        elif self.function_name == "update_facebook_verified_account":
            self.update_facebook_found_process_key(process_key='may_be_verified')
        elif self.function_name == "update_you_tube_verified_account":
            self.update_you_tube_found_process_key(process_key='may_be_verified')
        elif self.function_name == "update_telegram_verified_account":
            self.update_telegram_found_process_key(process_key='may_be_verified')
        # end of found verified account in post #

        # update each post verified account post #
        elif self.function_name == "update_telegram_blocked_account":
            self.update_telegram_found_process_key(process_key='may_be_blocked')
        # end of found verified account in post #

        # start of found email address in post #
        elif self.function_name == "update_twitter_found_phone_number":
            self.update_twitter_found_process_key(process_key='may_be_phone_number')
        elif self.function_name == "update_instagram_found_phone_number":
            self.update_instagram_found_process_key(process_key='may_be_phone_number')
        elif self.function_name == "update_facebook_found_phone_number":
            self.update_facebook_found_process_key(process_key='may_be_phone_number')
        elif self.function_name == "update_you_tube_found_phone_number":
            self.update_you_tube_found_process_key(process_key='may_be_phone_number')
        elif self.function_name == "update_telegram_found_phone_number":
            self.update_telegram_found_process_key(process_key='may_be_phone_number')
        # end of found email address in post #

        # start of found URL in post #
        elif self.function_name == "update_twitter_found_url_address":
            self.update_twitter_found_process_key(process_key='may_be_url')
        elif self.function_name == "update_instagram_found_url_address":
            self.update_instagram_found_process_key(process_key='may_be_url')
        elif self.function_name == "update_facebook_found_url_address":
            self.update_facebook_found_process_key(process_key='may_be_url')
        elif self.function_name == "update_you_tube_found_url_address":
            self.update_you_tube_found_process_key(process_key='may_be_url')
        elif self.function_name == "update_telegram_found_url_address":
            self.update_telegram_found_process_key(process_key='may_be_url')
        # end of found URL address in post #

        # start of found Crypto Addresses in post #
        elif self.function_name == "update_twitter_found_crypto_address":
            self.update_twitter_found_process_key(process_key='may_be_crypto')
        elif self.function_name == "update_instagram_found_crypto_address":
            self.update_instagram_found_process_key(process_key='may_be_crypto')
        elif self.function_name == "update_facebook_found_crypto_address":
            self.update_facebook_found_process_key(process_key='may_be_crypto')
        elif self.function_name == "update_you_tube_found_crypto_address":
            self.update_you_tube_found_process_key(process_key='may_be_crypto')
        elif self.function_name == "update_telegram_found_crypto_address":
            self.update_telegram_found_process_key(process_key='may_be_crypto')
        # end of found Crypto Addresses in post #

        # start of found input malicious url in social media #
        elif self.function_name == "update_twitter_posts_malicious_url":
            self.update_twitter_posts_malicious_positive_key(process_key='has_malicious_url')
        elif self.function_name == "update_instagram_posts_malicious_url":
            self.update_instagram_posts_malicious_positive_key(process_key='has_malicious_url')
        elif self.function_name == "update_facebook_posts_malicious_url":
            self.update_facebook_posts_malicious_positive_key(process_key='has_malicious_url')
        elif self.function_name == "update_you_tube_posts_malicious_url":
            self.update_youtube_posts_malicious_positive_key(process_key='has_malicious_url')
        elif self.function_name == "update_telegram_posts_malicious_url":
            self.update_telegram_posts_malicious_positive_key(process_key='has_malicious_url')
        # end of found input malicious url in social media #

        # start of found input malicious email in social media #
        elif self.function_name == "update_twitter_posts_malicious_email":
            self.update_twitter_posts_malicious_positive_key(process_key='has_malicious_email')
        elif self.function_name == "update_instagram_posts_malicious_email":
            self.update_instagram_posts_malicious_positive_key(process_key='has_malicious_email')
        elif self.function_name == "update_facebook_posts_malicious_email":
            self.update_facebook_posts_malicious_positive_key(process_key='has_malicious_email')
        elif self.function_name == "update_you_tube_posts_malicious_email":
            self.update_youtube_posts_malicious_positive_key(process_key='has_malicious_email')
        elif self.function_name == "update_telegram_posts_malicious_email":
            self.update_telegram_posts_malicious_positive_key(process_key='has_malicious_email')
        # end of found input malicious email in social media #

        # start of found input malicious phone number in social media #
        elif self.function_name == "update_twitter_posts_malicious_phone_number":
            self.update_twitter_posts_malicious_positive_key(process_key='has_malicious_phone_number')
        elif self.function_name == "update_instagram_posts_malicious_phone_number":
            self.update_instagram_posts_malicious_positive_key(process_key='has_malicious_phone_number')
        elif self.function_name == "update_facebook_posts_malicious_phone_number":
            self.update_facebook_posts_malicious_positive_key(process_key='has_malicious_phone_number')
        elif self.function_name == "update_you_tube_posts_malicious_phone_number":
            self.update_youtube_posts_malicious_positive_key(process_key='has_malicious_phone_number')
        elif self.function_name == "update_telegram_posts_malicious_phone_number":
            self.update_telegram_posts_malicious_positive_key(process_key='has_malicious_phone_number')
        # end of found  input malicious phone number in social media #

        # start of the update profile having blocked urls
        elif self.function_name == "update_twitter_profile_malicious_positive_key":
            self.update_twitter_profile_malicious_positive_key('has_malicious_url')
        elif self.function_name == "update_youtube_profile_malicious_positive_key":
            self.update_youtube_profile_malicious_positive_key('has_malicious_url')
        elif self.function_name == "update_facebook_profile_malicious_positive_key":
            self.update_facebook_profile_malicious_positive_key('has_malicious_url')
        elif self.function_name == "update_telegram_profile_malicious_positive_key":
            self.update_telegram_profile_malicious_positive_key('has_malicious_url')
        # end of the update profile having blocked urls

        elif self.function_name == "update_facebook_profile_malicious_phone_number":
            self.update_facebook_profile_phone_email('has_malicious_phone_number')
        elif self.function_name == "update_facebook_profile_malicious_email":
            self.update_facebook_profile_phone_email('has_malicious_email')

        # start of updating the duplicated text that has missing flag
        elif self.function_name == "update_twitter_duplicated_donation_context_text":
            self.update_twitter_duplicated_context_text(assert_context='is_donation_context_text')
        elif self.function_name == "update_instagram_duplicated_donation_context_text":
            self.update_instagram_duplicated_text_context(assert_context='is_donation_context_text')
        elif self.function_name == "update_facebook_duplicated_donation_context_text":
            self.update_facebook_duplicated_context_text(assert_context='is_donation_context_text')
        elif self.function_name == "update_you_tube_duplicated_donation_context_text":
            self.update_you_tube_duplicated_context_text(assert_context='is_donation_context_text')
        elif self.function_name == "update_telegram_duplicated_donation_context_text":
            self.update_telegram_duplicated_context_text(assert_context='is_donation_context_text')
        # end of updating the duplicated text that has missing flag


if __name__ == "__main__":
    _arg_parser = argparse.ArgumentParser(description="Analysis processor")
    _arg_parser.add_argument("-f", "--function_name",
                             action="store",
                             required=True,
                             help="function_name")

    _arg_value = _arg_parser.parse_args()

    _dc = FilterData(_arg_value.function_name)
    _dc.process()
