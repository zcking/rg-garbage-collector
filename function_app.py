import logging
import os

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
import azure.functions as func


subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

app = func.FunctionApp()

@app.function_name(name="rg_garbage_collector")
@app.schedule(schedule="0 0 0 * * *", arg_name="my_timer", run_on_startup=True,
              use_monitor=False)
def timer_trigger(my_timer: func.TimerRequest) -> None:
    """Timer trigger function for scanning Resource Groups for deletion.

    Args:
        my_timer (func.TimerRequest): azure function timer request
    """
    if my_timer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')
    # Create a credential object using the default Azure credentials
    credential = DefaultAzureCredential()

    # Create a ResourceManagementClient object
    resource_client = ResourceManagementClient(credential, subscription_id)

    # Get all resource groups in the current subscription
    resource_groups = resource_client.resource_groups.list()

    # Iterate over the resource groups and print their names
    for resource_group in resource_groups:
        print(resource_group.name)
        print(resource_group.tags)
        print('---' * 10)
