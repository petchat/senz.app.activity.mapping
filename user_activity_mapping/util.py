#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import time
from datetime import datetime

import pymongo

from bson.son import SON

from geopy.distance import vincenty

from user_activity_mapping.config import MONGODB_HOST, MONGODB_PORT
from user_activity_mapping.config import DB_NAME, DB_USER, DB_PASSWORD
from user_activity_mapping.config import DB_USER_LOCATION_TABLE
from user_activity_mapping.config import DB_USER_ACTIVITY_TABLE
from user_activity_mapping.config import DEFAULT_EVENT_NEAR_GEO_POINT, LEANCLOUD_QUERY_LIMIT
from user_activity_mapping.config import DB_ACTIVITY_TABLE

mongo_client = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT)
db_refinedlog = mongo_client.get_database(DB_NAME)
db_refinedlog.authenticate(DB_USER, DB_PASSWORD)
db_location = db_refinedlog.get_collection(DB_USER_LOCATION_TABLE)
db_activity = db_refinedlog.get_collection(DB_ACTIVITY_TABLE)
db_user_activity = db_refinedlog.get_collection(DB_USER_ACTIVITY_TABLE)


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
            # SON([("$near", geo_point), ("$maxDistance", 200)])
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


def save_mapping_result_to_mongodb(_id, map_result,
                                   mapped_locations,
                                   mapped_locations_ids):
    mapped_locations.sort(lambda x, y: cmp(y['timestamp'], x['timestamp']))
    trace_end_time = mapped_locations[0]['timestamp']
    trace_start_time = mapped_locations[-1]['timestamp']
    evidences = []
    for trace_id in mapped_locations_ids:
        evidences.append({'location_id': trace_id})
    # # # store result to db
    map_activities = dict()
    map_activities['user_id'] = _id
    map_activities['time_range_start'] = datetime.fromtimestamp(
        trace_start_time / 1000)
    map_activities['time_range_end'] = datetime.fromtimestamp(
        trace_end_time / 1000)
    map_activities['matched_activities'] = map_result
    map_activities['is_fake'] = False
    map_activities['evidence'] = evidences
    map_activities['create_at'] = datetime.now()
    db_user_activity.insert_one(map_activities)


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


def get_events_from_mongodb_by_coordinates(
        start_time, end_time,
        coordinates,
        max_num=DEFAULT_EVENT_NEAR_GEO_POINT):
    
    """
    coordinates [lng, lat]
    :param coordinates: [lnt, lat]
    :return: [] events
    """
    query = dict()
    fm_start_time = datetime.fromtimestamp(int(start_time) / 1000)
    fm_end_time = datetime.fromtimestamp(int(end_time) / 1000)
    query['start_time'] = {'$gte': fm_start_time}
    query['end_time'] = {'$lte': fm_end_time}
    query['coordinates'] = SON([("$near", coordinates),
                                ("$maxDistance", 0.2 / 111.2)])

    find_result = db_activity.find(query).limit(max_num)
    result = []
    for item in find_result:
        r_item = item
        r_item['event_id'] = item['_id']
        result.append(r_item)
    return result


def check_user_activities_exists(user_id, possible_acts):
    query = dict()

    acts_ids = [act['event_id'] for act in possible_acts]
    query['matched_activities.event_id'] = {'$in': acts_ids}
    query['user_id'] = {'$eq': user_id}
    find_result = db_activity.find(query).limit(DEFAULT_EVENT_NEAR_GEO_POINT)
    return find_result


# def update_user_activity_evidences(user_id, possible_acts, evidences):
#     acts_ids = [act['event_id'] for act in possible_acts]
#     db_activity.update_one({
#         'user_id': {'$eq': user_id},
#         'matched_activities': {'$in': acts_ids}
#     },{'$set': {}})
