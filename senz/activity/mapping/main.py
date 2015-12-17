#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from mapper import MatchUserActivity
from util import get_traces_from_mongodb_by_datetime
from util import save_mapping_result_to_mongodb
from util import parse_user_traces


def test_activities_mapping():
    user_ids = [
        '5640632400b0bf378b66e802',
        '5640632400b0bf378b66e802',
        '560388c100b09b53b59504d2',
        '55898213e4b0ef61557555a8',
        '5588d20be4b0dc547bacb2ce',
        '56065bba60b2aac0d6f2a38a',
        '5624da0960b27457e89bff13',
    ]
    user_activity_mapping = MatchUserActivity()
    for month in [10, 11]:
        for i in range(2, 30):
            for _id in user_ids:
                results = get_traces_from_mongodb_by_datetime(
                    _id,
                    datetime(2015, month, i - 1),
                    datetime(2015, month, i))

                user_traces = parse_user_traces(results)
                if user_traces:
                    map_result, mapped_locations, mapped_locations_ids = \
                        user_activity_mapping.map_trace_activity(
                            trace_list=user_traces)

                    if not map_result:
                        print("sorry, i can't mapping any activity!")

                    if map_result:
                        print(map_result)
                        save_mapping_result_to_mongodb(_id, map_result,
                                                       mapped_locations,
                                                       mapped_locations_ids)
                        print('I have success mapping a user activities.')


if __name__ == '__main__':
    test_activities_mapping()
