import os

"""
    Throughout the research, we stored all of data into MongoDB.
    The ``Collection`` class stores all the constants of the MongoDB Collections.
"""


class COLLECTIONS:
    DONATION_TEXT_SEARCH = "donation_text_search"
    DONATION_URL_SEARCH = "donation_url_search"
    INSTAGRAM_SINGLE_POST = "instagram_single_post"
    INSTAGRAM_ACCOUNT_SEARCH = "instagram_account_search"
    INSTAGRAM_HASH_TAG_SEARCH = "instagram_hash_tag_search"
    FACEBOOK_HASH_TAG_SEARCH = "facebook_hash_tag_search"
    FACEBOOK_SINGLE_POST = "facebook_single_post"
    INSTAGRAM_SINGLE_PROFILE_DATA = "instagram_single_profile_data"
    YOUTUBE_ACCOUNT_SEARCH = "you_tube_account_search"
    YOUTUBE_COMMENTS_SEARCH = "you_tube_comments_search"
    TELEGRAM_ACCOUNT_SEARCH = "telegram_account_search"
    TELEGRAM_SINGLE_POST = "telegram_single_post"
    TELEGRAM_ACCOUNT_DETAIL = "telegram_account_detail"
    TELEGRAM_ACCOUNT_MESSAGES = "telegram_account_messages"
    FACEBOOK_ACCOUNT_SEARCH = "facebook_account_search"
    FACEBOOK_SINGLE_PROFILE_DATE = "facebook_single_profile_data"
    TWITTER_USER_DETAIL = "twitter_user_detail"
    VT_LOOK_UP = "vt_look_up"
    FORMS_META_DATA = "forms_meta_data"
    EMAIL_LOOK_UP = "email_look_up"
    PHONE_NUMBER_LOOK_UP = "phone_number_look_up"
    FACEBOOK_MEGA_DATA = "facebook_mega_data"
    INSTAGRAM_MEGA_DATA = "instagram_mega_data"
    TWITTER_MEGA_DATA = "twitter_mega_data"
    TELEGRAM_MEGA_DATA = "telegram_mega_data"
    YOU_TUBE_MEGA_DATA = "youtube_mega_data"


"""
    Analysis - Storing images related data
"""


class IMAGES:
    SCAM_DONATION_IMG_DIR = "/home/{}/scam_donation_images".format('USER_NAME')
    INSTAGRAM = "{}/instagram".format(SCAM_DONATION_IMG_DIR)
    FACEBOOK = "{}/facebook".format(SCAM_DONATION_IMG_DIR)
    YOU_TUBE = "{}/youtube".format(SCAM_DONATION_IMG_DIR)
    TELEGRAM = "{}/telegram".format(SCAM_DONATION_IMG_DIR)
    TWITTER = "{}/twitter".format(SCAM_DONATION_IMG_DIR)
    FORMS = "{}/forms".format(SCAM_DONATION_IMG_DIR)
    DATA_SHARE = "{}/input".format(SCAM_DONATION_IMG_DIR)


"""
    Analysis - Storing posts related data
"""


class TEXT:
    SCAM_DONATION_TEXT_DIR = "/home/{}/scam_donation_text".format('USER_NAME')
    INSTAGRAM_POST = "{}/post/instagram".format(SCAM_DONATION_TEXT_DIR)
    FACEBOOK_POST = "{}/post/facebook".format(SCAM_DONATION_TEXT_DIR)
    YOU_TUBE_POST = "{}/post/youtube".format(SCAM_DONATION_TEXT_DIR)
    YOU_TUBE_COMMENT = "{}/comment/youtube".format(SCAM_DONATION_TEXT_DIR)
    TELEGRAM_POST = "{}/post/telegram".format(SCAM_DONATION_TEXT_DIR)
    TWITTER_POST = "{}/post/twitter".format(SCAM_DONATION_TEXT_DIR)
    QUALITATIVE_STUDY = "{}/qualitative_study".format(SCAM_DONATION_TEXT_DIR)
    DATA_SHARE = "{}/input".format(SCAM_DONATION_TEXT_DIR)


"""
    API Keys 
"""


class API_KEY:
    CHAT_GPT = os.environ['CHAT_GPT_KEY']
    APIFY_KEY = os.environ['APIFY_KEY']
    IP_QUALITY_SCORE = os.environ['IP_QUALITY_SCORE_KEY']
    VIRUS_TOTAL = os.environ['VIRUS_TOTAL_API_KEY']


class ANAMOLY:
    USER_DETAIL_ANAMOLY = "user_detail_anamoly"


class TWITTER_API_SUFFIX:
    DEFAULT = "TWITTER_SUBSCRIBED_API"
