import pandas as pd
from influxdb_client import InfluxDBClient


def long_to_wide(result):
    """
    InfluxDB uses a long format. Sometimes it easier to use a wide format. This function will turn a
    long format into a wide format.
    :param result:
    :return:
    """
    index = ['_time']+[column for column in result.columns if column[0] != '_']
    index.remove('table')
    result = result.pivot(index=index, columns=['_field'])['_value'].reset_index()
    return result


def custom_query_dataframe(query_api,qs,org):
    """
    Function I've ripped from GitHub (https://github.com/influxdata/influxdb-client-python/issues/72)
    to speed up querying from InfluxDB.
    :param query_api:
    :param qs:
    :param org:
    :return:
    """
    httpResp = query_api.query_raw(qs,org=org)
    headers = [httpResp.readline() for _ in range(3)] # stuff i dont need(I think?... not sure about "groups")
    df = pd.read_csv(httpResp)
    return df.drop(columns=df.columns[:2]) # some extra stuff i dont need



if __name__ == "__main__":
    print('hello world')