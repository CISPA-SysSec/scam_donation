from constants import COLLECTIONS
from db_util import MongoDBActor

import shared_util
import json
import argparse
import os

"""
    In this code section, we provide analysis of various sections of table include pre-processing of data, 
    table creation, fraud channels, and others.
"""


class Analysis:
    def __init__(self, function):
        self.function = function

    def process(self):
        if Analysis.social_media_hash_tags.__name__ == self.function:
            self.social_media_hash_tags()
        elif Analysis.raw_data_information.__name__ == self.function:
            self.raw_data_information()
        elif Analysis.create_raw_data_table.__name__ == self.function:
            self.create_raw_data_table()
        elif Analysis.create_pre_processing_data_table.__name__ == self.function:
            self.create_pre_processing_data_table()
        elif Analysis.create_mega_table_overall_posts_and_accounts.__name__ == self.function:
            self.create_mega_table_overall_posts_and_accounts()
        elif Analysis.create_mega_table_fraud_email_url_phone_number_crypto_information_data.__name__ == self.function:
            self.create_mega_table_fraud_email_url_phone_number_crypto_information_data()
        elif Analysis.create_all_scam_donation_emails_key_value_data.__name__ == self.function:
            self.create_all_scam_donation_emails_key_value_data()
        elif Analysis.create_all_scam_donation_emails_data.__name__ == self.function:
            self.create_all_scam_donation_emails_data()
        elif Analysis.create_all_scam_donation_phone_data.__name__ == self.function:
            self.create_all_scam_donation_phone_data()
        elif Analysis.create_all_scam_donation_url_data.__name__ == self.function:
            self.create_all_scam_donation_url_data()
        elif Analysis.create_all_scam_donation_phone_key_value_data.__name__ == self.function:
            self.create_all_scam_donation_phone_key_value_data()
        elif Analysis.create_all_scam_donation_urls_key_value_data.__name__ == self.function:
            self.create_all_scam_donation_urls_key_value_data()
        elif Analysis.create_twitter_scam_donation_user_handle_key_value_data.__name__ == self.function:
            self.create_twitter_scam_donation_user_handle_key_value_data()
        elif Analysis.create_instagram_scam_donation_user_handle_key_value_data.__name__ == self.function:
            self.create_instagram_scam_donation_user_handle_key_value_data()
        elif Analysis.create_facebook_scam_donation_user_handle_key_value_data.__name__ == self.function:
            self.create_facebook_scam_donation_user_handle_key_value_data()
        elif Analysis.create_you_tube_scam_donation_user_handle_key_value_data.__name__ == self.function:
            self.create_you_tube_scam_donation_user_handle_key_value_data()
        elif Analysis.create_telegram_scam_donation_user_handle_key_value_data.__name__ == self.function:
            self.create_telegram_scam_donation_user_handle_key_value_data()
        elif Analysis.combine_produced_categories_result.__name__ == self.function:
            self.combine_produced_categories_result()
        elif Analysis.combine_produced_location_result.__name__ == self.function:
            self.combine_produced_location_result()
        elif Analysis.combine_produced_profile_description_result.__name__ == self.function:
            self.combine_produced_profile_description_result()

    def combine_produced_profile_description_result(self):
        files = [
            "report/profile_meta_data/youtube/text.json",
            "report/profile_meta_data/twitter/description.json",
            "report/profile_meta_data/telegram/profile_data.channel_description.txt.json",
            "report/profile_meta_data/instagram/biography.json",
            "report/profile_meta_data/facebook/info.json"
        ]

        _all_data = {}
        _all_count = 0
        for f in files:
            with open(f, "r") as f_read:
                _data = json.load(f_read)

            for k, v in _data.items():
                if k not in _all_data:
                    _all_data[k] = v
                else:
                    _all_data[k] = v + _all_data[k]
                _all_count = _all_count + v

        _lst = []
        for each_k, each_v in _all_data.items():
            _lst.append((each_k, each_v))
        _lst.sort(key=lambda tup: tup[1], reverse=True)

        _sort_type = {}
        for each in _lst:
            _sort_type[each[0]] = each[1]

        f_dir = "report/profile_meta_data/combined/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)

        with open("{}/description.json".format(f_dir), "w") as f_write:
            json.dump(_sort_type, f_write, indent=4)

        print(_all_count)

    def combine_produced_business_result(self):
        files = [
            "report/profile_meta_data/youtube/text.json",
            "report/profile_meta_data/twitter/description.json",
            "report/profile_meta_data/telegram/profile_data.channel_description.txt.json"
        ]

        _all_data = {}
        _all_count = 0
        for f in files:
            with open(f, "r") as f_read:
                _data = json.load(f_read)

            for k, v in _data.items():
                if k not in _all_data:
                    _all_data[k] = v
                else:
                    _all_data[k] = v + _all_data[k]
                _all_count = _all_count + v

        _lst = []
        for each_k, each_v in _all_data.items():
            _lst.append((each_k, each_v))
        _lst.sort(key=lambda tup: tup[1], reverse=True)

        _sort_type = {}
        for each in _lst:
            _sort_type[each[0]] = each[1]

        f_dir = "report/profile_meta_data/combined/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)

        with open("{}/location.json".format(f_dir), "w") as f_write:
            json.dump(_sort_type, f_write, indent=4)

        print(_all_count)

    def combine_produced_location_result(self):
        files = [
            "report/profile_meta_data/youtube/location.json",
            "report/profile_meta_data/twitter/location.json",
            "report/profile_meta_data/telegram/input.country.json"
        ]

        _all_data = {}
        _all_count = 0
        for f in files:
            with open(f, "r") as f_read:
                _data = json.load(f_read)

            for k, v in _data.items():
                if k not in _all_data:
                    _all_data[k] = v
                else:
                    _all_data[k] = v + _all_data[k]
                _all_count = _all_count + v

        _lst = []
        for each_k, each_v in _all_data.items():
            _lst.append((each_k, each_v))
        _lst.sort(key=lambda tup: tup[1], reverse=True)

        _sort_type = {}
        for each in _lst:
            _sort_type[each[0]] = each[1]

        f_dir = "report/profile_meta_data/combined/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)

        with open("{}/location.json".format(f_dir), "w") as f_write:
            json.dump(_sort_type, f_write, indent=4)

        print(_all_count)

    def combine_produced_categories_result(self):
        files = [
            "report/profile_meta_data/facebook/categories.json",
            "report/profile_meta_data/twitter/professional.category.name.json",
            "report/profile_meta_data/instagram/businessCategoryName.json"
        ]

        _all_data = {}
        _all_count = 0
        for f in files:
            with open(f, "r") as f_read:
                _data = json.load(f_read)

            for k, v in _data.items():
                if k not in _all_data:
                    _all_data[k] = v
                else:
                    _all_data[k] = v + _all_data[k]
                _all_count = _all_count + v

        f_dir = "report/profile_meta_data/combined/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)

        with open("{}/categories.json".format(f_dir), "w") as f_write:
            json.dump(_all_data, f_write, indent=4)

        print(_all_count)

    def create_telegram_scam_donation_user_handle_key_value_data(self):
        _key_values = [
            "profile_data.channel_description.txt",
            "input.country"
        ]

        _author_ids = set(shared_util.get_mega_collection_abuse_candidate_author_id(COLLECTIONS.TELEGRAM_MEGA_DATA))
        for each_key in _key_values:
            print("Processing {}".format(each_key))
            _all_json = {}
            for each_author in _author_ids:
                _distinct_val = MongoDBActor(COLLECTIONS.TELEGRAM_ACCOUNT_SEARCH).distinct(key=each_key,
                                                                                           filter={
                                                                                               "telemtr_url": each_author})
                if None in _distinct_val:
                    _distinct_val.remove(None)
                if len(_distinct_val) > 0:
                    _found = _distinct_val[0]
                    if _found:
                        if _found not in _all_json:
                            _all_json[_found] = 1
                        else:
                            _all_json[_found] = 1 + _all_json[_found]

            _lst = []
            for each_k, each_v in _all_json.items():
                _lst.append((each_k, each_v))
            _lst.sort(key=lambda tup: tup[1], reverse=True)
            _recreate_again = {}

            _sort_type = {}
            for each in _lst:
                _sort_type[each[0]] = each[1]

            f_dir = "report/profile_meta_data/telegram/"
            if not os.path.exists(f_dir):
                os.makedirs(f_dir)
            with open("{}/{}.json".format(f_dir, each_key), "w") as f_write:
                json.dump(_sort_type, f_write, indent=4)

    def create_you_tube_scam_donation_user_handle_key_value_data(self):
        _key_values = [
            "title",
            "type",
            "likes",
            "location",
            "channelName",
            "duration",
            "text",
            "descriptionLinks.url",
            "descriptionLinks.text",
            "isMonetized"
        ]

        _author_ids = set(shared_util.get_mega_collection_abuse_candidate_author_id(COLLECTIONS.YOU_TUBE_MEGA_DATA))
        for each_key in _key_values:
            print("Processing {}".format(each_key))
            _all_json = {}
            for each_author in _author_ids:
                _distinct_val = MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(key=each_key,
                                                                                          filter={
                                                                                              "id": each_author})
                if None in _distinct_val:
                    _distinct_val.remove(None)
                if len(_distinct_val) > 0:
                    _found = _distinct_val[0]
                    if _found:
                        if _found not in _all_json:
                            _all_json[_found] = 1
                        else:
                            _all_json[_found] = 1 + _all_json[_found]

            _lst = []
            for each_k, each_v in _all_json.items():
                _lst.append((each_k, each_v))
            _lst.sort(key=lambda tup: tup[1], reverse=True)
            _recreate_again = {}

            _sort_type = {}
            for each in _lst:
                _sort_type[each[0]] = each[1]

            f_dir = "report/profile_meta_data/youtube/"
            if not os.path.exists(f_dir):
                os.makedirs(f_dir)
            with open("{}/{}.json".format(f_dir, each_key), "w") as f_write:
                json.dump(_sort_type, f_write, indent=4)

    def create_facebook_scam_donation_user_handle_key_value_data(self):
        _key_values = [
            "likes",
            "messenger",
            "priceRange",
            "title",
            "pageName",
            "email",
            "website",
            "rating",
            "ratingOverall",
            "ratingCount",
            "followers",
            "ad_status",
            "pageAdLibrary.is_business_page_active",
            "categories",
            "info",
            "about_me.text"
        ]

        _author_ids = set(shared_util.get_mega_collection_abuse_candidate_author_id(COLLECTIONS.FACEBOOK_MEGA_DATA))
        for each_key in _key_values:
            print("Processing {}".format(each_key))
            _all_json = {}
            for each_author in _author_ids:
                _distinct_val = MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).distinct(key=each_key,
                                                                                                filter={
                                                                                                    "pageId": each_author})
                if None in _distinct_val:
                    _distinct_val.remove(None)
                if len(_distinct_val) > 0:
                    _found = _distinct_val[0]
                    if _found:
                        if _found not in _all_json:
                            _all_json[_found] = 1
                        else:
                            _all_json[_found] = 1 + _all_json[_found]

            _lst = []
            for each_k, each_v in _all_json.items():
                _lst.append((each_k, each_v))
            _lst.sort(key=lambda tup: tup[1], reverse=True)
            _recreate_again = {}

            _sort_type = {}
            for each in _lst:
                _sort_type[each[0]] = each[1]

            f_dir = "report/profile_meta_data/facebook/"
            if not os.path.exists(f_dir):
                os.makedirs(f_dir)
            with open("{}/{}.json".format(f_dir, each_key), "w") as f_write:
                json.dump(_sort_type, f_write, indent=4)

    def create_instagram_scam_donation_user_handle_key_value_data(self):
        _key_values = [
            "fullName",
            "biography",
            "hasChannel",
            "isBusinessAccount",
            "businessCategoryName",
            "private",
            "postsCount",
            "externalUrl"
        ]

        _author_ids = set(shared_util.get_mega_collection_abuse_candidate_author_id(COLLECTIONS.INSTAGRAM_MEGA_DATA))
        for each_key in _key_values:
            print("Processing {}".format(each_key))
            _all_json = {}
            for each_author in _author_ids:
                _distinct_val = MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).distinct(key=each_key,
                                                                                                 filter={
                                                                                                     "ownerId": each_author})
                if None in _distinct_val:
                    _distinct_val.remove(None)
                if len(_distinct_val) > 0:
                    _found = _distinct_val[0]
                    if _found:
                        if _found not in _all_json:
                            _all_json[_found] = 1
                        else:
                            _all_json[_found] = 1 + _all_json[_found]

            _lst = []
            for each_k, each_v in _all_json.items():
                _lst.append((each_k, each_v))
            _lst.sort(key=lambda tup: tup[1], reverse=True)
            _recreate_again = {}

            _sort_type = {}
            for each in _lst:
                _sort_type[each[0]] = each[1]

            f_dir = "report/profile_meta_data/instagram/"
            if not os.path.exists(f_dir):
                os.makedirs(f_dir)
            with open("{}/{}.json".format(f_dir, each_key), "w") as f_write:
                json.dump(_sort_type, f_write, indent=4)

    def create_twitter_scam_donation_user_handle_key_value_data(self):
        _key_values = [
            "canDm",
            "professional.professional_type",
            "professional.category.name",
            "location",
            "protected",
            "canMediaTag",
            "type",
            "description",
            "name"
        ]
        _author_ids = set(shared_util.get_mega_collection_abuse_candidate_author_id(COLLECTIONS.TWITTER_MEGA_DATA))
        for each_key in _key_values:
            print("Processing {}".format(each_key))
            _all_json = {}
            for each_author in _author_ids:
                _distinct_val = MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).distinct(key=each_key,
                                                                                       filter={
                                                                                           "author_id": each_author})
                if None in _distinct_val:
                    _distinct_val.remove(None)
                if len(_distinct_val) > 0:
                    _found = _distinct_val[0]
                    if _found:
                        if _found not in _all_json:
                            _all_json[_found] = 1
                        else:
                            _all_json[_found] = 1 + _all_json[_found]

            _lst = []
            for each_k, each_v in _all_json.items():
                _lst.append((each_k, each_v))
            _lst.sort(key=lambda tup: tup[1], reverse=True)
            _recreate_again = {}

            _sort_type = {}
            for each in _lst:
                _sort_type[each[0]] = each[1]

            f_dir = "report/profile_meta_data/twitter/"
            if not os.path.exists(f_dir):
                os.makedirs(f_dir)
            with open("{}/{}.json".format(f_dir, each_key), "w") as f_write:
                json.dump(_sort_type, f_write, indent=4)

    def create_all_scam_donation_urls_key_value_data(self):
        collections = shared_util.get_all_collections()
        _key_values = [
            "network_info.tld",
            "network_info.asn",
            "network_info.ip",
            "network_info.owner",
            "network_info.cc",
            "domain_creation"
        ]

        for each_key in _key_values:
            print("Processing {}".format(each_key))
            _each_key_data = {}
            _all = {}
            for each_col in collections:
                print("Processing {}".format(each_col))
                _aggregated_each_social_media = {}
                _each_social_data = {}
                _phones = shared_util.get_mega_collection_fraud_urls(each_col)
                for each_phone in _phones:
                    found_data = list(shared_util.get_distinct_vt_urls_from_key_value_provided(each_key, each_phone))
                    if len(found_data) == 0:
                        continue
                    found_data = found_data[0]
                    if found_data not in _each_social_data:
                        _each_social_data[found_data] = [each_phone]
                    else:
                        _each_social_data[found_data] = list(set([each_phone] + _each_social_data[found_data]))
                    if found_data not in _all:
                        _all[found_data] = [each_phone]
                    else:
                        _all[found_data] = list(set([each_phone] + _all[found_data]))
                for k, v in _each_social_data.items():
                    _aggregated_each_social_media[k] = len(v)

                _each_key_data[each_col] = _aggregated_each_social_media

            _aggreagte_all_ = {}
            for k, v in _all.items():
                _aggreagte_all_[k] = len(v)

            _each_key_data['all'] = _aggreagte_all_

            _sort_type = {}
            for each_k, each_v in _each_key_data.items():
                _lst = []
                for e_v_k, e_v_v in each_v.items():
                    _lst.append((e_v_k, e_v_v))
                _lst.sort(key=lambda tup: tup[1], reverse=True)
                _recreate_again = {}
                for _l in _lst:
                    _recreate_again[_l[0]] = _l[1]
                _sort_type[each_k] = _recreate_again

            f_dir = "report/fraud_urls_evaluation/"
            if not os.path.exists(f_dir):
                os.makedirs(f_dir)
            with open("{}/{}.json".format(f_dir, each_key), "w") as f_write:
                json.dump(_sort_type, f_write, indent=4)

    def create_all_scam_donation_phone_key_value_data(self):
        collections = shared_util.get_all_collections()
        _key_values = [
            "output.fraud_score",
            "output.recent_abuse",
            "output.VOIP",
            "output.prepaid",
            "output.active",
            "output.carrier",
            "output.line_type",
            "output.sms_domain",
            "output.mnc",
            "output.mcc",
            "output.leaked",
            "output.spammer",
            "output.do_not_call",
            "output.sms_email",
            "output_abstract_api.country.code",
            "output_abstract_api.country.name",
            "output_abstract_api.country.type",
            "output_abstract_api.carrier"
        ]

        for each_key in _key_values:
            print("Processing {}".format(each_key))
            _each_key_data = {}
            _all = {}
            for each_col in collections:
                print("Processing {}".format(each_col))
                _aggregated_each_social_media = {}
                _each_social_data = {}
                _phones = shared_util.get_mega_collection_fraud_phone(each_col)
                for each_phone in _phones:
                    found_data = list(shared_util.get_distinct_phone_from_key_value_provided(each_key, each_phone))
                    if len(found_data) == 0:
                        continue
                    found_data = found_data[0]
                    if found_data not in _each_social_data:
                        _each_social_data[found_data] = [each_phone]
                    else:
                        _each_social_data[found_data] = list(set([each_phone] + _each_social_data[found_data]))
                    if found_data not in _all:
                        _all[found_data] = [each_phone]
                    else:
                        _all[found_data] = list(set([each_phone] + _all[found_data]))
                for k, v in _each_social_data.items():
                    _aggregated_each_social_media[k] = len(v)

                _each_key_data[each_col] = _aggregated_each_social_media

            _aggreagte_all_ = {}
            for k, v in _all.items():
                _aggreagte_all_[k] = len(v)

            _each_key_data['all'] = _aggreagte_all_

            _sort_type = {}
            for each_k, each_v in _each_key_data.items():
                _lst = []
                for e_v_k, e_v_v in each_v.items():
                    _lst.append((e_v_k, e_v_v))
                _lst.sort(key=lambda tup: tup[1], reverse=True)
                _recreate_again = {}
                for _l in _lst:
                    _recreate_again[_l[0]] = _l[1]
                _sort_type[each_k] = _recreate_again

            f_dir = "report/fraud_phone_evaluation/"
            if not os.path.exists(f_dir):
                os.makedirs(f_dir)
            with open("{}/{}.json".format(f_dir, each_key), "w") as f_write:
                json.dump(_sort_type, f_write, indent=4)

    def create_all_scam_donation_emails_key_value_data(self):
        collections = shared_util.get_all_collections()
        _key_values = [
            "output.first_seen.human",
            "output.disposable",
            "output.smtp_score",
            "output.dns_valid",
            "output.honeypot",
            "output.deliverability",
            "output.frequent_complainer",
            "output.recent_abuse",
            "output.fraud_score",
            "output.leaked",
            "output.first_seen.timestamp",
            "output.first_seen.iso",
            "output.risky_tld"
        ]

        for each_key in _key_values:
            print("Processing {}".format(each_key))
            _each_key_data = {}
            _all = {}
            for each_col in collections:
                print("Processing {}".format(each_col))
                _aggregated_each_social_media = {}
                _each_social_data = {}
                _emails = shared_util.get_mega_collection_fraud_email(each_col)
                for each_email in _emails:
                    found_data = list(shared_util.get_distinct_email_from_key_value_provided(each_key, each_email))
                    if len(found_data) == 0:
                        continue
                    found_data = found_data[0]
                    if found_data not in _each_social_data:
                        _each_social_data[found_data] = [each_email]
                    else:
                        _each_social_data[found_data] = list(set([each_email] + _each_social_data[found_data]))
                    if found_data not in _all:
                        _all[found_data] = [each_email]
                    else:
                        _all[found_data] = list(set([each_email] + _all[found_data]))
                for k, v in _each_social_data.items():
                    _aggregated_each_social_media[k] = len(v)

                _each_key_data[each_col] = _aggregated_each_social_media

            _aggreagte_all_ = {}
            for k, v in _all.items():
                _aggreagte_all_[k] = len(v)

            _each_key_data['all'] = _aggreagte_all_

            _sort_type = {}
            for each_k, each_v in _each_key_data.items():
                _lst = []
                for e_v_k, e_v_v in each_v.items():
                    _lst.append((e_v_k, e_v_v))
                _lst.sort(key=lambda tup: tup[1], reverse=True)
                _recreate_again = {}
                for _l in _lst:
                    _recreate_again[_l[0]] = _l[1]
                _sort_type[each_k] = _recreate_again

            f_dir = "report/fraud_email_evaluation/"
            if not os.path.exists(f_dir):
                os.makedirs(f_dir)
            with open("{}/{}.json".format(f_dir, each_key), "w") as f_write:
                json.dump(_sort_type, f_write, indent=4)

    def create_all_scam_donation_emails_data(self):
        collections = shared_util.get_all_collections()
        _all_emails = {}
        all_distinct_emails = set()
        for each_col in collections:
            print("Processing {}".format(each_col))
            _emails = shared_util.get_mega_collection_fraud_email(each_col)
            all_distinct_emails = all_distinct_emails.union(_emails)
            _all_emails[each_col] = list(_emails)

        _all_emails['all'] = list(all_distinct_emails)
        f_dir = "report/fraud_emails/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
        for key, values in _all_emails.items():
            cnt = 1
            with open("{}/{}.txt".format(f_dir, key), "w") as f_write:
                for each_email in values:
                    f_write.write("{},{}\n".format(cnt, each_email))
                    cnt = cnt + 1

    def create_all_scam_donation_phone_data(self):
        collections = shared_util.get_all_collections()
        _all_data = {}
        all_distinct_data = set()
        for each_col in collections:
            print("Processing {}".format(each_col))
            found_data = shared_util.get_mega_collection_fraud_phone(each_col)
            all_distinct_data = all_distinct_data.union(found_data)
            _all_data[each_col] = list(found_data)

        _all_data['all'] = list(all_distinct_data)
        f_dir = "report/lists/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
        for key, values in _all_data.items():
            cnt = 1
            with open("{}/{}.txt".format(f_dir, key), "w") as f_write:
                for each_email in values:
                    f_write.write("{},{}\n".format(cnt, each_email))
                    cnt = cnt + 1

    def create_all_scam_donation_url_data(self):
        collections = shared_util.get_all_collections()
        _all_data = {}
        all_distinct_data = set()
        for each_col in collections:
            print("Processing {}".format(each_col))
            found_data = shared_util.get_mega_collection_fraud_urls(each_col)
            all_distinct_data = all_distinct_data.union(found_data)
            _all_data[each_col] = list(found_data)

        _all_data['all'] = list(all_distinct_data)
        f_dir = "report/fraud_urls/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
        for key, values in _all_data.items():
            cnt = 1
            with open("{}/{}.txt".format(f_dir, key), "w") as f_write:
                for each_email in values:
                    f_write.write("{},{}\n".format(cnt, each_email))
                    cnt = cnt + 1

    def create_raw_data_table(self):
        _all_data = {}
        collections_ = {
            COLLECTIONS.INSTAGRAM_SINGLE_POST: {'id': "ownerId", 'text': 'text'},
            COLLECTIONS.DONATION_TEXT_SEARCH: {'id': "author_id", 'text': 'text'},
            COLLECTIONS.TELEGRAM_SINGLE_POST: {'id': "telemtr_url", 'text': 'text'},
            COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH: {'id': "id", 'text': 'text'},
            COLLECTIONS.FACEBOOK_SINGLE_POST: {'id': "id", 'text': 'text'}
        }

        _total_accts = 0
        _total_posts = 0
        for each_key, values in collections_.items():
            print('Processing {}'.format(each_key))
            _author_id = values['id']
            _text = values['text']
            _all_author = set()
            _all_posts = []
            for item in MongoDBActor(each_key).find():
                if _author_id in item:
                    _all_author.add(item[_author_id])
                if _text in item:
                    _all_posts.append(item[_text])
            _all_data[each_key] = {'accounts': len(_all_author), 'posts': len(_all_posts)}

            _total_accts = _total_accts + len(_all_author)
            _total_posts = _total_posts + len(_all_posts)

        _all_data['all'] = {'accounts': _total_accts, 'all_posts': _total_posts}
        f_dir = "report/overall_table/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
        with open("{}/table_1.json".format(f_dir), "w") as f_write:
            json.dump(_all_data, f_write, indent=4)

    def create_overview_table(self):
        _collections = shared_util.get_all_collections()
        _all_json = {}

        _all_json = {}
        _all_fraud_email = set()
        _all_fraud_phone = set()
        _all_fraud_urls = set()
        _all_crypto_address = set()

        _all_fraud_id_having_email = set()
        _all_fraud_id_having_phone = set()
        _all_fraud_id_having_urls = set()
        _all_id_having_crypto = set()

        _all_abuse_candidate = set()

        for each_col in _collections:
            print("Processing {}".format(each_col))
            _fraud_email_accts = shared_util.get_mega_collection_id_containing_fraud_email(each_col)
            _fraud_emails = shared_util.get_mega_collection_fraud_email(each_col)
            _all_emails = shared_util.get_all_found_email_from_social_media(each_col)

            _all_fraud_email = _fraud_emails.union(_all_fraud_email)
            _all_fraud_id_having_email = _all_fraud_id_having_email.union(_fraud_email_accts)

            _fraud_phone_accts = shared_util.get_mega_collection_id_containing_fraud_phone(each_col)
            _fraud_phone = shared_util.get_mega_collection_fraud_phone(each_col)
            _all_phone = shared_util.get_all_found_phone_number_from_social_media(each_col)

            _all_fraud_phone = _all_fraud_phone.union(_fraud_phone)
            _all_fraud_id_having_phone = _all_fraud_id_having_phone.union(_fraud_phone_accts)

            _fraud_urls_accts = shared_util.get_mega_collection_id_containing_fraud_urls(each_col)
            _fraud_urls = shared_util.get_mega_collection_fraud_urls(each_col)
            _all_found_url = shared_util.get_vt_

            _all_fraud_urls = _all_fraud_urls.union(_fraud_urls)
            _all_fraud_id_having_urls = _all_fraud_id_having_urls.union(_fraud_urls_accts)

            _crypto_address = shared_util.get_mega_collection_crypto(each_col)
            _crytpo_address_author_ids = shared_util.get_mega_collection_id_containing_crypto(each_col)

            _all_crypto_address = _all_crypto_address.union(_crypto_address)
            _all_id_having_crypto = _crytpo_address_author_ids.union(_all_id_having_crypto)

            _abuse_candidate = shared_util.get_mega_collection_abuse_candidate_author_id(each_col)
            _all_abuse_candidate = _all_abuse_candidate.union(_abuse_candidate)

            _all_json[each_col] = {'fraud_email': len(_fraud_emails),
                                   'fraud_email_author_id': len(_fraud_email_accts),
                                   'fraud_url': len(_fraud_urls),
                                   'fraud_url_author_id': len(_fraud_urls_accts),
                                   'fraud_phone': len(_fraud_phone),
                                   'fraud_phone_author_id': len(_fraud_phone_accts),
                                   'crytpo_address': len(_crypto_address),
                                   'crypto_author_id': len(_crytpo_address_author_ids),
                                   'abuse_candidate': len(_abuse_candidate)
                                   }
        _all_json['all'] = {'fraud_email': len(_all_fraud_email),
                            'fraud_email_author_id': len(_all_fraud_id_having_email),
                            'fraud_url': len(_all_fraud_urls),
                            'fraud_url_author_id': len(_all_fraud_id_having_urls),
                            'fraud_phone': len(_all_fraud_phone),
                            'fraud_phone_author_id': len(_all_fraud_id_having_phone),
                            'crytpo_address': len(_all_crypto_address),
                            'crypto_author_id': len(_all_id_having_crypto),
                            'abuse_candidate': len(_all_abuse_candidate)
                            }
        f_dir = "report/preprocess_table/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
        with open("{}/create_mega_table_fraud_email_url_phone_number_crypto_information_data.json".format(f_dir),
                  "w") as f_write:
            json.dump(_all_json, f_write, indent=4)

    def create_mega_table_fraud_email_url_phone_number_crypto_information_data(self):
        _collections = shared_util.get_all_collections()

        _all_json = {}
        _all_fraud_email = set()
        _all_fraud_phone = set()
        _all_fraud_urls = set()
        _all_crypto_address = set()

        _all_fraud_id_having_email = set()
        _all_fraud_id_having_phone = set()
        _all_fraud_id_having_urls = set()
        _all_id_having_crypto = set()

        _all_abuse_candidate = set()

        for each_col in _collections:
            print("Processing {}".format(each_col))
            _fraud_email_accts = shared_util.get_mega_collection_id_containing_fraud_email(each_col)
            _fraud_emails = shared_util.get_mega_collection_fraud_email(each_col)

            _all_fraud_email = _fraud_emails.union(_all_fraud_email)
            _all_fraud_id_having_email = _all_fraud_id_having_email.union(_fraud_email_accts)

            _fraud_phone_accts = shared_util.get_mega_collection_id_containing_fraud_phone(each_col)
            _fraud_phone = shared_util.get_mega_collection_fraud_phone(each_col)

            _all_fraud_phone = _all_fraud_phone.union(_fraud_phone)
            _all_fraud_id_having_phone = _all_fraud_id_having_phone.union(_fraud_phone_accts)

            _fraud_urls_accts = shared_util.get_mega_collection_id_containing_fraud_urls(each_col)
            _fraud_urls = shared_util.get_mega_collection_fraud_urls(each_col)

            _all_fraud_urls = _all_fraud_urls.union(_fraud_urls)
            _all_fraud_id_having_urls = _all_fraud_id_having_urls.union(_fraud_urls_accts)

            _crypto_address = shared_util.get_mega_collection_crypto(each_col)
            _crytpo_address_author_ids = shared_util.get_mega_collection_id_containing_crypto(each_col)

            _all_crypto_address = _all_crypto_address.union(_crypto_address)
            _all_id_having_crypto = _crytpo_address_author_ids.union(_all_id_having_crypto)

            _abuse_candidate = shared_util.get_mega_collection_abuse_candidate_author_id(each_col)
            _all_abuse_candidate = _all_abuse_candidate.union(_abuse_candidate)

            _all_json[each_col] = {'fraud_email': len(_fraud_emails),
                                   'fraud_email_author_id': len(_fraud_email_accts),
                                   'fraud_url': len(_fraud_urls),
                                   'fraud_url_author_id': len(_fraud_urls_accts),
                                   'fraud_phone': len(_fraud_phone),
                                   'fraud_phone_author_id': len(_fraud_phone_accts),
                                   'crytpo_address': len(_crypto_address),
                                   'crypto_author_id': len(_crytpo_address_author_ids),
                                   'abuse_candidate': len(_abuse_candidate)
                                   }
        _all_json['all'] = {'fraud_email': len(_all_fraud_email),
                            'fraud_email_author_id': len(_all_fraud_id_having_email),
                            'fraud_url': len(_all_fraud_urls),
                            'fraud_url_author_id': len(_all_fraud_id_having_urls),
                            'fraud_phone': len(_all_fraud_phone),
                            'fraud_phone_author_id': len(_all_fraud_id_having_phone),
                            'crytpo_address': len(_all_crypto_address),
                            'crypto_author_id': len(_all_id_having_crypto),
                            'abuse_candidate': len(_all_abuse_candidate)
                            }
        f_dir = "report/preprocess_table/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
        with open("{}/create_mega_table_fraud_email_url_phone_number_crypto_information_data.json".format(f_dir),
                  "w") as f_write:
            json.dump(_all_json, f_write, indent=4)

    def create_mega_table_overall_posts_and_accounts(self):
        _collections = shared_util.get_all_collections()
        _all_data = {}
        _all_acc = set()
        _all_posts = []

        _all_distinct_posts = set()

        for each_col in _collections:
            print("Processing {}".format(each_col))
            _accts = shared_util.get_mega_collection_accounts(each_col)
            _posts = shared_util.get_mega_collection_posts(each_col)
            _all_acc = _all_acc.union(_accts)
            _all_posts = _all_posts + _posts
            _all_data[each_col] = {'acct': len(_accts), 'posts': len(_posts), 'distinct_posts': len(set(_posts))}
        _all_data['all'] = {'acct': len(_all_acc), 'posts': len(_all_posts),
                            'distinct_posts': len(list(set(_all_posts)))}
        f_dir = "report/preprocess_table/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
        with open("{}/table_2.json".format(f_dir), "w") as f_write:
            json.dump(_all_data, f_write, indent=4)

    def create_pre_processing_data_table(self):
        _all_data = {}
        collections_ = {
            COLLECTIONS.INSTAGRAM_SINGLE_POST: {'id': "ownerId", 'text': 'text'},
            COLLECTIONS.DONATION_TEXT_SEARCH: {'id': "author_id", 'text': 'text'},
            COLLECTIONS.TELEGRAM_SINGLE_POST: {'id': "telemtr_url", 'text': 'text'},
            COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH: {'id': "id", 'text': 'text'},
            COLLECTIONS.FACEBOOK_SINGLE_POST: {'id': "id", 'text': 'text'}
        }

        _all_accounts = set()
        _all_texts = []

        combined_accounts = set()
        combined_posts = []

        _total_donation_accts = set()
        _total_donation_posts = []

        _total_verified_accts = set()
        _total_verified_posts = []

        _all_fb_account = shared_util.get_facebook_verified_author_ids()
        _all_insta_account = shared_util.get_instagram_verified_owner_ids()
        _all_twitter_account = shared_util.get_twitter_verified_author_ids()
        _all_youtube_account = shared_util.get_you_tube_verified_author_ids()
        _all_tele_account = shared_util.get_telegram_verified_author_ids()
        _all_verified_account = set(_all_fb_account).union(set(_all_insta_account)).union(
            set(_all_twitter_account)).union(set(_all_youtube_account)).union(set(_all_tele_account))

        for each_key, values in collections_.items():
            print('Processing {}'.format(each_key))
            _author_id = values['id']
            _text = values['text']

            _social_media_accounts = set()
            _social_media_posts = []

            _donation_context_account = set()
            _donation_context_text = []
            _verified_account = set()
            _verified_text = []

            for item in MongoDBActor(each_key).find():
                do_add = True
                if _author_id not in item:
                    continue
                _acct_id = item[_author_id]
                _social_media_accounts.add(_acct_id)
                _social_media_posts.append(item[_text])
                if 'is_donation_context_text' in item:
                    _found_context = item['is_donation_context_text']
                    if _found_context:
                        _donation_context_account.add(_acct_id)
                        _donation_context_text.append(item[_text])
                        _total_donation_accts.add(_acct_id)
                        _total_donation_posts.append(item[_text])
                        combined_accounts.add(_acct_id)
                        combined_posts.append(item[_text])
                        do_add = False
                if _acct_id in _all_verified_account:
                    _verified_account.add(_acct_id)
                    _verified_text.append(item[_text])
                    _total_verified_accts.add(_acct_id)
                    _total_verified_posts.append(item[_text])
                    combined_accounts.add(_acct_id)
                    if do_add:  # ensure non-duplicate
                        combined_posts.append(item[_text])

            _all_data[each_key] = {'donation_context_accounts': len(_donation_context_account),
                                   'donation_context_posts': len(_donation_context_text),
                                   'verified_accounts': len(_verified_account),
                                   'verified_posts': len(_verified_text),
                                   'total_accounts': len(_social_media_accounts),
                                   'total_posts': len(_social_media_posts)
                                   }
            _all_accounts = _all_accounts.union(_social_media_accounts)
            _all_texts = _all_texts + _social_media_posts

        _all_data['all'] = {'total_donation_accounts': len(_total_donation_accts),
                            'total_donation_posts': len(_total_donation_posts),
                            'total_verified_accounts': len(_total_verified_accts),
                            'total_verified_posts': len(_total_verified_posts),
                            'combined_accounts': len(combined_accounts),
                            'combined_posts': len(combined_posts),
                            'all_social_media_accounts': len(_all_accounts),
                            'all_social_media_posts': len(_all_texts)
                            }
        f_dir = "report/preprocess_table/"
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)
        with open("{}/table_1.json".format(f_dir), "w") as f_write:
            json.dump(_all_data, f_write, indent=4)

    def raw_data_information(self):
        _data_ = {
            'twitter_accounts': len(shared_util.get_all_unique_user_from_twitter()),
            'instagram_accounts': len(shared_util.get_all_unique_user_from_instagram()),
            'telegram_accounts': len(shared_util.get_all_unique_user_from_telegram()),
            'facebook_accounts': len(shared_util.get_all_unique_user_from_facebook()),
            'youtube_accounts': len(shared_util.get_all_unique_user_from_youtube()),

            'twitter_posts': len(shared_util.get_all_author_id_and_twitter_text_tuple()),
            'instagram_posts': len(shared_util.get_all_author_id_and_instagram_text_tuple()),
            'telegram_posts': len(shared_util.get_all_author_id_and_telegram_text_tuple()),
            'facebook_posts': len(shared_util.get_all_author_id_and_facebook_text_tuple()),
            'youtube_posts': len(shared_util.get_all_author_id_and_youtube_text_tuple())
        }

        _dir = "report/raw_data"
        if not os.path.exists(_dir):
            os.makedirs(_dir)

        f_path = "{}/table_1.json".format(_dir)

        with open(f_path, "w") as fwrite:
            json.dump(_data_, fwrite, indent=4)

    def social_media_hash_tags(self):
        # twitter
        # ToDo add others
        _data_ = {
            'instagram': self.instagram_social_media_hash_tags()
        }

        for key, values in _data_.items():
            with open("report/hash_tags/{}_hash_tags.csv".format(key), "w") as f_write:
                for val in values:
                    f_write.write("{}\n".format(val))

    def instagram_social_media_hash_tags(self):
        # Hash tags from Instagram Profile Search by keywords
        _top_posts_hash_tags_search_keywords = set(
            MongoDBActor(COLLECTIONS.INSTAGRAM_ACCOUNT_SEARCH).distinct(key="topPosts.hashtags"))
        _latest_posts_hash_tags_search_keywords = set(
            MongoDBActor(COLLECTIONS.INSTAGRAM_ACCOUNT_SEARCH).distinct(key="latestPosts.hashtags"))

        # single profile data
        _top_posts_hash_tags_single_profile = set(
            MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).distinct(key="topPosts.hashtags"))
        _latest_posts_hash_tags_single_profile = set(
            MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).distinct(key="latestPosts.hashtags"))

        _all = (_top_posts_hash_tags_search_keywords.union(
            _latest_posts_hash_tags_search_keywords).union(_top_posts_hash_tags_single_profile)
                .union(_latest_posts_hash_tags_single_profile))

        _all = list(_all)
        sorted(_all, reverse=True)

        # ToDo add hash tags search by single profile data

        return _all


if __name__ == "__main__":
    _arg_parser = argparse.ArgumentParser(description="Analysis processor")
    _arg_parser.add_argument("-f", "--function_name",
                             action="store",
                             required=True,
                             help="function_name")

    _arg_value = _arg_parser.parse_args()

    _dc = Analysis(_arg_value.function_name)
    _dc.process()
