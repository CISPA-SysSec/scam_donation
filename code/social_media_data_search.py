from twitter_api import TwitterFeeds
from constants import COLLECTIONS, IMAGES, API_KEY
from apify_client import ApifyClient
from db_util import MongoDBActor

import argparse
import os
import time
import shared_util

"""
    SocialMediaDataSearch- Collects data from social media
    This file collects data querying third party API Apify (Instagram, Facebook, Telegram, YouTube) 
    and Twitter to collect data related to social media profiles and their associated posts.
"""


class SocialMediaDataSearch:
    def __init__(self, social_media):
        self.social_media = social_media
        self.api_client = ApifyClient(API_KEY.APIFY_KEY)

    def process(self):
        if "search_keywords" in self.social_media:
            _keywords = shared_util.get_search_context()
            for count, _keyword in enumerate(_keywords):
                print("{}/{}, {}".format(count, len(_keywords), _keyword))
                if self.social_media == "instagram_search_keywords":
                    self.scrape_instagram_accounts_from_search_keywords(_keyword)
                elif self.social_media == "youtube_search_keywords":
                    self.scrape_you_tube_accounts_from_domain(_keyword)
        elif "single_profile_fetch_instagram" in self.social_media:
            self.scrape_instagram_single_profile_data()
        elif "single_profile_fetch_facebook" in self.social_media:
            self.single_profile_fetch_facebook()
        elif "search_instagram_hash_tags_collected" == self.social_media:
            self.search_instagram_hash_tags_collected()
        elif "search_facebook_hash_tags_collected" == self.social_media:
            self.search_facebook_hash_tags_collected()
        elif "download_youtube_thumbnail_image" == self.social_media:
            self.download_youtube_thumbnail_image()
        elif "re_download_facebook_hash_tag_images" == self.social_media:
            self.re_download_facebook_hash_tag_images()
        elif "download_twitter_profile_images" == self.social_media:
            self.download_twitter_profile_images()
        elif "collect_you_tube_comment" in self.social_media:
            self.collect_you_tube_comment()
        elif "collect_user_detail_from_author_id_twitter" in self.social_media:
            self.collect_user_detail_from_author_id_twitter()
        elif "collect_each_telegram_account_detail" in self.social_media:
            self.collect_each_telegram_account_detail()
        elif "collect_twitter_donation_context_search" in self.social_media:
            self.collect_twitter_donation_context_search()

    def collect_twitter_donation_context_search(self):
        _feeds = TwitterFeeds()
        _donation_context_text = shared_util.get_search_context()
        for _text in _donation_context_text:
            _data_found = _feeds.get_full_search_text_tweets_info(_text)
            for cnt, _d in enumerate(_data_found):
                _insert_json = {
                    'search_text': _text,
                    'time': int(time.time() * 1000),
                    'data': _d
                }
                _insert_id = MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).insert_data(_insert_json)
                print("Data inserted", _d)

    def collect_user_detail_from_author_id_twitter(self):
        _author_ids = set(MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(key="author_id"))
        if None in _author_ids:
            _author_ids.remove(None)

        for count, _author_id in enumerate(_author_ids):
            print('Processing {}, {}/{}'.format(_author_id, count, len(_author_ids)))
            is_found = len(set(MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).distinct(key="id",
                                                                                      filter={
                                                                                          "id": _author_id}))) > 0
            if is_found:
                print("Continuing data already processed !... {}".format(_author_id))
                pass

            run_input = {
                "customMapFunction": "(object) => { return {...object} }",
                "getFavorites": True,
                "getFollowers": True,
                "getFollowing": True,
                "getRetweeters": False,
                "includeUnavailableUsers": True,
                "maxItems": 50,
                "twitterUserIds": [
                    _author_id
                ]
            }

            try:
                run = self.api_client.actor("apidojo/twitter-user-scraper").call(run_input=run_input)
                for item in self.api_client.dataset(run["defaultDatasetId"]).iterate_items():
                    item['author_id'] = _author_id
                    item['time'] = shared_util.get_current_time_in_millis()
                    item['social_media'] = "twitter"
                    print(item)
                    MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).insert_data(item)
            except Exception as ex:
                print("Exception :{}".format(ex))

    def single_profile_fetch_facebook(self):
        _profiles = set(MongoDBActor(COLLECTIONS.FACEBOOK_HASH_TAG_SEARCH).distinct(key="user.profileUrl"))
        if None in _profiles:
            _profiles.remove(None)
        may_be_profiles = set(MongoDBActor(COLLECTIONS.FACEBOOK_HASH_TAG_SEARCH).distinct(key="url"))
        if None in may_be_profiles:
            may_be_profiles.remove(None)
        for may_be_profile in may_be_profiles:
            if "https://www.facebook.com/" in may_be_profile:
                splitter = may_be_profile.split("/")
                username = splitter[1]
                if not username:
                    continue
                username = username.strip()
                _created_url = "{}{}".format("https://www.facebook.com/", username)
                _profiles.add(_created_url)
        for count, each_profile in enumerate(_profiles):
            if "https://l.facebook.com/" in each_profile:
                continue
            print('Processing {}, {}/{}'.format(each_profile, count, len(_profiles)))
            is_found = len(set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).distinct(key="url",
                                                                                               filter={
                                                                                                   "url": each_profile}))) > 0
            if is_found:
                print("Continuing data already processed !... {}".format(each_profile))
                pass

            run_input = {
                "language": "en-US",
                "pages": [
                    each_profile
                ]
            }

            try:
                run = self.api_client.actor("apify/facebook-page-contact-information").call(run_input=run_input)
                for item in self.api_client.dataset(run["defaultDatasetId"]).iterate_items():
                    item['url'] = each_profile
                    item['time'] = shared_util.get_current_time_in_millis()
                    item['social_media'] = "facebook"
                    print(item)
                    MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).insert_data(item)
            except Exception as ex:
                print("Exception :{}".format(ex))

    def collect_you_tube_comment(self):
        _you_tube_urls = set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(key="url"))
        if None in _you_tube_urls:
            _you_tube_urls.remove(None)
        for count, you_tube_url in enumerate(_you_tube_urls):
            print("Processing {}/{} {}".format(count, len(_you_tube_urls), you_tube_url))

            is_found = len(set(MongoDBActor(COLLECTIONS.YOUTUBE_COMMENTS_SEARCH).distinct(key="url",
                                                                                          filter={
                                                                                              "url": you_tube_url}))) > 0
            if is_found:
                print("Continuing data already processed !... {}".format(you_tube_url))
                pass

            run_input = {
                "max_comments": 50,
                "proxySettings": {
                    "useApifyProxy": True
                },
                "start_urls": [
                    {
                        "url": you_tube_url
                    }
                ]
            }

            try:
                run = self.api_client.actor("deeper/youtube-comment-scrapper").call(run_input=run_input)
                for item in self.api_client.dataset(run["defaultDatasetId"]).iterate_items():
                    item['url'] = you_tube_url
                    item['time'] = shared_util.get_current_time_in_millis()
                    item['social_media'] = "youtube"
                    print(item)
                    MongoDBActor(COLLECTIONS.YOUTUBE_COMMENTS_SEARCH).insert_data(item)
            except Exception as ex:
                print("Exception :{}".format(ex))

    def download_twitter_profile_images(self):
        _to_download = []
        for item in MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).find():
            if 'profilePicture' in item:
                _profile_pic = item['profilePicture']
                _user_id = item['id']
                _save_path = "{}/{}.png".format(IMAGES.TWITTER, _user_id)
                _to_download.append((_user_id, _profile_pic, _save_path))

        _to_download = list(set(_to_download))

        for count, each_download in enumerate(_to_download):
            _user_id = each_download[0]
            _profile_pic = each_download[1]
            _save_path = each_download[2]
            print("Processing {}/{}, {}, {}".format(count, len(_to_download), _user_id, _save_path))
            if os.path.exists(_save_path):
                print("Already downloaded {}, {}".format(_user_id, _save_path))
                continue
            shared_util.download_image(_profile_pic, _save_path)
            print("Image download requested .. {}".format(_save_path))

    def re_download_facebook_hash_tag_images(self):
        for item in MongoDBActor(COLLECTIONS.FACEBOOK_HASH_TAG_SEARCH).find():
            if 'user' in item:
                _user = item['user']
                if 'profilePic' in _user:
                    _profile_pic = _user['profilePic']
                    _user_id = _user['id']
                    _save_path = "{}/{}.png".format(IMAGES.FACEBOOK, _user_id)
                    if os.path.exists(_save_path):
                        print("Already downloaded {}, {}".format(_user_id, _save_path))
                        continue
                    shared_util.download_image(_profile_pic, _save_path)
                    print("Image download requested .. {}".format(_save_path))

    def download_youtube_thumbnail_image(self):
        _tuple_data = []
        for val in MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find():
            if 'id' not in val and 'thumbnailUrl' not in val:
                continue
            _found_id = val['id']
            _thumb_nail_url = val['thumbnailUrl']
            _found = (_found_id, _thumb_nail_url)
            if _found not in _tuple_data:
                _tuple_data.append(_found)
        for count, each_tuple in enumerate(_tuple_data):
            print("Downloading image {}/{} {}".format(count, len(_tuple_data), each_tuple))
            _save_path = "{}/{}.png".format(IMAGES.YOU_TUBE, each_tuple[0])
            shared_util.download_image(each_tuple[1], _save_path)
            print("Image download requested .. {}".format(_save_path))

    def search_instagram_hash_tags_collected(self):
        _hash_tags = set()
        _hash_tags = _hash_tags.union(set(shared_util.HASH_TAG_INTERESTED_KEYWORDS))
        for each_keyword in shared_util.get_search_context():
            each_keyword = each_keyword.replace(" ", "")
            _hash_tags.add(each_keyword)

        print(list(_hash_tags))
        for count, _hash_tag in enumerate(_hash_tags):
            print("Processing {}\{} {}".format(count, len(_hash_tags), _hash_tag))

            is_found = len(set(MongoDBActor(COLLECTIONS.INSTAGRAM_HASH_TAG_SEARCH).distinct(key="search_keyword",
                                                                                            filter={
                                                                                                "search_keyword": _hash_tag}))) > 0
            if is_found:
                print("Continuing data already processed !... {}".format(_hash_tag))
                continue

            run_input = {
                "hashtags": ["#{}".format(_hash_tag)],

                "resultsLimit": 200,
            }
            try:
                run = self.api_client.actor("apify/instagram-hashtag-scraper").call(run_input=run_input)
                for item in self.api_client.dataset(run["defaultDatasetId"]).iterate_items():
                    item['search_keyword'] = _hash_tag
                    item['time'] = shared_util.get_current_time_in_millis()
                    item['social_media'] = "instagram"
                    print(item)
                    MongoDBActor(COLLECTIONS.INSTAGRAM_HASH_TAG_SEARCH).insert_data(item)
            except Exception as ex:
                print("Exception :{}".format(ex))

    def scrape_instagram_accounts_from_search_keywords(self, search_keyword):
        run_input = {
            "search": search_keyword,
            "resultsType": "details",
            "resultsLimit": 200,
            "searchType": "hashtag",
            "enhanceUserSearchWithFacebookPage": True,
            "searchLimit": 5,
        }

        try:
            run = self.api_client.actor("apify/instagram-scraper").call(run_input=run_input)
            for item in self.api_client.dataset(run["defaultDatasetId"]).iterate_items():
                item['search_keyword'] = search_keyword
                item['time'] = shared_util.get_current_time_in_millis()
                item['social_media'] = "instagram"
                print(item)
                MongoDBActor(COLLECTIONS.INSTAGRAM_ACCOUNT_SEARCH).insert_data(item)
        except Exception as ex:
            print("Exception :{}".format(ex))

    def search_facebook_hash_tags_collected(self):
        _hash_tags = set()
        _hash_tags = _hash_tags.union(set(shared_util.HASH_TAG_INTERESTED_KEYWORDS))
        for each_keyword in shared_util.get_search_context():
            each_keyword = each_keyword.replace(" ", "")
            _hash_tags.add(each_keyword)

        print(list(_hash_tags))
        for count, _hash_tag in enumerate(_hash_tags):
            print("Processing {}\{} {}".format(count, len(_hash_tags), _hash_tag))

            is_found = len(set(MongoDBActor(COLLECTIONS.FACEBOOK_HASH_TAG_SEARCH).distinct(key="search_keyword",
                                                                                           filter={
                                                                                               "search_keyword": _hash_tag}))) > 0
            if is_found:
                print("Continuing data already processed !... {}".format(_hash_tag))
                pass

            run_input = {
                "keywordList": [_hash_tag],
                "resultsLimit": 50000,
            }
            try:
                run = self.api_client.actor("apify/facebook-hashtag-scraper").call(run_input=run_input)
                for item in self.api_client.dataset(run["defaultDatasetId"]).iterate_items():
                    item['search_keyword'] = _hash_tag
                    item['time'] = shared_util.get_current_time_in_millis()
                    item['social_media'] = "facebook"
                    print(item)
                    MongoDBActor(COLLECTIONS.FACEBOOK_HASH_TAG_SEARCH).insert_data(item)

                    if 'user' in item:
                        _user = item['user']
                        if 'profilePic' in _user:
                            _profile_pic = _user['profilePic']
                            _user_id = _user['id']
                            _save_path = "{}/{}.png".format(IMAGES.FACEBOOK, _user_id)
                            if os.path.exists(_save_path):
                                continue
                            shared_util.download_image(_profile_pic, _save_path)
                            print("Image download requested .. {}".format(_save_path))
            except Exception as ex:
                print("Exception :{}".format(ex))

    def scrape_instagram_single_profile_data(self):
        self.scrape_instagram_single_profile_data_from_keywords_search()
        self.scrape_instagram_single_profile_data_from_hash_tag_search()

    def scrape_instagram_single_profile_data_from_hash_tag_search(self):
        owner_ids = set()
        print("Total ownerIDs found {}".format(len(owner_ids)))
        for count, each_owner in enumerate(owner_ids):
            print("Processing {}/{}, {}".format(count, len(owner_ids), each_owner))
            is_found = len(set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).distinct(key="ownerId",
                                                                                                filter={
                                                                                                    "ownerId": each_owner}))) > 0
            if is_found:
                print("Continuing data already processed !... {}".format(each_owner))
                continue

            run_input = {
                "usernames": [each_owner]
            }
            try:
                run = self.api_client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
                for item in self.api_client.dataset(run["defaultDatasetId"]).iterate_items():
                    item['ownerId'] = each_owner,
                    MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).insert_data(item)
                    if 'profilePicUrl' in item:
                        _request_url = item['profilePicUrl']
                        _save_path = "{}/{}.png".format(IMAGES.INSTAGRAM, item['username'])
                        shared_util.download_image(_request_url, _save_path)
                        print("Image download requested .. {}".format(_save_path))
                    print("Data inserted:{}".format(item))
            except Exception as ex:
                print("Exception :{}".format(ex))

    def scrape_instagram_single_profile_data_from_keywords_search(self):
        owner_ids = set()
        for posts in MongoDBActor(COLLECTIONS.INSTAGRAM_ACCOUNT_SEARCH).find():
            if "topPosts" in posts:
                top_posts = posts['topPosts']
                for tp in top_posts:
                    if 'ownerId' in tp:
                        owner_ids.add(tp['ownerId'])
            if "latestPosts" in posts:
                latest_posts = posts['latestPosts']
                for tp in latest_posts:
                    if 'ownerId' in tp:
                        owner_ids.add(tp['ownerId'])

        print("Total ownerIDs found {}".format(len(owner_ids)))
        for count, each_owner in enumerate(owner_ids):
            print("Processing {}/{}, {}".format(count, len(owner_ids), each_owner))
            is_found = len(set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).distinct(key="ownerId",
                                                                                                filter={
                                                                                                    "ownerId": each_owner}))) > 0
            if is_found:
                print("Continuing data already processed !... {}".format(each_owner))
                continue

            run_input = {
                "usernames": [each_owner]
            }
            try:
                run = self.api_client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
                for item in self.api_client.dataset(run["defaultDatasetId"]).iterate_items():
                    item['ownerId'] = each_owner,
                    MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).insert_data(item)
                    if 'profilePicUrl' in item:
                        _request_url = item['profilePicUrl']
                        _save_path = "{}/{}.png".format(IMAGES.INSTAGRAM, item['username'])
                        shared_util.download_image(_request_url, _save_path)
                        print("Image download requested .. {}".format(_save_path))
                    print("Data inserted:{}".format(item))
            except Exception as ex:
                print("Exception :{}".format(ex))

    def scrape_you_tube_accounts_from_domain(self, search_keyword):
        run_input = {
            "searchKeywords": search_keyword,
            "maxResults": 100,
            "maxResultsShorts": None,
            "maxResultStreams": None,
            "startUrls": [],
            "subtitlesLanguage": "en",
            "subtitlesFormat": "srt",
        }

        try:
            run = self.api_client.actor("h7sDV53CddomktSi5").call(run_input=run_input)
            for item in self.api_client.dataset(run["defaultDatasetId"]).iterate_items():
                item['search_keyword'] = search_keyword
                item['time'] = shared_util.get_current_time_in_millis()
                item['social_media'] = "youtube"
                print(item)
                MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).insert_data(item)
        except Exception as ex:
            print("Exception :{}".format(ex))

    def collect_each_telegram_account_detail(self):
        telegram_channels = set()
        for val in MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).find():
            if 'telemtr_url' in val:
                found_url = val['telemtr_url']
                found_url = found_url.replace("https://telemetr.io/en/channels/", "")
                if "-" in found_url:
                    _splitter = found_url.split("-")
                    if len(_splitter) < 1:
                        continue
                    telegram_channels.add(_splitter[1].strip())
                else:
                    telegram_channels.add(found_url.strip())

        if None in telegram_channels:
            telegram_channels.remove(None)
        for count, telegram_channel in enumerate(telegram_channels):
            print("Processing {}, {}/{}".format(telegram_channel, count, len(telegram_channels)))

            is_found = len(set(MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_DETAIL).distinct(key="channelId",
                                                                                          filter={
                                                                                              "channelId":
                                                                                                  telegram_channel}))) > 0
            if is_found:
                print("Continuing data already processed !... {}".format(telegram_channel))
                continue

            run_input = {
                "channels": [telegram_channel],
                "postsFrom": 1,
                "postsTo": 200,
                "proxy": {
                    "useApifyProxy": True,
                    "apifyProxyGroups": ["RESIDENTIAL"],
                },
            }

            try:
                run = self.api_client.actor("73JZk4CeKcDsWoJQu").call(run_input=run_input)
                for item in self.api_client.dataset(run["defaultDatasetId"]).iterate_items():
                    item['channelId'] = telegram_channel
                    MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_DETAIL).insert_data(item)
            except Exception as ex:
                print("Exception :{}".format(ex))


if __name__ == "__main__":
    _arg_parser = argparse.ArgumentParser(description="Social Media Data Search")
    _arg_parser.add_argument("-p", "--process_name",
                             action="store",
                             required=True,
                             help="processing function name")

    _arg_value = _arg_parser.parse_args()

    meta_data = SocialMediaDataSearch(_arg_value.process_name)
    meta_data.process()
