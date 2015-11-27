#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time

from util import get_date_between_events
from util import distance
from config import DEFAULT_ACTIVITY_LAST_TIME
from config import DEFAULT_NEAR_POI_DISTANCE_THRESHOLD


class MatchUserActivity(object):
    def __init__(self):
        self.mappingList = {}
        self.locations = []
        self.activities = []
        self.mapped = False  # tell the method if updating the results
        self.last_mappin_time = None  # retrieve the time from the db or the file
        # it's for checking the mapping period in case the info is outdated
        self.mapped_activities = {}

    # Consider whether user in this activity
    def _is_in_activity(self, user_traces, activity):
        """
        Is in activity.
        :param user_traces:
        :param activity:
        :return:
        """
        # geo point
        aty_lng = activity['location'].longitude
        aty_lat = activity['location'].latitude

        active_time = []
        active_loc_records = []
        activities_time_trace = []
        s_time = time.mktime(activity['start_time'].timetuple())

        # if has not end_time, mock an end_time data
        if (('end_time' in activity) and
                (activity['start_time'] != activity['end_time'])):
            e_time = time.mktime(activity['end_time'].timetuple())

        elif activity['category'] in DEFAULT_ACTIVITY_LAST_TIME:
            e_time = s_time + DEFAULT_ACTIVITY_LAST_TIME[activity['category']]

        else:
            e_time = s_time + (3600 * 6)

        #
        for _trace in user_traces:
            if 'location' in _trace:
                u_loc = _trace['location']
            else:
                u_loc = _trace

            u_lng = u_loc['longitude']
            u_lat = u_loc['latitude']

            _timestamp = _trace['timestamp'] / 1000

            if s_time < _timestamp < e_time:
                activities_time_trace.append(_trace)
                dist = distance(aty_lng, aty_lat, u_lng, u_lat)

                if dist < DEFAULT_NEAR_POI_DISTANCE_THRESHOLD:
                    active_time.append(_trace['timestamp'])
                    active_loc_records.append(_trace)

        len_active_time = len(active_time)

        if 0 < len_active_time >= 3:
            active_loc_records.sort(key=lambda x: x["timestamp"])
            min_timestamp = datetime.datetime.fromtimestamp(
                active_loc_records[0]['timestamp'] / 1000)
            max_timestamp = datetime.datetime.fromtimestamp(
                active_loc_records[-1]['timestamp'] / 1000)

            if (max_timestamp - min_timestamp).total_seconds() > 1800:
                return active_loc_records

        return []

    def _get_pos_activities(self, start_date, end_date, geo_point=None):
        """
        Get possible activities
        :param start_date:
        :param end_date:
        :param geo_point:
        :return:
        """
        if geo_point:
            all_activities = get_date_between_events(
                start_date, end_date, geo_point)
        else:
            all_activities = get_date_between_events(
                start_date, end_date)
        return all_activities

    def map_trace_activity(self, trace_list):
        """
        map activity by trace, data stored on leancloud  @Jayvee
        :param trace_list:
        :return:
        """
        if trace_list:
            # descend by timestamp
            trace_list.sort(lambda x, y: cmp(y['timestamp'], x['timestamp']))
            trace_end_time = trace_list[0]['timestamp']
            trace_start_time = trace_list[-1]['timestamp']

            lat_sum = 0.0
            lng_sum = 0.0
            for trace in trace_list:
                lat_sum += trace['location']['latitude']
                lng_sum += trace['location']['longitude']

            activities = self._get_pos_activities(trace_start_time,
                                                  trace_end_time)
            self.locations = trace_list
        else:
            self.locations = []
            return []

        # todo get the user's last place
        res = []
        mapped_locations = []
        mapped_locations_ids = []
        for ac in activities:
            results = self._is_in_activity(self.locations, ac)
            if results:
                res.append(ac)
                for item in results:
                    if str(item['trace_id']) not in mapped_locations_ids:
                        mapped_locations.append(item)
                        mapped_locations_ids.append(str(item['trace_id']))

        return res, mapped_locations, mapped_locations_ids
