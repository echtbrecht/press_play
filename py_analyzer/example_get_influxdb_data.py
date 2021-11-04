import pandas as pd
from influxdb_client import InfluxDBClient
import yaml
import logging


def long_to_wide(long_dataframe):
    """
    InfluxDB uses a long format. Sometimes it easier to use a wide format. This function will turn a
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
    headers = [httpResp.readline() for _ in range(3)]  # stuff i dont need(I think?... not sure about "groups")
    df = pd.read_csv(httpResp)
    df['_time'] = pd.to_datetime(df['_time'])
    return df.drop(columns=df.columns[:2])  # some extra stuff i dont need


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
    # Read the configuration file
    config = {}
    with open('configuration.yml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # Set up the influx db client
    endpoint = f"http://{config['influxdb']['url']}:{config['influxdb']['port']}"
    logging.debug(f"Connecting to following influxdb {endpoint}")
    client = InfluxDBClient(url=endpoint, token=config['influxdb']['token'])
    query_api = client.query_api()

    # Make a query. This one is taken from the InfluxDB webinterface
    query = """from(bucket: "Telegraf")
  |> range(start: -6h)
  |> filter(fn: (r) => r["_measurement"] == "votes")
  """
    # Get data
    result = custom_query_dataframe(query_api, query, org=config['influxdb']['organization'])
    result = long_to_wide(result)
    logging.info(f"Received a dataframe containing {len(result)} records")

    # The end
    logging.info("Congrats! We have data!")
