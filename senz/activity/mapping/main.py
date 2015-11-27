#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime

from mapper import MatchUserActivity
from util import get_traces_from_mongodb_by_datetime
from util import save_mapping_results_to_leancloud
from util import parse_user_traces


def test_activities_mapping():
    user_ids = [
        '5640632400b0bf378b66e802',
    ]
    for i in range(19, 20):
        for _id in user_ids:
            results = get_traces_from_mongodb_by_datetime(
                _id,
                datetime(2015, 11, i - 1),
                datetime(2015, 11, i))

            user_traces = parse_user_traces(results)

            user_activity_mapping = MatchUserActivity()
            map_result, mapped_locations, mapped_locations_ids = \
                user_activity_mapping.map_trace_activity(
                    trace_list=user_traces)

            if not map_result:
                print("sorry, i can't mapping any activity!")

            if map_result:
                print(map_result)
                save_mapping_results_to_leancloud(_id, map_result,
                                                  mapped_locations,
                                                  mapped_locations_ids)
                print('I have success mapping a user activities.')
                time.sleep(1)


if __name__ == '__main__':
    test_activities_mapping()
