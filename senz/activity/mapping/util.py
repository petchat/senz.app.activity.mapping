#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import time
from datetime import datetime

import leancloud
import pymongo
from leancloud import Object, Query
from geopy.distance import vincenty

from config import PARSERHUB_APP_ID, PARSERHUB_APP_KEY
from config import TIMELINE_APP_ID, TIMELINE_APP_KEY
from config import MONGODB_HOST, MONGODB_PORT
from config import DB_NAME, DB_USER, DB_PASSWORD
from config import DB_USER_LOCATION_TABLE
from config import DEFAULT_EVENT_NEAR_GEO_POINT, LEANCLOUD_QUERY_LIMIT
from config import LEANCLOUD_EVENT_TABLE, DB_ACTIVITY_TABLE


mongo_client = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT)
db_refinedlog = mongo_client.get_database(DB_NAME)
db_refinedlog.authenticate(DB_USER, DB_PASSWORD)
db_location = db_refinedlog.get_collection(DB_USER_LOCATION_TABLE)
db_activity = db_refinedlog.get_collection(DB_ACTIVITY_TABLE)


def get_recent_traces_from_mongodb(user_id, last_days=1):
    end_time = datetime.now()
    mkt_end_time = time.mktime(end_time.timetuple())
    if last_days:
        mkt_start_time = mkt_end_time - last_days * 3600 * 24
    else:
        mkt_start_time = mkt_end_time - 1 * 3600 * 24
    find_result = db_location.find(
        {
            "user_id": user_id,
            "timestamp": {"$gt": mkt_start_time * 1000,
                          "$lt": mkt_end_time * 1000}
        }).sort([("timestamp", pymongo.DESCENDING)])
    result = []
    for item in find_result:
        location = {
            'latitude': item['location'].get('lat'),
            'longitude': item['location'].get('lng'),
        }
        timestamp = item['timestamp']
        result.append(
            {
                'location': location,
                'timestamp': timestamp,
                'datetime': datetime.fromtimestamp(timestamp / 1000),
                'trace_id': str(item['_id']),
            })
    return result


def get_traces_from_mongodb_by_datetime(user_id, start_time, end_time):
    find_result = db_location.find(
        {
            "user_id": user_id,
            "timestamp": {
                "$gt": time.mktime(start_time.timetuple()) * 1000,
                "$lt": time.mktime(end_time.timetuple()) * 1000,
            }
        }).sort([("timestamp", pymongo.DESCENDING)])
    result = []
    for item in find_result:
        location = {
            'latitude': item['location'].get('lat'),
            'longitude': item['location'].get('lng'),
        }
        timestamp = item['timestamp']
        result.append(
            {
                'location': location,
                'timestamp': timestamp,
                'datetime': datetime.fromtimestamp(timestamp / 1000),
                'trace_id': str(item['_id']),
            })
    return result


def _query_limit(query, max_num=None):
    result = []
    if max_num and max_num < LEANCLOUD_QUERY_LIMIT:
        _query = copy.deepcopy(query)
        _query.limit(max_num)
        return _query.find()

    count = query.count()
    pages = count / LEANCLOUD_QUERY_LIMIT + 1

    # print count
    query_count = 0
    for i in range(pages):
        _query = copy.deepcopy(query)
        _query.limit(LEANCLOUD_QUERY_LIMIT)
        _query.skip(i * LEANCLOUD_QUERY_LIMIT)
        res = _query.find()

        for item in res:
            if max_num and query_count >= max_num:
                return result
            result.append(item)
            query_count += 1

    return result


def get_date_between_events(start_time, end_time, geo_point=None):
    """
    get events between start_time and end_time
    rewrite with leanengine by jayvee_he
    :param start_time:
    :param end_time:
    :param geo_point: input user central location point
    :return:
    """
    _find = dict()
    fm_start_time = datetime.fromtimestamp(int(start_time) / 1000)
    fm_end_time = datetime.fromtimestamp(int(end_time) / 1000)
    _find['start_time'] = {'$gte': fm_start_time}
    _find['end_time'] = {'$lte': fm_end_time}

    max_num = None
    if geo_point:
        _find['location'] = {
            '$near': geo_point
        }
        max_num = DEFAULT_EVENT_NEAR_GEO_POINT
    if max_num:
        find_result = db_activity.find(_find).limit(max_num)
    else:
        find_result = db_activity.find(_find)
    result = []
    for item in find_result:
        r_item = item
        r_item['event_id'] = item['_id']
        result.append(r_item)
    return result


def parse_user_traces(traces):
    user_traces = []
    for item in traces:
        if 'isMockedData' in item:
            pass
        else:
            location = {
                'latitude': item['location'].get('latitude'),
                'longitude': item['location'].get('longitude'),
            }
            timestamp = item['timestamp']
            user_traces.append(
                {
                    'location': location,
                    'timestamp': timestamp,
                    'datetime': datetime.fromtimestamp(timestamp / 1000),
                    'trace_id': item['trace_id'],
                })
    return user_traces


def save_mapping_results_to_leancloud(user_id, map_result,
                                      mapped_locations,
                                      mapped_locations_ids):
    mapped_locations.sort(lambda x, y: cmp(y['timestamp'], x['timestamp']))
    trace_end_time = mapped_locations[0]['timestamp']
    trace_start_time = mapped_locations[-1]['timestamp']
    evidences = []
    for trace_id in mapped_locations_ids:
        evidences.append({'location_id': trace_id})

    # # # # store result to db
    leancloud.init(TIMELINE_APP_ID, TIMELINE_APP_KEY)
    MapActivities = Object.extend('UserActivity')
    map_activities = MapActivities()
    map_activities.set('user_id', user_id)
    map_activities.set('time_range_start',
                       datetime.fromtimestamp(
                           trace_start_time / 1000))
    map_activities.set('time_range_end',
                       datetime.fromtimestamp(
                           trace_end_time / 1000))
    map_activities.set('matched_activities', map_result)
    map_activities.set('is_fake', False)
    map_activities.set('evidence', evidences)
    map_activities.save()


def distance(lon1, lat1, lon2, lat2):
    """
    distance is in meter
    calculate distance from GPS
    :param lon1:
    :param lat1:
    :param lon2:
    :param lat2:
    :return:
    """
    return vincenty((lat1, lon1), (lat2, lon2)).kilometers
