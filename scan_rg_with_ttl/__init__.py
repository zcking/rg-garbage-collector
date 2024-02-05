import logging
import os
import json
from datetime import datetime, date

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
import azure.functions as func


subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

TAG_DELETE_AT = "DeleteAt"

app = func.FunctionApp()


def main(myTimer: func.TimerRequest) -> None:
    """Timer trigger function for scanning Resource Groups for deletion.

    The following features are implemented:
    - Tag "DeleteAt" is used to give a date when the resource group should be deleted

    Args:
        timer (func.TimerRequest): azure function timer request
    """
    print("Function starting...")
    if myTimer.past_due:
        logging.warning("The timer is past due!")

    # Create a credential object using the default Azure credentials
    credential = DefaultAzureCredential()

    # Create a ResourceManagementClient object
    resource_client = ResourceManagementClient(credential, subscription_id)

    # Get all resource groups in the current subscription
    # that have the "DeleteAt" tag populated
    resource_groups = resource_client.resource_groups.list(filter="tagname eq 'DeleteAt'")

    # Iterate through the resource groups and flag those that should be deleted
    flagged_resource_groups = {}
    for resource_group in resource_groups:
        #sanity
        if not resource_group.tags:
            continue

        # If the resource group is already being deleted, skip it
        if resource_group.properties.provisioning_state == "Deleting":
            continue

        if TAG_DELETE_AT in resource_group.tags:
            # Parse the date from the tag value, in the format "YYYY-MM-DD"
            delete_at = datetime.strptime(resource_group.tags[TAG_DELETE_AT], "%Y-%m-%d")
            if delete_at.date() <= date.today():
                flagged_resource_groups[resource_group.name] = resource_group.as_dict()
        
    # Delete the flagged resource groups
    for rg in flagged_resource_groups:
        # Delete the resource group, or log an error if it fails
        try:
            logging.info(f"Deleting resource group {rg}...")
            resource_client.resource_groups.begin_delete(rg)
        except Exception as e:
            logging.error(f"Failed to delete resource group {rg}: {e}")

    response_body = json.dumps({
        "deleted": flagged_resource_groups,
    })
    return func.HttpResponse(response_body, mimetype="application/json")
