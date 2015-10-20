#!/usr/bin/env python

# Requires "requests" and "beautifulsoup4"

# Fix 1:
#   Upgrade PIP: http://discuss.tweepy.org/t/pip-install-tweepy-fails/209
# Fix 2:
#   sudo pip install --ignore-installed six tweepy # http://stackoverflow.com/a/33136494/4077759

# Source: https://github.com/dfm/feedfinder2
import time
import tweepy
import threading
from Queue import Queue
from threading import Thread
from ff2 import find_feeds

# Threading help here:
#  http://www.troyfawkes.com/learn-python-multithreading-queues-basics/
    
def get_feed(url):
    return find_feeds(url)

def process_friend(friendq):
  while True:
    feed = []
    url = ""
    friend = friendq.get()
    if 'url' in friend.entities:
        if 'urls' in friend.entities['url']:
            url = friend.entities["url"]["urls"][0]["expanded_url"]
            feed = get_feed(url)
    if len(feed) > 0:
        print "User: %s\tFeed: %s" % (friend.screen_name, feed[0])
        opmlfile.write(OPML_OUTLINE_FEED % {'title': friend.screen_name, 'html_url': url, 'xml_url': feed[0]})
        opmlfile.write("\n")
    friendq.task_done()

## Main

# Queue and Threading Starting
friendq = Queue(maxsize=0)
num_threads = 20

for i in range(num_threads):
  worker = Thread(target=process_friend, args=(friendq,))
  worker.setDaemon(True)
  worker.start()


# Twitter / Tweepy configs
ckey = 'your consumer key goes here'
csec = 'your consumer secret goes here'
atok = 'your access token goes here'
asec = 'your access token secret goes here'

# Twitter OAuth
auth = tweepy.OAuthHandler(ckey, csec)
auth.set_access_token(atok, asec)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# OPML Code From: 
#   https://gist.github.com/myles/1051517

opmlfile = open("friendsfeeds.opml", 'w')


OPML_START = """<?xml version="1.0" encoding="UTF-8"?>
<!-- OPML generated by FriendsFeeds -->
<opml version="1.1">
	<head>
		<title>Twitter Friends</title>
	</head>
	<body>
		<outline text="Twitter Friends" title="Twitter Friends">"""
OPML_END = """		</outline>
	</body>
</opml>"""
OPML_OUTLINE_FEED = '<outline text="%(title)s" title="%(title)s" type="rss" version="RSS" htmlUrl="%(html_url)s" xmlUrl="%(xml_url)s" />'

opmlfile.write(OPML_START)
opmlfile.write("\n")

for friend in tweepy.Cursor(api.friends, count=200).items():
    # Process the friend here
    friendq.put(friend)

friendq.join()
opmlfile.write("\n")
opmlfile.write(OPML_END)
