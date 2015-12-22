#!/usr/bin/env python
# -*- coding: utf-8 -*-

#####################################
# Lean cloud parserhub db Part ######
#####################################
PARSERHUB_APP_ID = 't0szmn5lnnipvozh1z3copk6r76joyy6uzioum96z9nq00g8'
PARSERHUB_APP_KEY = 's6q8cksb27b2mktmczyzoohvkmadvw19tl2qhhduuk7mntse'

TIMELINE_APP_ID = 'pin72fr1iaxb7sus6newp250a4pl2n5i36032ubrck4bej81'
TIMELINE_APP_KEY = 'qs4o5iiywp86eznvok4tmhul360jczk7y67qj0ywbcq35iia'


#########################
# Mongo DB Part #########
#########################
MONGODB_HOST = '119.254.111.40'
MONGODB_PORT = 27017
DB_NAME = 'RefinedLog'
DB_USER = 'senzhub'
DB_PASSWORD = 'Senz2everyone'
DB_USER_LOCATION_TABLE = 'UserLocation'
DB_ACTIVITY_TABLE = 'Events'
DB_USER_ACTIVITY_TABLE = 'UserActivity'

########################
# Redis Part ###########
########################
REDIS_HOST = '123.57.5.45'  # '127.0.0.1'
REDIS_PORT = 6379
# redis db for parserhub calculate speed
REDIS_DB_LOCATION = 3  # this is for saving user location
REDIS_DB_USER_ACTIVITY = 4  # this is for user activity


########################
# constants ############
#########################
DEFAULT_EVENT_NEAR_GEO_POINT = 10
LEANCLOUD_QUERY_LIMIT = 1000
LEANCLOUD_EVENT_TABLE = 'Events'
DEFAULT_NEAR_POI_DISTANCE_THRESHOLD = 0.2  # km
DEFAULT_ACTIVITY_LAST_TIME = {"公益": 3600 * 5,
                              "讲座": 3600 * 3,
                              "旅行": 3600 * 6,
                              "其他": 3600 * 6,
                              "聚会": 3600 * 3,
                              "运动": 3600 * 2,
                              "音乐": 3600 * 3,
                              "电影": 3600 * 2,
                              "戏剧": 3600 * 2.5,
                              "展览": 3600 * 4}
