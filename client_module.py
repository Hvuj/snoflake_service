from imports import Any, ttl_cache
from api import get_version
from facebook_business.api import FacebookAdsApi


@ttl_cache(maxsize=1)
def create_manager_client(account_id: str, access_token: str) -> Any:
    try:
        return FacebookAdsApi.init(
            access_token=access_token,
            account_id=account_id,
            api_version=get_version(),
        )

    except Exception as access_error:
        print(
            "There was an error initiating FB access token \n",
            access_error,
        )
        raise access_error
