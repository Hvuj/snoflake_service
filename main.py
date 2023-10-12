from imports import Final, Client, bigquery, Optional, Any, datetime, timedelta
from settings import PROJECT_NAME, ACCESS_TOKEN
from client_module import create_manager_client
from data_utils import api_call, upload_data_to_bq
from transformations import map_data, transform_column_names
import functions_framework


@functions_framework.http
def run(request: Optional[Any]) -> str:
    """
    Runs the udf.

    Parameters
    ----------
    request : Optional[Any]
        The payload received that can be used to get dynamic data from outside the function.

    Returns
    -------
    logic: str
        On success - 'True'.
        On failure - 'False'.
    """
    # global start_date, end_date

    try:
        start_date = request.get_json()["start_date"]
        end_date = request.get_json()["end_date"]
    except Exception as e:
        date_type = "%Y-%m-%d"
        start_date = (datetime.now() - timedelta(days=31)).strftime(date_type)
        end_date = (datetime.now() - timedelta(days=2)).strftime(date_type)
    project_id = request.get_json().get("project_id")
    dataset_name = request.get_json().get("dataset_name")
    table_name = request.get_json().get("table_name")
    bq_client: Final[Client] = bigquery.Client(project_id)

    account_id: Final[str] = PROJECT_NAME[project_id]["account_id"]
    access_token: Final[str] = ACCESS_TOKEN

    create_manager_client(account_id=account_id, access_token=access_token)
    raw_data = api_call(account_id=account_id, start_date=start_date, end_date=end_date)
    mapped_data = map_data(data_to_map=raw_data).astype(str)
    mapped_data.columns = transform_column_names(mapped_data)
    upload_data_to_bq(
        client=bq_client,
        project_id=project_id,
        dataset_name=dataset_name,
        table_name=table_name,
        data_to_send=mapped_data,
    )
    return "True"
