"""IBM Cloud Function that gets all reviews for a dealership

Returns:
    List: List of reviews for the given dealership
"""
from cloudant.client import Cloudant
from cloudant.error import CloudantException
import requests


def main(param_dict):
    """Main Function

    Args:
        param_dict (Dict): input paramater

    Returns:
        _type_: _description_ TODO
    """

    try:
        client = Cloudant.iam(
            account_name=param_dict["https://apikey-v2-362iuztsewhc5fyvsqz1x5qizsty4clva6wogfsrv1e9:0b2374ecb5a964bb0870d89b5189a32a@f4269b51-8a28-4d6f-9d9d-906b353c80bc-bluemix.cloudantnosqldb.appdomain.cloud"],
            api_key=param_dict["X6cV4GxKuDhfilvjWO1SJHhet_jRmJ8Jo1KAckvDY-Cy"],
            connect=True,
        )
        print(f"Databases: {client.all_dbs()}")
    except CloudantException as cloudant_exception:
        print("unable to connect")
        return {"error": cloudant_exception}
    except (requests.exceptions.RequestException, ConnectionResetError) as err:
        print("connection error")
        return {"error": err}

    return {"dbs": client.all_dbs()}
