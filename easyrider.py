import json
import re
from collections import namedtuple, defaultdict
from itertools import groupby

STOP_NAME_FORMAT_TEMPLATE = r'^([A-Z][a-z]+ )+(Road|Avenue|Boulevard|Street)$'
BUS_STATION_TYPES = {'S', 'O', 'F', ''}
A_TIME_FORMAT_TEMPLATE = r'[0-2][0-9]:[0-5][0-9]'

Station = namedtuple(
    'Station',
    ['bus_id', 'stop_id', 'stop_name', 'next_stop', 'stop_type', 'a_time']
)


def validate_station(station: Station, errors: dict, bus_lines: dict) -> None:
    def validate_bus_id(bus_id) -> bool:
        return isinstance(bus_id, int)

    def validate_stop_id(stop_id) -> bool:
        return isinstance(stop_id, int)

    def validate_stop_name(stop_name) -> bool:
        return isinstance(stop_name, str) and len(stop_name) > 0 and re.match(STOP_NAME_FORMAT_TEMPLATE, stop_name)

    def validate_next_stop(next_stop) -> bool:
        return isinstance(next_stop, int)

    def validate_stop_type(stop_type) -> bool:
        return isinstance(stop_type, str) and stop_type in BUS_STATION_TYPES

    def validate_a_time(a_time) -> bool:
        return isinstance(a_time, str) and len(a_time) > 0 and re.match(A_TIME_FORMAT_TEMPLATE, a_time)

    if not validate_bus_id(station.bus_id):
        errors[station._fields[0]] += 1
    else:
        bus_lines[station.bus_id] += 1
    if not validate_stop_id(station.stop_id):
        errors[station._fields[1]] += 1
    if not validate_stop_name(station.stop_name):
        errors[station._fields[2]] += 1
    if not validate_next_stop(station.next_stop):
        errors[station._fields[3]] += 1
    if not validate_stop_type(station.stop_type):
        errors[station._fields[4]] += 1
    if not validate_a_time(station.a_time):
        errors[station._fields[5]] += 1


def display_errors(errors: dict) -> None:
    print(f'Type and field validation: {sum(errors.values())} errors')
    for error, count in errors.items():
        print(f'{error}: {count}')


def display_bus_lines(bus_lines: dict) -> None:
    print('\nLine names and number of stops:')
    for line, stops in bus_lines.items():
        print(f'bus_id: {line}, stops: {stops}')


def validate_bus_lines(data: list[dict], stop_types: dict, errors: dict):
    station_names = [station['stop_name'] for station in data]
    for station_name in station_names:
        if station_names.count(station_name) > 1:
            stop_types['transfer_stops'].add(station_name)

    for station in data:
        if station['stop_type'] == 'S':
            stop_types['start_stops'].add(station['stop_name'])
        elif station['stop_type'] == 'F':
            stop_types['finish_stops'].add(station['stop_name'])
        elif station['stop_type'] == 'O' and station['stop_name'] not in stop_types['transfer_stops']:
            stop_types['on_demand_stops'].add(station['stop_name'])

    for bus_line, group in groupby(data, key=lambda x: x['bus_id']):
        last_time = 0
        for station in group:
            current_time = int(station['a_time'].replace(':', ''))
            if current_time <= last_time:
                errors['a_time'] += 1
                break
            else:
                last_time = current_time


def display_stop_types(stop_types: dict):
    start_stations = list(stop_types['start_stops'])
    start_stations.sort()
    transfer_stations = list(stop_types['transfer_stops'])
    transfer_stations.sort()
    finish_stations = list(stop_types['finish_stops'])
    finish_stations.sort()
    on_demand_stops = list(stop_types['on_demand_stops'])
    on_demand_stops.sort()
    print(f'\nStart stops: {len(start_stations)} {start_stations}')
    print(f'Transfer stops: {len(transfer_stations)} {transfer_stations}')
    print(f'Finish stops: {len(finish_stations)} {finish_stations}')
    print(f'On demand stops: {len(on_demand_stops)} {on_demand_stops}')


def main() -> None:
    data = json.loads(input())
    errors = dict.fromkeys(Station._fields, 0)
    bus_lines = defaultdict(int)
    stop_types = defaultdict(set)

    for station_info in data:
        bus_station = Station(**station_info)
        validate_station(bus_station, errors, bus_lines)

    if not all((errors['bus_id'], errors['stop_name'], errors['stop_type'])):
        validate_bus_lines(data, stop_types, errors)

    display_errors(errors)
    display_bus_lines(bus_lines)
    display_stop_types(stop_types)


if __name__ == "__main__":
    main()
