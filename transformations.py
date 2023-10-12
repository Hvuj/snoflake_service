from imports import pd, List


def apply_func_on_df(df, func_to_run, **kwargs):
    """
    Apply a given function to each row of a DataFrame.

    Args:
        df (pandas.DataFrame or dask.DataFrame): The DataFrame to apply the function on.
        func_to_run (callable): The function to apply on each row.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        pandas.Series or dask.Series: The result of applying the function to each row.

    """
    if kwargs:
        return df.apply(func_to_run, axis=1, kwargs=kwargs)
    return df.apply(func_to_run, axis=1)


def get_date(element):
    return element.date.split("T")[0]


def get_id(element):
    return element.id.split("/")[0]


def extract_dimension_key_follower(element):
    return element[0]["results"][0]["dimension_values"][0]


def extract_dimension_key_non_follower(element):
    return element[0]["results"][1]["dimension_values"][0]


def extract_dimension_values(row):
    results = row[0]["results"]
    dimension_values = [result["dimension_values"][0] for result in results]
    values = [result["value"] for result in results]
    return list(zip(dimension_values, values))


def map_data(data_to_map):
    data_to_map["date"] = pd.to_datetime(
        apply_func_on_df(df=data_to_map, func_to_run=get_date)
    ).dt.date

    data_to_map["id"] = apply_func_on_df(df=data_to_map, func_to_run=get_id)

    data_to_map["breakdowns"] = data_to_map["total_value"].str.get("breakdowns")

    data_to_map["dimension_values_and_values"] = data_to_map["breakdowns"].apply(
        extract_dimension_values
    )

    data_to_map = data_to_map.explode("dimension_values_and_values")
    data_to_map[["type", "value"]] = pd.DataFrame(
        data_to_map["dimension_values_and_values"].tolist(), index=data_to_map.index
    )

    data_to_map = data_to_map.drop(
        ["breakdowns", "dimension_values_and_values", "total_value", "period", "title"],
        axis=1,
    )

    return data_to_map


def transform_column_names(report_data: pd.DataFrame) -> List[str]:
    """
    Transform column names of a DataFrame to a specific format.

    Args:
        report_data (dask.DataFrame): The DataFrame containing the report data.

    Returns:
        List[str]: A list of transformed column names.

    Raises:
        ValueError: If an error occurs during the transformation.

    """
    try:
        bq_schema: List[str] = [
            "".join(f"_{char.lower()}" if char.isupper() else char for char in word)
            for word in report_data.columns.tolist()
        ]
        return bq_schema
    except ValueError as value_error:
        print(f"There is no:{value_error}")
        raise value_error
