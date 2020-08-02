import csv
import os
import arrow


def readable_time(req_time):
    ts = arrow.get(req_time.timestamp())
    return ts.format('YYYY-MM-DD HH:mm:ss')


def generate_csv_file(file_path, contents):
    with open(file_path, mode='a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=contents[0].keys())

        if os.stat(file_path).st_size == 0:
            writer.writeheader()
        for val in contents:
            writer.writerow(val)
