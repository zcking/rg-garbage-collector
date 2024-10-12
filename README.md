# rg-garbage-collector

Automatically clean up Azure resource groups based on tags. Useful for development sandboxes and cost control.

## Usage

Create or update your Azure Resource Group with the tag `DeleteAt` and give it the value of the date you want the resource group to be deleted. The date should be in the format `YYYY-MM-DD`. When the `rg-garbage-collector` runs, it will delete any resource group that has a `DeleteAt` tag with a date in the past.

## Deployment

The `rg-garbage-collector` is a Python application that can be deployed as an Azure Function. The function is triggered by a timer trigger that runs every 24 hours. If you would like to change the schedule it runs at you can update the [function.json](./scan_rg_with_ttl/function.json) file.

To deploy the function you can use the Azure CLI or the Azure Portal. The function requires the `AZURE_SUBSCRIPTION_ID` environment variable to be set. This is the subscription that the function will list and delete resource groups from. You may reference the [GitHub Actions workflow](./.github/workflows/main_rg-garbage-collector.yml) for automatically deploying to your Azure cloud environment from CI/CD pipelines.

Once the function has been deployed it will run on schedule and iterate through all resource groups in the subscription and delete any resource group that has a `DeleteAt` tag with a date in the past.


