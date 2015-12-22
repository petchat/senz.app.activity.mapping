#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import logging

from pyleus.storm import SimpleBolt

from user_activity_mapping.session import user_activity_session
from user_activity_mapping.util import check_user_activities_exists


log = logging.getLogger('mapping_user_possible_activity')


class MupaBolt(SimpleBolt):
    """
    Mapping User Possible activities
    """
    OUTPUT_FIELDS = ['user_id', 'evidences', 'activities', 'is_exists']

    def process_tuple(self, tup):
        user_id, user_location, possible_acts = tup.values

        # log receive data
        log.debug('--MupaBolt--get-user-id--:{0}'.format(user_id))
        log.debug('--MupaBolt--get-user-location--:{0}'.format(
            user_location))
        log.debug('--MupaBolt--get-user-possible-activities--:{0}'.format(
            possible_acts))

        # check db has current user and possible activities
        is_exists = check_user_activities_exists(user_id,
                                                 possible_acts)

        if is_exists:
            # if there is mapped user's activities
            #  then append the evidences.
            # _saved_acts = user_activity_session.get(user_id)
            self.emit((user_id, [user_location['_id']],
                       possible_acts, True))

        else:
            # user_id and event_id
            _saved_acts = user_activity_session.get(user_id)
            for _event_id in _saved_acts:
                if len(_saved_acts[_event_id]) > 3:
                    # we think current user mapped to this activity
                    self.emit((user_id, _saved_acts[_event_id],
                               possible_acts, False))
                    del _saved_acts[_event_id]


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='/tmp/mapping_user_possible_activity.log',
        filemode='a',
    )

    MupaBolt().run()
