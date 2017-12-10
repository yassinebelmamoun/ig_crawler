from InstagramAPI import InstagramAPI
import time # For Naps

IG_USERNAME = ''
IG_PASSWORD = ''

a = InstagramAPI(username=IG_USERNAME, password=IG_PASSWORD)
a.login()

# Start from an influencer (Need to be improved: start from a list of influencer)
id_influencer = '4172793932'

def get_followings(id):
    print('Get all followings of the influencers')
    # Limit to 500
    total_follows = a.getTotalFollowings(usernameId=id)[:500]
    size = len(total_follows)
    follows = []
    for i, follow in enumerate(total_follows):
        if i % 9 == 0:
            time.sleep(15)
        else:
            time.sleep(2)
        print(' ------ Step:' + str(i) + '/' + str(size))
        info = get_info(follow)
        follows.append(info)
    return follows

def get_info(user):
    return {
        'pk': user.get('pk'),
        'username': user.get('username'),
        'full_name': user.get('full_name'),
        'details': get_details(id=user.get('pk'))
    }

def get_details(id):

    while not a.getUsernameInfo(id):
        print("Let's sleep for 60 secondes")
        time.sleep(60)

    response = a.LastJson
    return {
        'is_private': response.get('user').get('is_private'),
        'media_count': response.get('user').get('media_count'),
        'profile_picture': response.get('user').get('profile_pic_url'),
        'follower_count': response.get('user').get('follower_count'),
        'following_count': response.get('user').get('following_count'),
        'biography': response.get('user').get('biography'),
        'usertags_count': response.get('user').get('usertags_count'),
    }

def job(id):
    return get_followings(id=id) 