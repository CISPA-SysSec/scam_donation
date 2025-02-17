from constants import COLLECTIONS, API_KEY
from db_util import MongoDBActor
from openai import OpenAI

import base64
import os
import re
import hashlib
import tempfile as tmp
import subprocess
import shutil
import time
import pycountry
import requests

"""
    ```Shared Utils```
    This file contains shared functions that are used in several classes analysis.
"""

HASH_TAG_INTERESTED_KEYWORDS = [
    "givebetter",
    "fund",
    "help",
    "actofkindness",
    "support",
    "charity",
    "donate",
    "donation",
    "donor",
    "awareness",
    "giving",
    "foundation",
    "contribute",
    "helpsomeoneout"
]

SEARCH_TEXT = [
    "donate",
    "donation",
    "charity",
    "support ukraine",
    "earthquake support",
    "surgery support",
    "cancer support",
    "local firefighters support",
    "police support",
    "veterans support",
    "animal support",
    "hunger support",
    "help victim",
    "send via PayPal friends",
    "sent via PayPal friends",
    "thank you for a donation",
    "donate right now",
    "good cause",
    "help disaster victim",
    "tax relief",
    "gofundme",
    "christmas gift",
    "wildfires disaster charity",
    "breast cancer charity",
    "bible society charity",
    "covid charity",
    "home test kits support",
    "PPE charity",
    "kids wish network",
    "cancer fund of america",
    "Children Wish Foundation International",
    "Fund American Breast Cancer Foundation",
    "Fund Firefighters Charitable Foundation",
    "Fund Breast Cancer Relief Foundation",
    "Fund International Union of Police Associations",
    "Fund National Veterans Service Fund",
    "Fund American Association of State Troopers",
    "Fund Children Cancer Fund of America",
    "Fund Children Cancer Recovery Foundation",
    "Youth Development Fund",
    "Fund Committee For Missing Children",
    "Fund Association for Firefighters and Paramedics",
    "Fund Project Cure",
    "National Caregiving Foundation",
    "Fund Operation Lookout National Center for Missing Youth",
    "Fund United States Deputy Sheriffs Association",
    "Fund Vietnow National Headquarters",
    "Police Protective Fund",
    "Fund National Cancer Coalition",
    "Fund Woman to Woman Breast Cancer Foundation",
    "Fund American Foundation For Disabled Children",
    "The Veterans Fund",
    "Fund Heart Support of America",
    "Fund Veterans Assistance Foundation",
    "Fund Children Charity Fund",
    "Fund Wishing Well Foundation USA",
    "Fund Defeat Diabetes Foundation",
    "Fund Disabled Police Officers of America Inc.",
    "Fund National Police Defense Foundation",
    "Fund American Association of the Deaf & Blind",
    "Fund Reserve Police Officers Association",
    "Fund Optimal Medical Foundation",
    "Fund Disabled Police and Sheriffs Foundation",
    "Fund Disabled Police Officers Counseling Center",
    "Fund Children Leukemia Research Association",
    "Fund United Breast Cancer Foundation",
    "Fund Shiloh International Ministries",
    "Fund Circle of Friends For American Veterans",
    "Fund Find the Children",
    "Survivors and Victims Empowered",
    "Firefighters Assistance Fund",
    "Caring for Our Children Foundation Fund",
    "Fund National Narcotic Officers Associations Coalition",
    "Fund American Foundation for Children With AIDS",
    "Fund Our American Veterans",
    "Fund for Eradication of Rheumatoid Disease",
    "Firefighters Burn Fund",
    "Hope Cancer Fund",
]


def has_url_text(_text):
    _splitter = _text.split(" ")
    for _split in _splitter:
        if "http://" in _split or "https://" in _split or "www." in _split:
            _split = _split.strip()
            return _split


def get_virus_total_url_check(_url):
    return True


def get_search_context():
    return SEARCH_TEXT


def get_current_time_in_millis():
    return int(time.time() * 1000)


def get_countries():
    _all_countries = set()
    _countries = pycountry.countries
    for country in _countries:
        _name = country.name
        _all_countries.add(_name)
    return _all_countries


def download_image(request_url, save_path):
    try:
        response = requests.get(request_url, stream=True)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        if response.status_code == 200:
            with open('{}'.format(save_path), 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
    except Exception as ex:
        print("Exception occurred in downloading request to image {}".format(ex))


def get_all_distinct_twitter_text():
    print("Processing .. get_all_distinct_twitter_text")
    _texts = set()
    for item in MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find():
        if 'text' in item:
            _found_text = item['text']
            if _found_text not in _texts:
                _texts.add(_found_text)
    return list(_texts)


def get_all_author_id_and_twitter_text_tuple():
    print("Processing ... get_all_author_id_and_twitter_text_tuple")
    _tuple = []
    for item in MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find():
        if 'text' in item and 'author_id' in item:
            _found_text = item['text']
            _author_id = item['author_id']
            _found_tuple = (_author_id, _found_text)
            if _found_tuple not in _tuple:
                _tuple.append(_found_tuple)
    return _tuple


def get_all_unique_user_from_twitter():
    print("Processing .. get_all_unique_user_from_twitter")
    _found_accounts = set()
    for item in MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find():
        if 'author_id' in item:
            _author_id = item['author_id']
            _found_accounts.add(_author_id)
    return _found_accounts


def get_all_distinct_facebook_text():
    print("Processing .. get_all_distinct_facebook_text")
    _texts = set()
    for item in MongoDBActor(COLLECTIONS.FACEBOOK_HASH_TAG_SEARCH).find():
        if 'text' in item:
            _found_text = item['text']
            if _found_text not in _texts:
                _texts.add(_found_text)
    return list(_texts)


def get_all_author_id_and_facebook_text_tuple():
    print("Processing .. get_all_author_id_and_facebook_text_tuple")
    _tuple = []
    for item in MongoDBActor(COLLECTIONS.FACEBOOK_HASH_TAG_SEARCH).find():
        if 'user' in item and 'text' in item:
            _found_text = item['text']
            _user = item['user']
            if 'id' not in _user:
                continue
            _author_id = item['user']['id']
            _found_tuple = (_author_id, _found_text)
            if _found_tuple not in _tuple:
                _tuple.append(_found_tuple)
    return _tuple


def get_all_unique_user_from_facebook():
    print("Processing .. get_all_unique_user_from_facebook")
    _found_accounts = set()
    for item in MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).find():
        if 'pageName' in item:
            _author_id = item['pageName']
            _found_accounts.add(_author_id)
    return _found_accounts


def get_all_distinct_instagram_text():
    print("Processing .. get_all_distinct_instagram_text")
    _texts = set()
    _owner_id = get_all_unique_user_from_instagram()
    for each_owner in _owner_id:
        _distinct_top_text = set(MongoDBActor(COLLECTIONS.INSTAGRAM_ACCOUNT_SEARCH).distinct(key="topPosts.caption",
                                                                                             filter={
                                                                                                 "ownerId": each_owner}))
        _distinct_latest_text = set(
            MongoDBActor(COLLECTIONS.INSTAGRAM_ACCOUNT_SEARCH).distinct(key="latestPosts.caption",
                                                                        filter={
                                                                            "ownerId": each_owner}))
        _texts = _texts.union(_distinct_top_text).union(_distinct_latest_text)
    if None in _texts:
        _texts.remove(None)
    return list(_texts)


def get_all_author_id_and_instagram_text_tuple():
    print("Processing .. get_all_author_id_and_instagram_text_tuple")
    _tuple = []
    _owner_id = get_all_unique_user_from_instagram()
    for each_owner in _owner_id:
        _distinct_top_text = set(MongoDBActor(COLLECTIONS.INSTAGRAM_ACCOUNT_SEARCH).distinct(key="topPosts.caption",
                                                                                             filter={
                                                                                                 "topPosts.ownerId": each_owner}))
        _distinct_latest_text = set(
            MongoDBActor(COLLECTIONS.INSTAGRAM_ACCOUNT_SEARCH).distinct(key="latestPosts.caption",
                                                                        filter={
                                                                            "topPosts.ownerId": each_owner}))

        _union = _distinct_latest_text.union(_distinct_top_text)
        if None in _union:
            _union.remove(None)
        for each_u in _union:
            _created_tuple = (each_owner, each_u)
            if _created_tuple not in _tuple:
                print("Adding instagram .. {}".format(_created_tuple))
                _tuple.append(_created_tuple)

    return _tuple


def get_all_unique_user_from_instagram():
    print("Processing ... get_all_unique_user_from_instagram")
    _found_accounts = set()
    for item in MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).find():
        if 'ownerId' in item:
            _author_id = item['ownerId']
            _author_id = _author_id[0]
            _found_accounts.add(_author_id)
    return _found_accounts


def get_all_distinct_you_tube_text():
    print("Processing .. get_all_distinct_you_tube_text")
    _texts = set()
    _owner_id = get_all_unique_user_from_youtube()
    for each_owner in _owner_id:
        _distinct_text = set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(key="text",
                                                                                       filter={
                                                                                           "id": each_owner}))
        if None in _distinct_text:
            _distinct_text.remove(None)
        _texts = _texts.union(_distinct_text)

    return list(_texts)


def get_all_author_id_and_youtube_text_tuple():
    print("Processing ..get_all_author_id_and_youtube_text_tuple ")
    _tuple = []
    _owner_id = get_all_unique_user_from_youtube()
    for each_owner in _owner_id:
        _distinct_text = set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(key="text",
                                                                                       filter={
                                                                                           "id": each_owner}))
        if None in _distinct_text:
            _distinct_text.remove(None)
        for each_u in _distinct_text:
            _created_tuple = (each_owner, each_u)
            if _created_tuple not in _tuple:
                print("Adding {}".format(_created_tuple))
                _tuple.append(_created_tuple)

    return _tuple


def get_all_unique_user_from_youtube():
    print("Processing .. get_all_unique_user_from_youtube")
    _found_accounts = set()
    for item in MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find():
        if 'id' in item:
            _author_id = item['id']
            _found_accounts.add(_author_id)
    return _found_accounts


def get_all_distinct_telegram_text():
    print("Processing .. get_all_distinct_telegram_text")
    _texts = set()
    _owner_id = get_all_unique_user_from_telegram()
    for each_owner in _owner_id:
        _distinct_text = set(MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).distinct(key="posts_data.text",
                                                                                        filter={
                                                                                            "telemtr_url": each_owner}))
        if None in _distinct_text:
            _distinct_text.remove(None)
        _texts = _texts.union(_distinct_text)

    return list(_texts)


def get_all_author_id_and_telegram_text_tuple():
    print("Processing .. get_all_author_id_and_telegram_text_tuple")
    _tuple = []
    _owner_id = get_all_unique_user_from_telegram()
    for each_owner in _owner_id:
        _distinct_text = set(MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).distinct(key="posts_data.text",
                                                                                        filter={
                                                                                            "telemtr_url": each_owner}))
        if None in _distinct_text:
            _distinct_text.remove(None)
        for each_u in _distinct_text:
            _created_tuple = (each_owner, each_u)
            if _created_tuple not in _tuple:
                print("Added created tuple, telegram:{}".format(_created_tuple))
                _tuple.append(_created_tuple)

    return _tuple


def get_all_unique_user_from_telegram():
    print("Processing .. get_all_unique_user_from_telegram ")
    _found_accounts = set()
    for item in MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).find():
        if 'profile_data' not in item:
            continue
        if 'telemtr_url' in item:
            _author_id = item['telemtr_url']
            print("Added telemtrl url: {}".format(_author_id))
            _found_accounts.add(_author_id)
    return list(_found_accounts)


def get_chat_gpt_queried_data(_line_):
    _data_result = None
    client = OpenAI(api_key=API_KEY.CHAT_GPT)

    for counter in range(0, 5):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": _line_
                    }
                ],
                model="gpt-4o",
            )
            _data_result = chat_completion.choices[0].message.json()
            break
        except Exception as ex:
            # ToDo: Log here
            print("Exception occurred in fetching chatGPT {}".format(ex))
            time.sleep(counter)  # incremental wait time
    return _data_result


def get_email_address_from_line_item(line_item):
    if not line_item:
        return None
    if len(line_item) < 7:
        return None

    # https://www.mailmunch.com/blog/best-email-service-providers
    _check_email_ = ["@gmail.com", "@mail.com", "@hotmail.com", "@outlook.com", "@aol.com", "@aim.com", "@yahoo.com",
                     "@icloud.com", "@protonmail.com", "@pm.com", "@zoho.com", "@yandex.com", "@titan.com", "@gmx.com",
                     "@hubspot.com", "@tutanota.com"]

    _has_email_client = False
    _email_client = None
    for _e_client in _check_email_:
        if _e_client in line_item:
            _has_email_client = True
            _email_client = _e_client
            break

    if not _has_email_client:
        return None

    # split given line by spaces, the idea is to break by space and find the email
    _splitter = line_item.split(" ")
    for _split in _splitter:
        _split = _split.strip()
        if _email_client in _split:
            _cleaned_text = _get_cleaned_email_text(_split, _email_client)
            return _cleaned_text
    return None


def _get_cleaned_email_text(_split_text, _email_client):
    # check prepended text in the beginning of the email
    _pre_pended_char = ["&lt;", "@", "\n", ":", ",", "[", "{", "("]
    for _ch in _pre_pended_char:
        if _split_text.startswith(_ch):
            _split_text = _split_text.split(_ch)[1]
            _split_text = _split_text.strip()

    # check ending extra words with email client
    _extra_append_char = [".", "&gt;", ",", "*", "\n", "]", "}", ")"]
    for _ch in _extra_append_char:
        _extra = "{}{}".format(_email_client, _ch)
        if _extra in _split_text:
            _split_text = _split_text.split(_extra)[0]
            # re-add the email_client that removed from above split
            if _email_client not in _split_text:
                _split_text = "{}{}".format(_split_text, _email_client)
                _split_text = _split_text.strip()

    # middle text if present
    _middle_char = ["(", "{", "[", ":", "#", "mail=", "…", "*"]
    for _ch in _middle_char:
        if _ch in _split_text:
            _split_text = _split_text.split(_ch)[1]
            _split_text = _split_text.strip()

    # special case
    _other_char = ["\n", ",", "➡️", " ", '👉']
    for _o in _other_char:
        if _o in _split_text:
            _split_again = _split_text.split(_o)
            _may_be = None
            if len(_split_again) > 0:
                for _s in _split_again:
                    if "gmail.com" in _s.lower() or "mail.com" in _s.lower():
                        _split_text = _s
                        _split_text = _split_text.strip()
                        break

    _split_text = _split_text.lower()

    # some email endup as
    # t.co/ehxo7kjpgk.reg@gmail.com
    # //t.co/ehxo7kjhqm.reg@gmail.com

    if "//t.co/" in _split_text:  # scammer put
        return None
    if "." not in _split_text:
        return None

    if ".com" in _split_text:
        _email = _split_text.split(".com")[0]
        _split_text = "{}{}".format(_email, ".com")
        _split_text = _split_text.strip()

    if "www." in _split_text:
        _split_text = _split_text.replace("www.", "")

    if '@' not in _split_text:
        return None

    if "at" in _split_text:
        _split_text = _split_text.replace("at", "")
        _split_text = _split_text.strip()

    if _split_text.startswith("."):
        _split_text = _split_text[1:len(_split_text)]

    return _split_text


# https://github.com/SLakhani1/Phone-Number-and-Email-Address-Extractor/blob/master/extractor.py
def get_phone_number_from_line(line):
    result = []
    PhnNumCheck = re.compile(r'''
        (\d{3}|\(\d{3}\))    #first three-digit
        (\s|-|\.)?           #separator or space
        (\d{3}|\(\d{3}\))    #second three-digits
        (\s|-|\.)?           #separator or space
        (\d{4}|\(\d{4}\))    #last four-digits
    ''', re.VERBOSE)
    for num in PhnNumCheck.findall(line):
        result.append(num[0] + num[2] + num[4])
    if result:
        return result[0]
    else:
        return None


def get_email(line):
    result = []
    emailCheck = re.compile(r'''
        [a-zA-Z0-9.+_-]+  #username
        @                 #@ character
        [a-zA-Z0-9.+_-]+  #domain name
        \.                #first .(dot) 
        [a-zA-Z]          #domain type like-- com
        \.?               #second .(dot) for domains like co.in
        [a-zA-Z]*         #second part of domain type like 'in' in  co.in 
    ''', re.VERBOSE)

    for emails in emailCheck.findall(line):
        result.append(emails)
    if len(result) > 0:
        return result[0]
    else:
        return None


def get_url_from_line(line):
    _found_url = []
    try:
        _splitter = line.split(" ")
        for l in _splitter:
            urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', l)
            _found_url = _found_url + list(urls)
    except:
        pass
    return list(set(_found_url))

def get_crypto_address_from_line(_line_item):
    try:
        if not _line_item:
            return None
        _splitter = _line_item.split(" ")
        for _s in _splitter:
            is_btc = is_valid_bitcoin_address(_s)
            if is_btc:
                return _s
            is_eth = is_valid_ethereum_address((_s))
            if is_eth:
                return _s
    except:
        pass
    return None


def is_valid_bitcoin_address(_str):
    try:
        regex = "^(bc1|[13])[a-km-zA-HJ-NP-Z1-9]{25,34}$"
        p = re.compile(regex)
        if str is None:
            return False
        return re.search(p, _str)
    except:
        pass
    return None


def is_valid_ethereum_address(_str):
    try:
        regex = r'^(0x)?[0-9a-fA-F]{40}$'
        return re.match(regex, _str)
    except:
        pass
    return None


def get_twitter_verified_author_ids():
    author_ids = set(MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).distinct(key="author_id",
                                                                            filter={"isVerified": True}))
    if None in author_ids:
        author_ids.remove(None)
    return author_ids


def is_twitter_verified_author_id(author_id):
    is_verified = set(MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).distinct(key="isVerified",
                                                                             filter={"author_id": author_id}))
    if None in is_verified:
        is_verified.remove(None)
    if len(is_verified) == 0:
        return False
    return list(is_verified)[0]


def get_instagram_verified_owner_ids():
    owner_ids = set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).distinct(key="ownerId",
                                                                                     filter={"verified": True}))
    if None in owner_ids:
        owner_ids.remove(None)
    return owner_ids


def is_instagram_verified_author_id(ownerId):
    is_verified = set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).distinct(key="verified",
                                                                                       filter={"ownerId": ownerId}))
    if None in is_verified:
        is_verified.remove(None)
    if len(is_verified) == 0:
        return False
    return list(is_verified)[0]


# Note facebook does not have verified author ids
def get_facebook_verified_author_ids():
    return []


# Note telegram does not have verified author ids
def get_telegram_verified_author_ids():
    return []


# Note youtube does not have verified author ids
def get_you_tube_verified_author_ids():
    return []


def telegram_restricted_account():
    _acc = set(MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).distinct(key="telemtr_url",
                                                                          filter={
                                                                              "input.restriction": "telegramRestriction"}))
    if None in _acc:
        _acc.remove(None)
    return _acc


def get_facebook_donation_context_account():
    _acc = set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).distinct(key="id",
                                                                       filter={
                                                                           "is_donation_context_text": True}))
    if None in _acc:
        _acc.remove(None)
    return _acc


def get_instagram_donation_context_account():
    _acc = set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).distinct(key="ownerId",
                                                                        filter={
                                                                            "is_donation_context_text": True}))
    if None in _acc:
        _acc.remove(None)
    return _acc


def get_twitter_donation_context_account():
    _acc = set(MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(key="author_id",
                                                                       filter={
                                                                           "is_donation_context_text": True}))
    if None in _acc:
        _acc.remove(None)
    return _acc


def get_telegram_donation_context_account():
    _acc = set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(key="telemtr_url",
                                                                       filter={
                                                                           "is_donation_context_text": True}))
    if None in _acc:
        _acc.remove(None)
    return _acc


def get_you_tube_donation_context_account():
    _acc = set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(key="id",
                                                                         filter={
                                                                             "is_donation_context_text": True}))
    if None in _acc:
        _acc.remove(None)
    return _acc


def get_all_collections():
    _collections = [
        COLLECTIONS.FACEBOOK_MEGA_DATA,
        COLLECTIONS.TWITTER_MEGA_DATA,
        COLLECTIONS.INSTAGRAM_MEGA_DATA,
        COLLECTIONS.YOU_TUBE_MEGA_DATA,
        COLLECTIONS.TELEGRAM_MEGA_DATA
    ]
    return _collections


def get_distinct_email_from_key_value_provided(key, email):
    _val = set(MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).distinct(key=key, filter={"email": email}))
    if None in _val:
        _val.remove(None)
    return _val


def get_distinct_phone_from_key_value_provided(key, phone):
    _val = set(MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).distinct(key=key, filter={"phone_number": phone}))
    if None in _val:
        _val.remove(None)
    return _val


def get_distinct_vt_urls_from_key_value_provided(key, url):
    _val = set(MongoDBActor(COLLECTIONS.VT_LOOK_UP).distinct(key=key, filter={"url": url}))
    if None in _val:
        _val.remove(None)
    return _val


def get_mega_collection_abuse_candidate_author_id(collection_name):
    _found = set(MongoDBActor(collection_name).distinct(key="id", filter={"is_donation_abuse_candidate": True}))
    if None in _found:
        _found.remove(None)
    return _found


def get_mega_collection_fraud_urls(collection_name):
    _found = set(MongoDBActor(collection_name).distinct(key="fraud_url"))
    if None in _found:
        _found.remove(None)
    return _found


def get_mega_collection_id_containing_fraud_urls(collection_name):
    _found = set(MongoDBActor(collection_name).distinct(key="id", filter={"has_fraud_url": True}))
    if None in _found:
        _found.remove(None)
    return _found


def get_mega_collection_fraud_email(collection_name):
    _found = set(MongoDBActor(collection_name).distinct(key="fraud_email"))
    if None in _found:
        _found.remove(None)
    return _found


def get_mega_collection_id_containing_fraud_email(collection_name):
    _found = set(MongoDBActor(collection_name).distinct(key="id", filter={"has_fraud_email": True}))
    if None in _found:
        _found.remove(None)
    return _found


def get_vt_all_urls_from_social_media(each_col):
    if 'twitter' in each_col:
        _social_media = 'twitter'
    elif 'instagram' in each_col:
        _social_media = 'instagram'
    elif 'youtube' in each_col:
        _social_media = 'youtube'
    elif 'facebook' in each_col:
        _social_media = 'facebook'
    elif 'telegram' in each_col:
        _social_media = 'telegram'
    else:
        raise Exception("Unsupported exception!")
    _found = set(MongoDBActor(COLLECTIONS.VT_LOOK_UP).distinct(key="url",
                                                               filter={"additional_info.social_media": _social_media}))
    if None in _found:
        _found.remove(None)
    return _found


def get_all_found_phone_number_from_social_media(each_col):
    if 'twitter' in each_col:
        _social_media = 'twitter'
    elif 'instagram' in each_col:
        _social_media = 'instagram'
    elif 'youtube' in each_col:
        _social_media = 'youtube'
    elif 'facebook' in each_col:
        _social_media = 'facebook'
    elif 'telegram' in each_col:
        _social_media = 'telegram'
    else:
        raise Exception("Unsupported exception!")
    _found = set(MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).distinct(key="phone_number",
                                                                         filter={"social_media": _social_media}))
    if None in _found:
        _found.remove(None)
    return _found


def get_all_found_email_from_social_media(each_col):
    if 'twitter' in each_col:
        _social_media = 'twitter'
    elif 'instagram' in each_col:
        _social_media = 'instagram'
    elif 'youtube' in each_col:
        _social_media = 'youtube'
    elif 'facebook' in each_col:
        _social_media = 'facebook'
    elif 'telegram' in each_col:
        _social_media = 'telegram'
    else:
        raise Exception("Unsupported exception!")

    _found = set(MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).distinct(key="email",
                                                                  filter={"social_media": _social_media}))
    if None in _found:
        _found.remove(None)
    return _found


def get_mega_collection_fraud_phone(collection_name):
    _found = set(MongoDBActor(collection_name).distinct(key="fraud_phone"))
    if None in _found:
        _found.remove(None)
    return _found


def get_mega_collection_id_containing_fraud_phone(collection_name):
    _found = set(MongoDBActor(collection_name).distinct(key="id", filter={"has_fraud_phone": True}))
    if None in _found:
        _found.remove(None)
    return _found


def get_mega_collection_crypto(collection_name):
    _found = set(MongoDBActor(collection_name).distinct(key="has_crypto"))
    if None in _found:
        _found.remove(None)
    return _found


def get_mega_collection_id_containing_crypto(collection_name):
    _found = set(MongoDBActor(collection_name).distinct(key="id", filter={"has_crypto": True}))
    if None in _found:
        _found.remove(None)
    return _found


def get_mega_collection_accounts(collection_name):
    _found = set(MongoDBActor(collection_name).distinct(key="id"))
    return _found


def get_mega_collection_posts(collection_name):
    _posts = []
    for item in MongoDBActor(collection_name).find():
        for each in item['posts_data']:
            if 'text' in each:
                _posts.append(each['text'])
    return _posts


def get_text_from_img(img_path):
    try:
        file_to_store = tmp.NamedTemporaryFile(delete=False)

        process = subprocess.Popen(['tesseract', img_path, file_to_store.name], stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        process.communicate()

        with open(file_to_store.name + '.txt', 'r') as handle:
            result_msg = handle.read()

        os.remove(file_to_store.name + '.txt')
        os.remove(file_to_store.name)

        return result_msg
    except Exception as ex:
        print("Error in taking image OCR {}".format(ex))

    return ""


def get_img_hash(img_path):
    with open(img_path, "rb") as f:
        img_hash = hashlib.sha256()
        while chunk := f.read(8192):
            img_hash.update(chunk)
    return img_hash.hexdigest()


def get_vt_positive_url_from_social_media(social_media):
    _all_vt_positive_url = set(MongoDBActor(COLLECTIONS.VT_LOOK_UP).distinct(key="url",
                                                                             filter={"results.positives": {
                                                                                 "$gte": 2},
                                                                                 "additional_info"
                                                                                 ".social_media": social_media}))
    if None in _all_vt_positive_url:
        _all_vt_positive_url.remove(None)
    return _all_vt_positive_url


def get_ip_risk_email_by_social_media(social_media):
    _all_ip_positive_email = set(MongoDBActor(COLLECTIONS.EMAIL_LOOK_UP).distinct(key="email",
                                                                                  filter={"output.fraud_score": {
                                                                                      "$gte": 85},
                                                                                      "social_media": social_media}))
    if None in _all_ip_positive_email:
        _all_ip_positive_email.remove(None)
    return _all_ip_positive_email


def get_ip_risk_phone_number_by_social_media(social_media):
    _all_ip_positive_phone_number = set(MongoDBActor(COLLECTIONS.PHONE_NUMBER_LOOK_UP).distinct(key="phone_number",
                                                                                                filter={
                                                                                                    "output.fraud_score": {
                                                                                                        "$gte": 85},
                                                                                                    "social_media": social_media}))
    if None in _all_ip_positive_phone_number:
        _all_ip_positive_phone_number.remove(None)
    return _all_ip_positive_phone_number
