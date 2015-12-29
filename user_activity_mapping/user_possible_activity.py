#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import json
import logging

from pyleus.storm import SimpleBolt

from user_activity_mapping.session import redis_location_session
from user_activity_mapping.session import user_activity_session
from user_activity_mapping.util import get_events_from_mongodb_by_coordinates

log = logging.getLogger('user_possible_activity')


class UpaBolt(SimpleBolt):
    """
    User Possible Activities Bolt
    """
    OUTPUT_FIELDS = ['user_id', 'user_location', 'possible_acts']

    def process_tuple(self, tup):
        _raw_data_str = tup.values[0]

        log.debug('--UpaBolt--get-location--:' +
                  str(_raw_data_str['location']))

        user_location = json.loads(_raw_data_str['location'])

        user_id = user_location['user_id']
        log.debug('--UpaBolt--get-user_id--:' + str(user_id))

        _timestamp = user_location['timestamp']
        log.debug('--UpaBolt--get-timestamp--:' + str(_timestamp))

        coordinates = [user_location['location']['lng'],
                       user_location['location']['lat']]

        # get possible activity
        possible_acts = get_events_from_mongodb_by_coordinates(
            _timestamp,
            _timestamp,
            coordinates)

        # 如果有可能的活动传出去 准备多次匹配
        if possible_acts:
            log.debug('--UpaBolt--user_id--possible_activities--: %s----%s'
                      % (user_id, possible_acts))
            # save current location to db and possible acts
            redis_location_session.setex(user_location['_id'],
                                         3600 * 2,
                                         user_location)

            # save possible activities in redis db
            for act in possible_acts:
                event_id = act['event_id']
                _saved_acts = user_activity_session.get(user_id)
                if not _saved_acts:
                    save_acts = dict()
                    save_acts[event_id] = [user_location['_id']]
                    user_activity_session.setex(
                        user_id, 3600 * 24,
                        save_acts)

                elif event_id not in _saved_acts:
                    _saved_acts[event_id] = [user_location['_id']]
                    user_activity_session.setex(
                        user_id, 3600 * 24,
                        _saved_acts)
                else:
                    _saved_acts[event_id].append = user_location['_id']
                    user_activity_session.setex(
                        user_id, 3600 * 24,
                        _saved_acts)

            self.emit((user_id, user_location, possible_acts))


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='/tmp/user_possible_activity.log',
        filemode='a',
    )

    UpaBolt().run()
