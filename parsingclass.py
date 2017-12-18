import csv
import re

import langdetect
from langdetect.lang_detect_exception import LangDetectException

from config import config
from sqlclass import Sql


def export_users_and_data(sql, max=-1):
    # get users and data (via yield)
    count = {}
    users = parse_instagram_bios(sql, max)

    #  writing all_users csv file
    users_filename = 'instagram_users.csv'

    users_fields = ['user_id', 'from_user_id', 'username', 'full_name', 'is_private', 'media_count', 'follower_count',
                    'following_count', 'biography', 'usertags_count', 'language', 'email', 'phone', 'line', 'facebook',
                    'whatsapp', 'wechat']

    with open(users_filename, 'w') as user_file:
        user_writer = csv.DictWriter(user_file, fieldnames=users_fields)
        user_writer.writeheader()
        for user, count in users:
            user.pop('id')
            user.pop('profile_pic_url')
            user_writer.writerow(user)
            count = count

    print('File is generated')
    print(count)


def parse_instagram_bios(sql, max=-1):
    # record some statistics while parsing
    count = {'total': 0, 'influencer': 0, 'th': 0, 'en': 0, 'email': 0, 'phone': 0,
             'whatsapp': 0, 'line': 0, 'wechat': 0, 'facebook': 0}

    users = sql.get_all_users()

    for i, user in enumerate(users):
        count['total'] += 1

        print('------ User parsed data {}/{} ------'.format(i+1, max))

        influencer = is_influencer(user)
        if influencer:
            count['influencer'] += 1
        biography = user.get('biography')

        language = get_language(biography)
        for lang in ['th', 'en']:
            if language == lang:
                count[lang] += 1

        email = get_email(biography)
        if email != '':
            count['email'] += 1

        phone = get_phone(biography)
        if phone != '':
            count['phone'] += 1

        apps = {}
        for app in ['whatsapp', 'line', 'wechat', 'facebook']:
            result = get_social_accounts(biography, app)
            apps[app] = result
            if result != '':
                count[app] += 1

        user.update({'language': language, 'email': email, 'phone': phone,
                     'whatsapp': apps['whatsapp'], 'line': apps['line'],
                     'wechat': apps['wechat'], 'facebook': apps['facebook']})

        print(user)
        print()

        if i == max-1:
            break

        yield user, count


def get_language(biography):
    language = ''
    try:
        language = langdetect.detect(biography)
    except LangDetectException:
        pass
    return language


def get_email(biography):
    email = ''
    match = re.search(r'[\w\.-]+@[\w\.-]+', biography)
    if match:
        email = match.group(0)
    return email


def get_phone(biography):
    phone = ''
    match = re.search(r'1?[\s-]?\(?(\d{3})\)?[\s-]?\d{3}[\s-]?\d{4}', biography)
    if match:
        phone = match.group(0)
    return phone


def get_social_accounts(biography, app):
    result = ''
    if app.lower() in biography.lower():
        try:
            cleaned_text = ''.join(ch if ch.isalnum() else ' ' for ch in biography)
            index = cleaned_text.lower().find(app.lower())
            next_words = cleaned_text[index + len(app) - 1:].split()
            filtered = [word for word in next_words if len(word) > 2]
            result = filtered[0]
        except IndexError:
            result = ''

    return result


def is_influencer(user):
    follower_count = user['follower_count']
    result = follower_count >= 10000
    return result


if __name__ == '__main__':
    # define sql connection
    sql = Sql(
        user=config.get('postgres_user'),
        password=config.get('postgres_password'),
        database=config.get('postgres_database')
    )
    # crawl instagram followings
    print('Parse instagram bios...')
    print()
    export_users_and_data(sql, max=100)
