"""All the available endpoints of the MAL API v2, excluding the ones that
require user login to perform actions.
"""

BASE = 'https://api.myanimelist.net/v2'


ANIME = BASE + '/anime'
ANIME_RANKING = BASE + '/anime/ranking'
ANIME_SEASONAL = BASE + '/anime/season'
ANIME_SUGGESTIONS = BASE + '/anime/suggestions'

MANGA = BASE + '/manga'
MANGA_RANKING = BASE + '/manga/ranking'

# use /user/<username>/mangalist or /user/<username>/animelist for those
USER = BASE + '/users'

FORUM_BOARDS = BASE + '/forum/boards'
FORUM_TOPICS = BASE + '/forum/topics'
FORUM_TOPIC_DETAIL = BASE + '/forum/topic'
