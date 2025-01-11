import requests
import json
import os
from rich.console import Console
from rich.progress import Progress
from rich.traceback import install

# Enable rich tracebacks for better error visibility
install()

# Initialize Rich Console
console = Console()

def select_env():
    envs = [
        "UAT",
        "EUT",
        "PRE PROD",
        "US PROD",
        "US PROD 2",
        "EU PROD",
        "ACCORD EU PROD"
    ]

    subscription_ids = [
        "7c651e19-e4c9-4783-a62b-8ada7a7ed16a",
        "fe9b2128-c21d-4fc7-9275-0a012f074412",
        "6351b8d5-6fa2-4e42-9100-472d994fc245",
        "71e1088e-e5f1-4991-bd18-af1e1926f14d",
        "946458f2-1d72-42a5-8cee-fdd8897462a7",
        "7bede9ea-32ef-4abd-b2c4-6593809b601d",
        "00dd0f57-7fc5-4fd1-88cd-3f685ae21487"
    ]

    resource_groups = [
        "73strings_UAT-01",
        "73Strings-IT-RG-UAT-West-EU",
        "73Strings_wuPreprod_RG",
        "US_Production_instance",
        "73Strings_USProd-2_RG",
        "73Strings-IT-RG-WestEU-Prod",
        "accord-euprod-svc-rg"
    ]

    service_names = [
        "stringsuatapi",
        "strings-it-apim-uat-west-eu",
        "strings-pre-prod-api",
        "strings-prod-us-region",
        "strings-us-prod2",
        "stringsprodapi",
        "accord-euprod-api"
    ]

    console.log("Select the serial number of environment:")
    size = len(envs)
    for index in range(size):
        console.print(f"            {index+1}. {envs[index]}")
    env_number = int(input())

    while True:
        if(env_number>size or env_number <= 0):
            console.print(f"[red]Invalid environment selected, Enter a valid serial number[/red]")
            env_number = int(input())
        else:
            return {
                "subscription_id":subscription_ids[env_number-1],
                "resource_group": resource_groups[env_number-1],
                "service_name":service_names[env_number-1]
            }





# def get_subscription_id():
#     subscriptions = [
#         "73 Strings PRE PROD",
#         "73 Strings UAT",
#         "73 Strings US PROD",
#         "73 Strings US PROD 2",
#         "73s-accord-euprod",
#         "73Strings_EU PROD",
#         "73Strings_EUT"
#         ]
#     subscription_ids = [
#         "6351b8d5-6fa2-4e42-9100-472d994fc245",
#         "7c651e19-e4c9-4783-a62b-8ada7a7ed16a",
#         "71e1088e-e5f1-4991-bd18-af1e1926f14d",
#         "946458f2-1d72-42a5-8cee-fdd8897462a7",
#         "00dd0f57-7fc5-4fd1-88cd-3f685ae21487",
#         "7bede9ea-32ef-4abd-b2c4-6593809b601d",
#         "fe9b2128-c21d-4fc7-9275-0a012f074412"
#         ]

        
#     console.log("Select the serial number of subscription:")
#     size = len(subscriptions)
#     for index in range(size):
#         console.print(f"            {index+1}. {subscriptions[index]}")
#     subscription_number = int(input())

#     while True:
#         if(subscription_number>size or subscription_number <= 0):
#             console.print(f"[red]Invalid subscription selected, Enter a valid serial number[/red]")
#             subscription_number = int(input())
#         else:
#             return subscription_ids[subscription_number-1]

# def get_resource_group(subscription_id):
#     resource_groups = []



def get_info():
    # subscription_id = get_subscription_id()
    info = select_env()

    # Replace these variables with your Azure details
    api_id = "your_api_id"
    swagger_file_path = "path_to_your_swagger.json"

    # Azure management endpoint
    url = f"https://management.azure.com/subscriptions/{info.get('subscription_id')}/resourceGroups/{info.get('resource_group')}/providers/Microsoft.ApiManagement/service/{info.get('service_name')}/apis/{api_id}?api-version=2023-03-01-preview"

    console.log(url)
    # for uat url shoule be
    #https://management.azure.com/subscriptions/7c651e19-e4c9-4783-a62b-8ada7a7ed16a/resourceGroups/73strings_UAT-01/providers/Microsoft.ApiManagement/service/stringsuatapi/apis/debt-model-api-documentation?import=true&api-version=2022-09-01-preview
    return {
        "url":url,
        "swagger_file_path":swagger_file_path
    }

# Function to get Azure access token using Azure CLI
def get_access_token():
    console.log("Fetching Azure access token...")
    try:
        result = os.popen("az account get-access-token --query accessToken --output tsv").read().strip()
        console.log("[green]Access token fetched successfully![/green]")
        return result
    except Exception as e:
        console.log(f"[red]Error getting access token: {e}[/red]")
        return None

# Function to read the Swagger (OpenAPI) file
def read_swagger_file(file_path):
    console.log(f"Reading Swagger file from [blue]{file_path}[/blue]...")
    try:
        with open(file_path, 'r') as file:
            console.log("[green]Swagger file read successfully![/green]")
            return file.read()
    except FileNotFoundError:
        console.log("[red]Swagger file not found![/red]")
        return None

# Main function to update Swagger in APIM
def update_swagger():
    access_token = get_access_token()
    swagger_file_path = get_info().swagger_file_path

    if not access_token:
        console.log("[red]Failed to get access token.[/red]")
        return

    swagger_content = read_swagger_file(swagger_file_path)
    if not swagger_content:
        console.log("[red]Failed to read Swagger file.[/red]")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "properties": {
            "format": "openapi+json",
            "value": json.loads(swagger_content),
            "path": "api-path"
        }
    }

    info = get_info()

    with Progress() as progress:
        task = progress.add_task("[cyan]Updating Swagger in APIM...", total=100)

        response = requests.put(info.url, headers=headers, json=body)
        progress.update(task, advance=100)

    if response.status_code == 200:
        console.log("[green]Swagger file updated successfully![/green]")
    else:
        console.log(f"[red]Failed to update Swagger. Status code: {response.status_code}[/red]")
        console.log(f"Response: {response.text}")

# Run the script
if __name__ == "__main__":
    console.rule("[bold blue]Azure Swagger Updater[/bold blue]")
    # update_swagger()
    get_info()
