from imports import (
    logging,
    bigquery,
    Final,
    LoadJobConfig,
    LoadJob,
    TimePartitioning,
    TimePartitioningType,
    datetime,
    timedelta,
    List,
    Dict,
    Any,
    TypedDict,
    pd,
    contextlib,
)
from facebook_business.adobjects.iguser import IGUser
from facebook_business.adobjects.adaccount import AdAccount


def upload_data_to_bq(
    client: bigquery.Client,
    project_id: str,
    dataset_name: str,
    table_name: str,
    data_to_send,
) -> str:
    """
    Uploads data from a Pandas DataFrame to Google BigQuery.

    Args:
        client: A `bigquery.Client` instance for the desired GCP project.
        project_id: A string representing the project ID where the target dataset resides.
        dataset_name: A string representing the name of the target dataset.
        table_name: A string representing the name of the target table.
        data_to_send: A Pandas DataFrame containing the data to upload.

    Returns:
        A string indicating whether the job completed successfully or not.
    """
    table_id: Final[str] = f"{project_id}.{dataset_name}.{table_name}_staging"

    try:
        logging.info("Pushing data from BigQuery successfully")
        return run_job(client, table_id, data_to_send)
    except Exception as e:
        # Log the error message and raise the exception
        logging.error(f"An error occurred while uploading data to BigQuery: {e}")
        raise e


def run_job(client: bigquery.Client, table_id: str, data_to_send) -> str:
    """
    Uploads a given pandas DataFrame to a specified BigQuery table using the provided BigQuery client object.

    Args:
        client (bigquery.Client): A client object used to interact with BigQuery.
        table_id (str): A string representing the ID of the BigQuery table to upload the data to.
        data_to_send (pd.DataFrame): A pandas DataFrame containing the data to upload to BigQuery.

    Returns:
        str: A string 'True' if the upload was successful.

    Raises:
        This function does not raise any exceptions.

    """
    logging.info(f"Pushing data to table: {table_id}")
    job_config: Final[LoadJobConfig] = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        skip_leading_rows=0,
        source_format=bigquery.SourceFormat.CSV,
        autodetect=False,
        encoding="UTF-8",
        schema=[
            bigquery.SchemaField(
                "date",
                bigquery.enums.SqlTypeNames.DATE,
                description="date",
                mode="NULLABLE",
            ),
            bigquery.SchemaField(
                "value",
                bigquery.enums.SqlTypeNames.INT64,
                description="value",
                mode="NULLABLE",
            ),
            bigquery.SchemaField(
                "name",
                bigquery.enums.SqlTypeNames.STRING,
                description="name",
                mode="NULLABLE",
            ),
            bigquery.SchemaField(
                "description",
                bigquery.enums.SqlTypeNames.STRING,
                description="description",
                mode="NULLABLE",
            ),
            bigquery.SchemaField(
                "type",
                bigquery.enums.SqlTypeNames.STRING,
                description="type",
                mode="NULLABLE",
            ),
            bigquery.SchemaField(
                "id",
                bigquery.enums.SqlTypeNames.INT64,
                description="id",
                mode="NULLABLE",
            ),
        ]
        # clustering_fields=["date", "id"],
        # time_partitioning=TimePartitioning(
        #     type_=TimePartitioningType.MONTH, field="date"
        # ),
    )
    job: Final[LoadJob] = client.load_table_from_dataframe(
        data_to_send, table_id, job_config=job_config
    )  # Make an API request.
    job.result()  # Wait for the job to complete.
    table = client.get_table(table_id)  # Make an API request.
    print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")
    logging.info(f"Upload to BigQuery completed, job status: {job.state}")

    return "True"


def date_range(start_date: str, end_date: str) -> List[str]:
    """
    This function takes in two arguments, start_date and end_date, both of which should be strings of format "YYYY-MM-DD".
    It then creates a list of dates between the start_date and end_date and returns the list.

    :param start_date: The starting date of the range.
    :type start_date: str
    :param end_date: The ending date of the range.
    :type end_date: str
    :return: A list of dates between the start_date and end_date in the format of "YYYY-MM-DD"
    :rtype: List[str]
    :raises ValueError: If the date format is incorrect
    """

    try:
        date_list: List[str] = []
        start_date: datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_date: datetime = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as val_error:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD") from val_error

    current_date: datetime = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    return date_list


def prepare_data_by_day(
    start_date: str,
    end_date: str,
):
    try:
        request_list: Final[List[TypedDict[str, List[TypedDict[str, Any]]]]] = []
        for new_date in date_range(start_date=start_date, end_date=end_date):
            params: Final[Dict[str, Any]] = {
                "metric": "follows_and_unfollows",
                "period": "day",
                "metric_type": "total_value",
                "since": f"{new_date}T00:00:00z",
                "until": f"{new_date}T23:59:59z",
                "breakdown": "follow_type",
            }
            request_list.append(params)
        return request_list
    except ValueError as val_error:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD") from val_error


async def get_iguser_insights(ig_user_id, param):
    with contextlib.suppress(Exception):
        data = pd.DataFrame(IGUser(ig_user_id).get_insights(params=param))
        data["date"] = param["since"]
        full_data = [pd.DataFrame(data)]
        return pd.concat(full_data)


async def get_data(
    list_of_user_ids: List[Dict[str, str]], params: List[Dict[str, str]]
) -> pd.DataFrame:
    tasks = []
    for user in list_of_user_ids:
        for param in params:
            ig_user_id = dict(user)["id"]
            task = asyncio.ensure_future(
                get_iguser_insights(ig_user_id=ig_user_id, param=param)
            )
            tasks.append(task)
    return pd.concat(await asyncio.gather(*tasks, return_exceptions=True))


def api_call(account_id: str, start_date: str, end_date: str):
    ig_users = AdAccount(account_id).get_connected_instagram_accounts()
    params = prepare_data_by_day(start_date=start_date, end_date=end_date)
    return asyncio.run(get_data(ig_users, params))
