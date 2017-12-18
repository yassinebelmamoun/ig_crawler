import time
import random
import datetime

from config import config


class User(object):

    def __init__(self, user_id, sql, api, from_user_id=None):
        self.user_id = user_id
        self.sql = sql
        self.api = api
        self.from_user_id = from_user_id
        self.sleep_duration = 10

        # create row
        if not User.is_user_in_db(sql=self.sql, user_id=self.user_id):
            # query user info api
            response = self.get_user_info()
            self.username = response.get('user').get('username')
            self.full_name = response.get('user').get('full_name')
            self.is_private = response.get('user').get('is_private')
            self.media_count = response.get('user').get('media_count')
            self.profile_pic_url = response.get('user').get('profile_pic_url')
            self.follower_count = response.get('user').get('follower_count')
            self.following_count = response.get('user').get('following_count')
            self.biography = response.get('user').get('biography')
            self.usertags_count = response.get('user').get('usertags_count')
            # insert user in SQL db
            self.insert_user_in_db()
        # or update row
        else:
            # query local table
            user = self.sql.get_user_by_user_id(self.user_id)
            for key, value in user.items():
                setattr(self, key, value)
                # todo: append from_user_id to list
            pass

    def __str__(self):
        return str({'user_id': self.user_id, 'from_user_id': self.from_user_id, 'username': self.username,
                    'is_private': self.is_private, 'media_count': self.media_count, 'follower_count': self.follower_count,
                    'following_count': self.following_count, 'usertags_count': self.usertags_count}) + '\n' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_user_info(self):
        while not self.api.getUsernameInfo(self.user_id):
            # sleep some time (increasing) if there is an error
            self.sleeper()
        response = self.api.LastJson
        # sleep just a little bit between each api call
        duration = 2 + 2 * random.random()
        time.sleep(duration)
        return response

    def sleeper(self):
        print('Sleep for %d sec'.format(self.sleep_duration))
        time.sleep(self.sleep_duration)
        self.sleep_duration *= 2

    @staticmethod
    def is_user_in_db(sql, user_id):
        result = sql.is_user_id_in_table(user_id=user_id)
        return result

    def insert_user_in_db(self):
        user_dict = {'user_id': self.user_id, 'from_user_id': self.from_user_id, 'username': self.username,
                     'full_name': self.full_name, 'is_private': self.is_private, 'media_count': self.media_count,
                     'profile_pic_url': self.profile_pic_url, 'follower_count': self.follower_count,
                     'following_count': self.following_count, 'biography': self.biography,
                     'usertags_count': self.usertags_count}

        self.sql.insert_user_in_table(user_dict=user_dict)

    def get_and_save_user_followings(self):
        total_follows = self.api.getTotalFollowings(usernameId=self.user_id)
        total_follows = total_follows[:config.get('followings_limit')]
        size = len(total_follows)
        for i, follow in enumerate(total_follows):
            print('Following {}/{}'.format(i+1, size))

            is_private = follow.get('is_private')
            new_user_id = str(follow.get('pk'))
            if is_private is False:
                # we keep the same sql and api connections
                new_user = User(user_id=new_user_id, sql=self.sql, api=self.api, from_user_id=self.user_id)
                print(new_user)
                print()
            elif is_private is True:
                print('User {} is private'.format(new_user_id))
                print()

