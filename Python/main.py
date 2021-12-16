import os
from datetime import datetime, timezone
import numpy as np
import logging
import pandas as pd
from influxdb_client import InfluxDBClient
import time

pd.set_option('display.max_columns', None)


def long_to_wide(long_dataframe):
    """
    InfluxDB uses a long format. Sometimes it is easier to use a wide format. This function will turn a
    long format into a wide format.
    :param long_dataframe:
    :return:
    """
    index = ['_time'] + [column for column in long_dataframe.columns if column[0] != '_']
    index.remove('table')
    long_dataframe = long_dataframe.pivot(index=index, columns=['_field'])['_value'].reset_index()
    return long_dataframe


def custom_query_dataframe(query_api, qs, org):
    """
    Function I've ripped from GitHub (https://github.com/influxdata/influxdb-client-python/issues/72)
    to speed up querying from InfluxDB.
    :param query_api:
    :param qs:
    :param org:
    :return:
    """
    httpResp = query_api.query_raw(qs, org=org)
    headers = [httpResp.readline() for _ in range(3)]
    # stuff I don't need(I think?... not sure about "groups")
    df = pd.read_csv(httpResp)
    df['_time'] = pd.to_datetime(df['_time'])
    return df.drop(columns=df.columns[:2])  # some extra stuff I don't need


def reset(config, start_time_window, start_unit):
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    # Set up the influx db client
    endpoint = f"http://{config['url']}:{config['port']}"
    logging.debug(f"Connecting to following influxdb {endpoint}")
    client = InfluxDBClient(url=endpoint, token=config['token'])
    query_api = client.query_api()

    # Make a query. This one is taken from the InfluxDB webinterface
    query = f"""from(bucket: "telegraf_data")
            |> range(start: {start_time_window}{start_unit})
            |> filter(fn: (r) =>r["_measurement"] == "controllers")
            """

    # Get data
    result = custom_query_dataframe(query_api, query, org=config['organization'])
    result = long_to_wide(result)
    df_influx = pd.DataFrame(columns=['_time'] + list(result['id'].unique()))
    df_influx.set_index(['_time'], inplace=True)
    n = len(result['id'].unique())
    n_cycle = 0
    id_list = list(result['id'].unique())

    # first check whether file exists or not
    # calling remove method to delete the csv file
    # in remove method you need to pass file name and type
    file = 'output.csv'
    if (os.path.exists(file) and os.path.isfile(file)):
        os.remove(file)
        print("file deleted")
    else:
        print("file not found")

    return df_influx, n, n_cycle, id_list


def loop_get_data(df_influx, start_utc, n_cycle, step, id_list):
    # df_parameters = op('table_parameters')
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    # Set up the influx db client
    endpoint = f"http://{config['url']}:{config['port']}"
    # logging.debug(f"Connecting to following influxdb {endpoint}")
    client = InfluxDBClient(url=endpoint, token=config['token'])
    query_api = client.query_api()

    # n_cycle = df_parameters['n_cycle',1]
    start = np.add(start_utc, n_cycle * step)
    print('start ', start)
    # stop = np.add(start, step)
    # print('stop ', stop)

    # Make a query. This one is taken from the InfluxDB webinterface
    query = f"""
    from(bucket: "telegraf_data")
    |> range(start: {start_utc},stop: -10s)
    |> filter(fn: (r) => r["_measurement"] == "controllers")
    |> filter(fn: (r) => r["_field"] == "button")
    |> aggregateWindow(every: 1s, fn: first, createEmpty: true)
    |> keep(columns: ["_time", "id","_value"])
    |> pivot(rowKey:["_time"], columnKey: ["id"], valueColumn: "_value")
    """

    # Get data
    result = client.query_api().query_data_frame(org=config['organization'], query=query)
    print(result)
    if result.empty is False:
        #result = result[['_time','id','_value']]
        result = result.drop(columns=['result', 'table'])
        print(result)
        result = result.replace(1.0, True)
        result = result.replace(2.0, False)
        #result['_time'] = (result['_time'].astype(int) / 10**9).astype(int)
        #result['_value'] = np.where(result['_value'] == 1.0, True, False)
        #for i in range(len(result)):
        #    print(result.iloc[i, 0])
        #    print(result.iloc[i, 1])
        #    df_influx.loc[start, result.iloc[i, 0]] = result.iloc[i, 1]
        #    print(result)
        logging.info("Congrats! We have data!")
    #else:
    #    df_influx.loc[start] = [None] * len(id_list)
        df_influx = result
    return df_influx


if __name__ == '__main__':
    # Read the configuration file
    config = {'url': 'localhost',
              'port': 8086,
              'token': 'oursecrettoken',
              'organization': 'press_play'}
    start_time_window = -632000
    start_unit = 's'
    df_influx, n, n_cycle, id_list = reset(config, start_time_window, start_unit)
    # print(n)
    # print(id_list)
    dt = datetime.now(timezone.utc)
    start_utc = int(time.mktime(dt.timetuple())) + 3588
    start_time = time.time()
    step = 1
    for i in range(3000):
        time.sleep(start_time + i * step - time.time())
        df_influx = loop_get_data(df_influx, start_utc, n_cycle, step, id_list)
        n_cycle = np.add(n_cycle, 1)
        print(n_cycle)
        df_influx.fillna('nan', inplace=True)
        df_influx.to_csv('output.csv', index=False)
    print(df_influx.head())
