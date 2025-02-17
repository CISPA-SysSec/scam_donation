from db_util import MongoDBActor
from constants import COLLECTIONS

import argparse
import json
import os
import shared_util

"""
    DataCreator - Creates data for graph
    This classes processes from MongoDB to collect data for graphing.
    The output of the file is saved in json file for creating the graph which is later run by ```graph_creator.py```.
"""


class DataCreator:
    def __init__(self, function_name):
        self.function_name = function_name

    def process(self):
        if self.function_name == "followers_data":
            self.followers_data_creator()
        elif self.function_name == "date_of_creation_data":
            self.date_of_creation_data_creator()
        elif self.function_name == "post_data_creator":
            self.post_data_creator()

    def get_twitter_user_followers(self, author_id):
        for item in MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).find({"author_id": author_id}):
            if 'followers' in item:
                return int(item['followers'])
        return None

    def get_twitter_user_date_of_creation(self, author_id):
        for item in MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).find({"author_id": author_id}):
            if 'createdAt' in item:
                _found = item['createdAt']
                _split = _found.split(" ")
                _year = _split[-1]
                _year = _year.strip()
                return int(_year)
        return None

    def get_twitter_user_post_count(self, author_id):
        for item in MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).find({"author_id": author_id}):
            if 'statusesCount' in item:
                return int(item['statusesCount'])
        return None

    def get_instagram_user_followers(self, owner_id):
        for item in MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).find({"ownerId": owner_id}):
            if 'followersCount' in item:
                return int(item['followersCount'])
        return None

    def get_instagram_user_post_count(self, owner_id):
        for item in MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).find({"ownerId": owner_id}):
            if 'postsCount' in item:
                return int(item['postsCount'])
        return None

    def get_instagram_user_date_of_creation(self, owner_id):
        _processed_year = set()
        _distinct_latest_post_time_stamp = set(
            MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).distinct(key="latestPosts.timestamp",
                                                                             filter={"ownerId": owner_id}))

        _distinct_video_post_time_stamp = set(
            MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).distinct(key="laestIgtvVideos.timestamp",
                                                                             filter={"ownerId": owner_id}))

        _all = _distinct_latest_post_time_stamp.union(_distinct_video_post_time_stamp)

        if None in _all:
            _all.remove(None)

        for _a in _all:
            if _a:
                time_stamp = _a.split("-")[0]
                time_stamp = time_stamp.strip()
                time_stamp = int(time_stamp)
                _processed_year.add(time_stamp)

        _processed_year = list(_processed_year)
        _processed_year.sort(reverse=False)
        return _processed_year[0]

    def get_facebook_user_followers(self, pageId):
        for item in MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).find({"pageId": pageId}):
            if 'followers' in item:
                return int(item['followers'])
        return None

    def get_facebook_user_date_of_creation(self, pageId):
        for item in MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).find({"pageId": pageId}):
            if 'creation_date' in item:
                _found = item['creation_date']
                _found = _found.split(",")[1]
                _found = _found.strip()
                return int(_found)
        return None

    def get_facebook_user_posts_count(self, pageId):
        for item in MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).find({"pageId": pageId}):
            if 'likes' in item:
                found_likes = int(item['likes'])
                if found_likes == 0:
                    return None
                else:
                    return found_likes
        return None

    def get_telegram_user_followers(self, telemtr_url):
        for item in MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).find({"telemtr_url": telemtr_url}):
            if 'profile_data' in item:
                _profile_data = item['profile_data']
                if 'subscriber' in _profile_data:
                    return int(_profile_data['subscriber'])
        return None

    def get_telegram_user_date_of_creation(self, telemtr_url):
        for item in MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).find({"telemtr_url": telemtr_url}):
            if 'profile_data' in item:
                _profile_data = item['profile_data']
                if 'created_date' in _profile_data:
                    _created_data = _profile_data['created_date']
                    _splitter = _created_data.split("-")
                    _date_ = _splitter[0]
                    _year_ = _date_.split(",")[1]
                    _year_ = _year_.strip()
                    return int(_year_)
        return None

    def get_telegram_user_post_count(self, telemtr_url):
        for item in MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).find({"telemtr_url": telemtr_url}):
            if 'profile_data' in item:
                _profile_data = item['profile_data']
                if 'post_view' in _profile_data:
                    _post_view = _profile_data['post_view']
                    try:
                        _post_view = int(int(_post_view) * 0.05)
                        if _post_view < 1:
                            _post_view = 1
                        return _post_view
                    except:
                        pass
                    return None
        return None

    def get_you_tube_user_followers(self, id):
        for item in MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find({"id": id}):
            if 'numberOfSubscribers' in item:
                return int(item['numberOfSubscribers'])
        return None

    def get_you_tube_user_posts_count(self, id):
        for item in MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find({"id": id}):
            if 'commentsCount' in item:
                return int(item['commentsCount'])
        return None

    def get_you_tube_user_date_of_creation(self, id):
        for item in MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find({"id": id}):
            if 'date' in item:
                _found_date = item['date']
                _year = _found_date.split("-")[0]
                _year = _year.strip()
                return int(_year)
        return None

    def followers_data_creator(self):
        _collections = shared_util.get_all_collections()
        _all_data = {}
        for _each_col in _collections:
            print("Processing {}".format(_each_col))
            _each_data = []
            _abuse_candidate_id = shared_util.get_mega_collection_abuse_candidate_author_id(_each_col)
            for _each_abuse_candidate in _abuse_candidate_id:
                _found_number = None
                if 'twitter' in _each_col:
                    _found_number = self.get_twitter_user_followers(_each_abuse_candidate)
                elif 'instagram' in _each_col:
                    _found_number = self.get_instagram_user_followers(_each_abuse_candidate)
                elif 'telegram' in _each_col:
                    _found_number = self.get_telegram_user_followers(_each_abuse_candidate)
                elif 'youtube' in _each_col:
                    _found_number = self.get_you_tube_user_followers(_each_abuse_candidate)
                elif 'facebook' in _each_col:
                    _found_number = self.get_facebook_user_followers(_each_abuse_candidate)
                else:
                    raise Exception("Unsupported request")
                if type(_found_number) is int:
                    _each_data.append(_found_number)
            _all_data[_each_col] = _each_data
        f_dir = "data/graph/graph_data/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
        with open("{}/follower_data.json".format(f_dir), "w") as f_write:
            json.dump(_all_data, f_write, indent=4)

    def date_of_creation_data_creator(self):
        _collections = shared_util.get_all_collections()
        _all_data = {}
        for _each_col in _collections:
            print("Processing {}".format(_each_col))
            _each_data = []
            _abuse_candidate_id = shared_util.get_mega_collection_abuse_candidate_author_id(_each_col)
            for _each_abuse_candidate in _abuse_candidate_id:
                _found_number = None
                if 'twitter' in _each_col:
                    _found_number = self.get_twitter_user_date_of_creation(_each_abuse_candidate)
                elif 'instagram' in _each_col:
                    _found_number = self.get_instagram_user_date_of_creation(_each_abuse_candidate)
                elif 'telegram' in _each_col:
                    _found_number = self.get_telegram_user_date_of_creation(_each_abuse_candidate)
                elif 'youtube' in _each_col:
                    _found_number = self.get_you_tube_user_date_of_creation(_each_abuse_candidate)
                elif 'facebook' in _each_col:
                    _found_number = self.get_facebook_user_date_of_creation(_each_abuse_candidate)
                else:
                    raise Exception("Unsupported request")
                if type(_found_number) is int:
                    _each_data.append(_found_number)
            _all_data[_each_col] = _each_data
        f_dir = "data/graph/graph_data/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
        with open("{}/date_of_creation.json".format(f_dir), "w") as f_write:
            json.dump(_all_data, f_write, indent=4)

    def post_data_creator(self):
        _collections = shared_util.get_all_collections()
        _all_data = {}
        for _each_col in _collections:
            print("Processing {}".format(_each_col))
            _each_data = []
            _abuse_candidate_id = shared_util.get_mega_collection_abuse_candidate_author_id(_each_col)
            for _each_abuse_candidate in _abuse_candidate_id:
                _found_number = None
                if 'twitter' in _each_col:
                    _found_number = self.get_twitter_user_post_count(_each_abuse_candidate)
                elif 'instagram' in _each_col:
                    _found_number = self.get_instagram_user_post_count(_each_abuse_candidate)
                elif 'telegram' in _each_col:
                    _found_number = self.get_telegram_user_post_count(_each_abuse_candidate)
                elif 'youtube' in _each_col:
                    _found_number = self.get_you_tube_user_posts_count(_each_abuse_candidate)
                elif 'facebook' in _each_col:
                    _found_number = self.get_facebook_user_posts_count(_each_abuse_candidate)
                else:
                    raise Exception("Unsupported request")
                if type(_found_number) is int:
                    _each_data.append(_found_number)
            _all_data[_each_col] = _each_data
        f_dir = "data/graph/graph_data/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
        with open("{}/posts_data_creation.json".format(f_dir), "w") as f_write:
            json.dump(_all_data, f_write, indent=4)


if __name__ == "__main__":
    _arg_parser = argparse.ArgumentParser(description="Graph data processor")
    _arg_parser.add_argument("-f", "--function_name",
                             action="store",
                             required=True,
                             help="function_name")

    _arg_value = _arg_parser.parse_args()

    _dc = DataCreator(_arg_value.function_name)
    _dc.process()
