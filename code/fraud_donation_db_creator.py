from constants import COLLECTIONS
from db_util import MongoDBActor

import shared_util
import argparse

"""
    This class evaluates each of the data whether it contains fraud communication channels.
"""


class CandidateCreator:
    def __init__(self, function_name):
        self.function_name = function_name

    def process(self):
        if self.function_name == "create_facebook_scam_data_collection":
            self.create_facebook_scam_data_collection()
        elif self.function_name == "create_instagram_scam_data_collection":
            self.create_instagram_scam_data_collection()
        elif self.function_name == "create_you_tube_scam_data_collection":
            self.create_you_tube_scam_data_collection()
        elif self.function_name == "create_twitter_scam_data_collection":
            self.create_twitter_scam_data_collection()
        elif self.function_name == "create_telegram_scam_data_collection":
            self.create_telegram_scam_data_collection()

    def create_facebook_scam_data_collection(self):
        mega_fb_collection = []
        _distinct_verified_accounts = shared_util.get_facebook_verified_author_ids()
        _distinct_donation_context_accounts = shared_util.get_facebook_donation_context_account()

        _distinct_vt_urls = shared_util.get_vt_positive_url_from_social_media('facebook')
        _distinct_ip_score_emails = shared_util.get_ip_risk_email_by_social_media('facebook')
        _distinct_ip_score_phone_number = shared_util.get_ip_risk_phone_number_by_social_media('facebook')

        _len = len(_distinct_donation_context_accounts)
        for cnt, each_acct in enumerate(_distinct_donation_context_accounts):
            print("Processing facebook: {}/{}, {}".format(cnt, _len, each_acct))
            each_scam_accounts_data = {'id': each_acct}
            _may_be_post_url = set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).distinct(key='may_be_url',
                                                                                           filter={"id": each_acct}))

            _may_be_profile_url = set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).distinct(key='website',
                                                                                                      filter={
                                                                                                          "pageId": each_acct}))

            _may_be_url = _may_be_post_url.union(_may_be_profile_url)
            if None in _may_be_url:
                _may_be_url.remove(None)

            _intersect_vt = list(_may_be_url.intersection(_distinct_vt_urls))
            each_scam_accounts_data['fraud_url'] = _intersect_vt
            has_fraud_url = len(_intersect_vt) > 0
            each_scam_accounts_data['has_fraud_url'] = has_fraud_url

            # Note the id of facebook was received from face has tag, user.id
            _may_be_email_single_post = set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).distinct(
                key='may_be_email',
                filter={"id": each_acct}))

            _may_be_email_single_profile = set(MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).distinct(
                key='email',
                filter={"pageId": each_acct}))

            _may_be_email = _may_be_email_single_post.union(_may_be_email_single_profile)

            if None in _may_be_email:
                _may_be_email.remove(None)

            _intersect_fraud_email = list(_distinct_ip_score_emails.
                                          intersection(_may_be_email))
            each_scam_accounts_data['fraud_email'] = _intersect_fraud_email
            has_fraud_email = len(_intersect_fraud_email) > 0
            each_scam_accounts_data['has_fraud_email'] = has_fraud_email

            _may_be_phone_profile_data = set(
                MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_PROFILE_DATE).distinct(key='phone',
                                                                                filter={"pageId": each_acct}))

            _may_be_phone_post_data = set(
                MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).distinct(key='may_be_phone_number',
                                                                        filter={"id": each_acct}))

            _may_be_phone = _may_be_phone_profile_data.union(_may_be_phone_post_data)

            if None in _may_be_phone:
                _may_be_phone.remove(None)

            _intersect_phone = list(_distinct_ip_score_phone_number.
                                    intersection(_may_be_phone))
            each_scam_accounts_data['fraud_phone'] = _intersect_phone
            has_fraud_phone = len(_intersect_phone) > 0
            each_scam_accounts_data['has_fraud_phone'] = has_fraud_phone

            _may_be_crypto_data = set(
                MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).distinct(key='may_be_crypto',
                                                                        filter={"id": each_acct}))
            if None in _may_be_crypto_data:
                _may_be_crypto_data.remove(None)

            has_crytpo = len(_may_be_crypto_data) > 0
            each_scam_accounts_data['crypto_addresses'] = list(_may_be_crypto_data)
            each_scam_accounts_data['has_crypto'] = has_crytpo

            posts_data = []
            for item in MongoDBActor(COLLECTIONS.FACEBOOK_SINGLE_POST).find({"id": each_acct}):
                _found_text = item['text']
                _found_donation_context_text = item['is_donation_context_text']
                _data_item = {'text': _found_text, 'is_donation_context_text': _found_donation_context_text}
                if _data_item not in posts_data:
                    posts_data.append(_data_item)

            each_scam_accounts_data['posts_data'] = posts_data

            each_scam_accounts_data[
                'is_donation_abuse_candidate'] = has_fraud_url or has_fraud_phone or has_fraud_email or has_crytpo
            mega_fb_collection.append(each_scam_accounts_data)

        for cnt, each_val in enumerate(mega_fb_collection):
            MongoDBActor(COLLECTIONS.FACEBOOK_MEGA_DATA).find_and_modify(key={"id": each_val['id']}, data=each_val)
            print("Inserted: {}/{}, {}".format(cnt, len(mega_fb_collection), each_val))

    def create_instagram_scam_data_collection(self):
        mega_fb_collection = []
        _distinct_verified_accounts = shared_util.get_instagram_verified_owner_ids()
        _distinct_donation_context_accounts = shared_util.get_instagram_donation_context_account()

        _distinct_vt_urls = shared_util.get_vt_positive_url_from_social_media('instagram')
        _distinct_ip_score_emails = shared_util.get_ip_risk_email_by_social_media('instagram')
        _distinct_ip_score_phone_number = shared_util.get_ip_risk_phone_number_by_social_media('instagram')

        _len = len(_distinct_donation_context_accounts)
        for cnt, each_acct in enumerate(_distinct_donation_context_accounts):
            print("Processing instagram: {}/{}, {}".format(cnt, _len, each_acct))
            each_scam_accounts_data = {'id': each_acct}
            _may_be_post_url = set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).distinct(key='may_be_url',
                                                                                            filter={
                                                                                                "ownerId": each_acct}))

            _may_be_profile_url = set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_PROFILE_DATA).distinct(key='website',
                                                                                                       filter={
                                                                                                           "ownerId": each_acct}))

            _may_be_url = _may_be_post_url.union(_may_be_profile_url)
            if None in _may_be_url:
                _may_be_url.remove(None)

            _intersect_vt = list(_may_be_url.intersection(_distinct_vt_urls))
            each_scam_accounts_data['fraud_url'] = _intersect_vt
            has_fraud_url = len(_intersect_vt) > 0
            each_scam_accounts_data['has_fraud_url'] = has_fraud_url

            # Note the id of facebook was received from face has tag, user.id
            _may_be_email = set(MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).distinct(
                key='may_be_email',
                filter={"ownerId": each_acct}))

            if None in _may_be_email:
                _may_be_email.remove(None)

            _intersect_fraud_email = list(_distinct_ip_score_emails.
                                          intersection(_may_be_email))
            each_scam_accounts_data['fraud_email'] = _intersect_fraud_email
            has_fraud_email = len(_intersect_fraud_email) > 0
            each_scam_accounts_data['has_fraud_email'] = has_fraud_email

            _may_be_phone = set(
                MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).distinct(key='may_be_phone_number',
                                                                         filter={"ownerId": each_acct}))

            if None in _may_be_phone:
                _may_be_phone.remove(None)

            _intersect_phone = list(_distinct_ip_score_phone_number.
                                    intersection(_may_be_phone))
            each_scam_accounts_data['fraud_phone'] = _intersect_phone
            has_fraud_phone = len(_intersect_phone) > 0
            each_scam_accounts_data['has_fraud_phone'] = has_fraud_phone

            _may_be_crypto_data = set(
                MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).distinct(key='may_be_crypto',
                                                                         filter={"ownerId": each_acct}))
            if None in _may_be_crypto_data:
                _may_be_crypto_data.remove(None)

            has_crytpo = len(_may_be_crypto_data) > 0
            each_scam_accounts_data['crypto_addresses'] = list(_may_be_crypto_data)
            each_scam_accounts_data['has_crypto'] = has_crytpo

            posts_data = []
            for item in MongoDBActor(COLLECTIONS.INSTAGRAM_SINGLE_POST).find({"ownerId": each_acct}):
                _found_text = item['text']
                _found_donation_context_text = item['is_donation_context_text']
                _data_item = {'text': _found_text, 'is_donation_context_text': _found_donation_context_text}
                if _data_item not in posts_data:
                    posts_data.append(_data_item)

            each_scam_accounts_data['posts_data'] = posts_data

            each_scam_accounts_data[
                'is_donation_abuse_candidate'] = has_fraud_url or has_fraud_phone or has_fraud_email or has_crytpo
            mega_fb_collection.append(each_scam_accounts_data)

        for cnt, each_val in enumerate(mega_fb_collection):
            MongoDBActor(COLLECTIONS.INSTAGRAM_MEGA_DATA).find_and_modify(key={"id": each_val['id']}, data=each_val)
            print("Inserted: {}/{}, {}".format(cnt, len(mega_fb_collection), each_val))

    def create_you_tube_scam_data_collection(self):
        mega_fb_collection = []
        _distinct_verified_accounts = shared_util.get_you_tube_verified_author_ids()
        _distinct_donation_context_accounts = shared_util.get_you_tube_donation_context_account()

        _distinct_vt_urls = shared_util.get_vt_positive_url_from_social_media('youtube')
        _distinct_ip_score_emails = shared_util.get_ip_risk_email_by_social_media('youtube')
        _distinct_ip_score_phone_number = shared_util.get_ip_risk_phone_number_by_social_media('youtube')

        _len = len(_distinct_donation_context_accounts)
        for cnt, each_acct in enumerate(_distinct_donation_context_accounts):
            print("Processing youtube: {}/{}, {}".format(cnt, _len, each_acct))
            each_scam_accounts_data = {'id': each_acct}
            _may_be_post_url = set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(key='may_be_url',
                                                                                             filter={
                                                                                                 "id": each_acct}))

            _may_be_profile_url = set(
                MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(key='descriptionLinks.url',
                                                                          filter={
                                                                              "id": each_acct}))

            _may_be_url = _may_be_post_url.union(_may_be_profile_url)
            if None in _may_be_url:
                _may_be_url.remove(None)

            _intersect_vt = list(_may_be_url.intersection(_distinct_vt_urls))
            each_scam_accounts_data['fraud_url'] = _intersect_vt
            has_fraud_url = len(_intersect_vt) > 0
            each_scam_accounts_data['has_fraud_url'] = has_fraud_url

            _may_be_email = set(MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(
                key='may_be_email',
                filter={"id": each_acct}))

            if None in _may_be_email:
                _may_be_email.remove(None)

            _intersect_fraud_email = list(_distinct_ip_score_emails.
                                          intersection(_may_be_email))
            each_scam_accounts_data['fraud_email'] = _intersect_fraud_email
            has_fraud_email = len(_intersect_fraud_email) > 0
            each_scam_accounts_data['has_fraud_email'] = has_fraud_email

            _may_be_phone = set(
                MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(key='may_be_phone_number',
                                                                          filter={"id": each_acct}))

            if None in _may_be_phone:
                _may_be_phone.remove(None)

            _intersect_phone = list(_distinct_ip_score_phone_number.
                                    intersection(_may_be_phone))
            each_scam_accounts_data['fraud_phone'] = _intersect_phone
            has_fraud_phone = len(_intersect_phone) > 0
            each_scam_accounts_data['has_fraud_phone'] = has_fraud_phone

            _may_be_crypto_data = set(
                MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).distinct(key='may_be_crypto',
                                                                          filter={"id": each_acct}))
            if None in _may_be_crypto_data:
                _may_be_crypto_data.remove(None)

            has_crytpo = len(_may_be_crypto_data) > 0
            each_scam_accounts_data['crypto_addresses'] = list(_may_be_crypto_data)
            each_scam_accounts_data['has_crypto'] = has_crytpo

            posts_data = []
            for item in MongoDBActor(COLLECTIONS.YOUTUBE_ACCOUNT_SEARCH).find({"id": each_acct}):
                _found_text = item['text']
                _found_donation_context_text = item['is_donation_context_text']
                _data_item = {'text': _found_text, 'is_donation_context_text': _found_donation_context_text}
                if _data_item not in posts_data:
                    posts_data.append(_data_item)

            each_scam_accounts_data['posts_data'] = posts_data

            each_scam_accounts_data[
                'is_donation_abuse_candidate'] = has_fraud_url or has_fraud_phone or has_fraud_email or has_crytpo
            mega_fb_collection.append(each_scam_accounts_data)

        for cnt, each_val in enumerate(mega_fb_collection):
            MongoDBActor(COLLECTIONS.YOU_TUBE_MEGA_DATA).find_and_modify(key={"id": each_val['id']}, data=each_val)
            print("Inserted: {}/{}, {}".format(cnt, len(mega_fb_collection), each_val))

    def create_twitter_scam_data_collection(self):
        mega_fb_collection = []
        _distinct_verified_accounts = shared_util.get_twitter_verified_author_ids()
        _distinct_donation_context_accounts = shared_util.get_twitter_donation_context_account()

        _distinct_vt_urls = shared_util.get_vt_positive_url_from_social_media('twitter')
        _distinct_ip_score_emails = shared_util.get_ip_risk_email_by_social_media('twitter')
        _distinct_ip_score_phone_number = shared_util.get_ip_risk_phone_number_by_social_media('twitter')

        _len = len(_distinct_donation_context_accounts)
        for cnt, each_acct in enumerate(_distinct_donation_context_accounts):
            print("Processing twitter: {}/{}, {}".format(cnt, _len, each_acct))
            each_scam_accounts_data = {'id': each_acct}
            _may_be_post_url = set(MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(key='may_be_url',
                                                                                           filter={
                                                                                               "author_id": each_acct}))

            _may_be_profile_url = set(
                MongoDBActor(COLLECTIONS.TWITTER_USER_DETAIL).distinct(key='entities.url.urls.expanded_url',
                                                                       filter={
                                                                           "author_id": each_acct}))

            _may_be_url = _may_be_post_url.union(_may_be_profile_url)
            if None in _may_be_url:
                _may_be_url.remove(None)

            _intersect_vt = list(_may_be_url.intersection(_distinct_vt_urls))
            each_scam_accounts_data['fraud_url'] = _intersect_vt
            has_fraud_url = len(_intersect_vt) > 0
            each_scam_accounts_data['has_fraud_url'] = has_fraud_url

            _may_be_email = set(MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(
                key='may_be_email',
                filter={"author_id": each_acct}))

            if None in _may_be_email:
                _may_be_email.remove(None)

            _intersect_fraud_email = list(_distinct_ip_score_emails.
                                          intersection(_may_be_email))
            each_scam_accounts_data['fraud_email'] = _intersect_fraud_email
            has_fraud_email = len(_intersect_fraud_email) > 0
            each_scam_accounts_data['has_fraud_email'] = has_fraud_email

            _may_be_phone = set(
                MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(key='may_be_phone_number',
                                                                        filter={"author_id": each_acct}))

            if None in _may_be_phone:
                _may_be_phone.remove(None)

            _intersect_phone = list(_distinct_ip_score_phone_number.
                                    intersection(_may_be_phone))
            each_scam_accounts_data['fraud_phone'] = _intersect_phone
            has_fraud_phone = len(_intersect_phone) > 0
            each_scam_accounts_data['has_fraud_phone'] = has_fraud_phone

            _may_be_crypto_data = set(
                MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).distinct(key='may_be_crypto',
                                                                        filter={"author_id": each_acct}))
            if None in _may_be_crypto_data:
                _may_be_crypto_data.remove(None)

            has_crytpo = len(_may_be_crypto_data) > 0
            each_scam_accounts_data['crypto_addresses'] = list(_may_be_crypto_data)
            each_scam_accounts_data['has_crypto'] = has_crytpo

            posts_data = []
            for item in MongoDBActor(COLLECTIONS.DONATION_TEXT_SEARCH).find({"author_id": each_acct}):
                _found_text = item['text']
                _found_donation_context_text = item['is_donation_context_text']
                _data_item = {'text': _found_text, 'is_donation_context_text': _found_donation_context_text}
                if _data_item not in posts_data:
                    posts_data.append(_data_item)

            each_scam_accounts_data['posts_data'] = posts_data

            each_scam_accounts_data[
                'is_donation_abuse_candidate'] = has_fraud_url or has_fraud_phone or has_fraud_email or has_crytpo
            mega_fb_collection.append(each_scam_accounts_data)

        for cnt, each_val in enumerate(mega_fb_collection):
            MongoDBActor(COLLECTIONS.TWITTER_MEGA_DATA).find_and_modify(key={"id": each_val['id']}, data=each_val)
            print("Inserted: {}/{}, {}".format(cnt, len(mega_fb_collection), each_val))

    def create_telegram_scam_data_collection(self):
        mega_fb_collection = []
        _distinct_verified_accounts = shared_util.get_telegram_verified_author_ids()
        _distinct_donation_context_accounts = shared_util.get_telegram_donation_context_account()

        _distinct_vt_urls = shared_util.get_vt_positive_url_from_social_media('telegram')
        _distinct_ip_score_emails = shared_util.get_ip_risk_email_by_social_media('telegram')
        _distinct_ip_score_phone_number = shared_util.get_ip_risk_phone_number_by_social_media('telegram')

        _len = len(_distinct_donation_context_accounts)
        for cnt, each_acct in enumerate(_distinct_donation_context_accounts):
            print("Processing telegram: {}/{}, {}".format(cnt, _len, each_acct))
            each_scam_accounts_data = {'id': each_acct}
            _may_be_url = set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(key='may_be_url',
                                                                                      filter={
                                                                                          "telemtr_url": each_acct}))
            if None in _may_be_url:
                _may_be_url.remove(None)

            _intersect_vt = list(_may_be_url.intersection(_distinct_vt_urls))
            each_scam_accounts_data['fraud_url'] = _intersect_vt
            has_fraud_url = len(_intersect_vt) > 0
            each_scam_accounts_data['has_fraud_url'] = has_fraud_url

            _may_be_email = set(MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(
                key='may_be_email',
                filter={"telemtr_url": each_acct}))

            if None in _may_be_email:
                _may_be_email.remove(None)

            _intersect_fraud_email = list(_distinct_ip_score_emails.
                                          intersection(_may_be_email))
            each_scam_accounts_data['fraud_email'] = _intersect_fraud_email
            has_fraud_email = len(_intersect_fraud_email) > 0
            each_scam_accounts_data['has_fraud_email'] = has_fraud_email

            _may_be_phone = set(
                MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(key='may_be_phone_number',
                                                                        filter={"telemtr_url": each_acct}))

            if None in _may_be_phone:
                _may_be_phone.remove(None)

            _intersect_phone = list(_distinct_ip_score_phone_number.
                                    intersection(_may_be_phone))
            each_scam_accounts_data['fraud_phone'] = _intersect_phone
            has_fraud_phone = len(_intersect_phone) > 0
            each_scam_accounts_data['has_fraud_phone'] = has_fraud_phone

            _may_be_crypto_data = set(
                MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).distinct(key='may_be_crypto',
                                                                        filter={"telemtr_url": each_acct}))
            if None in _may_be_crypto_data:
                _may_be_crypto_data.remove(None)

            has_crytpo = len(_may_be_crypto_data) > 0
            each_scam_accounts_data['crypto_addresses'] = list(_may_be_crypto_data)
            each_scam_accounts_data['has_crypto'] = has_crytpo

            posts_data = []
            for item in MongoDBActor(COLLECTIONS.TELEGRAM_SINGLE_POST).find({"telemtr_url": each_acct}):
                _found_text = item['text']
                _found_donation_context_text = item['is_donation_context_text']
                _data_item = {'text': _found_text, 'is_donation_context_text': _found_donation_context_text}
                if _data_item not in posts_data:
                    posts_data.append(_data_item)

            each_scam_accounts_data['posts_data'] = posts_data

            each_scam_accounts_data[
                'is_donation_abuse_candidate'] = has_fraud_url or has_fraud_phone or has_fraud_email or has_crytpo
            mega_fb_collection.append(each_scam_accounts_data)

        for cnt, each_val in enumerate(mega_fb_collection):
            MongoDBActor(COLLECTIONS.TELEGRAM_MEGA_DATA).find_and_modify(key={"id": each_val['id']}, data=each_val)
            print("Inserted: {}/{}, {}".format(cnt, len(mega_fb_collection), each_val))


if __name__ == "__main__":
    _arg_parser = argparse.ArgumentParser(description="Data Creator")
    _arg_parser.add_argument("-f", "--function_name",
                             action="store",
                             required=True,
                             help="function_name")

    _arg_value = _arg_parser.parse_args()

    _dc = CandidateCreator(_arg_value.function_name)
    _dc.process()
