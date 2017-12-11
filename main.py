import time

from InstagramAPI import InstagramAPI

from config import config
from user_class import User
from sql_class import Sql

influencer_id_list = ['4172793932', '21426140', '20392165', ]


def check_api(current_api):
    return current_api


def crawl_influencer_followings(sql, api):
    for i, influencer_id in enumerate(influencer_id_list):
        size = len(influencer_id_list)
        print('------ Influencer {}/{} ------'.format(i+1, size))
        user = User(user_id=influencer_id, sql=sql, api=check_api(current_api=api))
        print(user)
        print()
        if user.following_count < config.get('max_followings'):
            user.get_and_save_user_followings()
        print()


if __name__ == '__main__':
    # define sql connection
    sql = Sql(
        user=config.get('postgres_user'),
        password=config.get('postgres_password'),
        database=config.get('postgres_database')
    )
    conn, meta = sql.connect()
    # define instagram connection
    api = InstagramAPI(username=config.get('ig_username'), password=config.get('ig_password'))
    api.login()
    time.sleep(5)
    # crawl instagram followings
    crawl_influencer_followings(sql=sql, api=api)
