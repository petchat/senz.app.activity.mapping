#!/usr/bin/python
# -*- coding: utf-8 -*-
import redis

from user_activity_mapping.config import REDIS_HOST
from user_activity_mapping.config import REDIS_PORT
from user_activity_mapping.config import REDIS_DB_LOCATION
from user_activity_mapping.config import REDIS_DB_USER_ACTIVITY


redis_location_session = redis.StrictRedis(host=REDIS_HOST,
                                           port=REDIS_PORT,
                                           db=REDIS_DB_LOCATION)

user_activity_session = redis.StrictRedis(host=REDIS_HOST,
                                          port=REDIS_PORT,
                                          db=REDIS_DB_USER_ACTIVITY)
