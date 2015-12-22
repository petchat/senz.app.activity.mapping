#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import logging

from pyleus.storm import SimpleBolt

from user_activity_mapping.session import redis_location_session
from user_activity_mapping.util import check_user_activities_exists
from user_activity_mapping.util import save_mapping_result_to_mongodb

log = logging.getLogger('save_mapped_result_to_db')


class SmtdBolt(SimpleBolt):
    """
    Save Mapped Result to DB
    """

    def process_tuple(self, tup):
        user_id, evidences, possible_acts, is_exists = tup.values
        log.debug('---SMTD-Bolt---user_id:{0}---'.format(user_id))
        log.debug('---SMTD-Bolt---evidences:{0}---'.format(evidences))
        log.debug('---SMTD-Bolt---possible_acts:{0}---'.format(possible_acts))
        log.debug('---SMTD-Bolt---is_exists:{0}---'.format(is_exists))
        if is_exists:
            # if is exists is true, we can append the evidence to db
            find_results = check_user_activities_exists(user_id, possible_acts)
            # TODO: update user activities evidences ?
            # update user activity evidences
            log.debug('---SMTD-Bolt--update-user-activity-evidences'
                      '--user_id:{0}--evidences:{1}---'.format(
                user_id, evidences))

        else:
            # get user location from redis db
            user_locations = redis_location_session.mget(evidences)
            save_mapping_result_to_mongodb(user_id, possible_acts,
                                           user_locations, evidences)
            log.debug('---SMTD-Bolt--save_to_db--user_id:{0}'
                      '--possible_acts:{1}---'.format(
                user_id, possible_acts))


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='/tmp/save_mapped_result_to_db.log',
        filemode='a',
    )

    SmtdBolt().run()
