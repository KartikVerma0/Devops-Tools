#!/usr/local/bin/python
import requests
import json
import os
import shutil
import sys
from rich.console import Console
from rich.progress import Progress
from rich.traceback import install
from openapi_spec_validator import validate_spec
from openapi_spec_validator.exceptions import OpenAPISpecValidatorError

# Enable rich tracebacks for better error visibility
install()

# Initialize Rich Console
console = Console()

def select_env():
    """
    Returns environment details \n
    {
        "subscription_id",\n
        "resource_group",\n
        "service_name",\n
        "environment"\n
    }
    """
    envs = [
        {
            "env":"UAT",
            "subscription_id":"7c651e19-e4c9-4783-a62b-8ada7a7ed16a",
            "resource_group":"73strings_UAT-01"
        },
        {
            "env":"EUT",
            "subscription_id":"fe9b2128-c21d-4fc7-9275-0a012f074412",
            "resource_group":"73Strings-IT-RG-UAT-West-EU"
        },
        {
            "env":"PRE PROD",
            "subscription_id":"6351b8d5-6fa2-4e42-9100-472d994fc245",
            "resource_group":"73Strings_wuPreprod_RG"
        },
        {
            "env":"US PROD",
            "subscription_id":"71e1088e-e5f1-4991-bd18-af1e1926f14d",
            "resource_group":"US_Production_instance"
        },
        {
            "env":"US PROD 2",
            "subscription_id":"946458f2-1d72-42a5-8cee-fdd8897462a7",
            "resource_group":"73Strings_USProd-2_RG"
        },
        {
            "env":"EU PROD",
            "subscription_id":"7bede9ea-32ef-4abd-b2c4-6593809b601d",
            "resource_group":"73Strings-IT-RG-WestEU-Prod"
        },
        {
            "env":"ACCORD EU PROD",
            "subscription_id":"00dd0f57-7fc5-4fd1-88cd-3f685ae21487",
            "resource_group":"accord-euprod-svc-rg"
        },
        {
            "env":"ACCORD UAT",
            "subscription_id":"a1765757-982b-4940-81d6-f06a52f22935",
            "resource_group":"accord-uat-svc-rg"
        },
        {
            "env":"Automation Testing",
            "subscription_id":"7d69fe92-15ec-4013-9b31-35fdbe8aca85",
            "resource_group":"Training-RG"
        }
    ]
    

    console.log("Select the serial number of environment:")
    size = len(envs)
    for index in range(size):
        console.print(f"            {index+1}. {envs[index].get('env')}")
    env_number = int(input())
    selection = verify_selection()

    while True:
        if not selection:
            console.log(f"Enter the serial number of environment")
            env_number = int(input())
            selection = verify_selection()
        elif(env_number>size or env_number <= 0):
            console.print(f"[red]Invalid environment selected, Enter a valid serial number[/red]")
            env_number = int(input())
            selection = verify_selection()
        else:
            return {
                "subscription_id":envs[env_number-1].get('subscription_id'),
                "resource_group": envs[env_number-1].get('resource_group'),
                "service_name": select_service_names(env_number-1),
                "environment": envs[env_number-1].get('env')
            }

def verify_selection():
    console.log("Do you want to confirm your selection? (Y/N)")
    selection = input()

    if selection.lower() == "n":
        return False
    elif selection == "" or selection.lower() == "y":
        return True
    return False

def select_service_names(env_number):
    """
    Returns service name
    """
    service_names = [
        [
            "stringsuatapi",
            "uatapi-73strings"
        ],
        [
            "strings-it-apim-uat-west-eu",
            "api-eut-73strings"
        ],
        [
            "strings-pre-prod-api",
        ],
        [
            "strings-prod-us-region",
            "api-us-73strings"
        ],
        [
            "strings-us-prod2",
            "api-usa-73strings"
        ],
        [
            "stringsprodapi",
            "api-73strings"
        ],
        [
            "accord-euprod-api",
        ],
        [
            "accord-uat-api",
        ],
        [
            "swagger-automation-apim",
        ]
    ]

    console.log("Select the serial number of service:")
    size = len(service_names[env_number])
    _index = 0
    for _service in service_names[env_number]:
        console.print(f"            {_index+1}. {_service}")
        _index+=1
    service_number = int(input())
    selection = verify_selection()

    while True:
        if not selection:
            console.log(f"Enter the serial number of service")
            service_number = int(input())
            selection = verify_selection()
        elif(service_number>size or service_number <= 0):
            console.print(f"[red]Invalid service selected, Enter a valid serial number[/red]")
            service_number = int(input())
            selection = verify_selection()
        else:
            return service_names[env_number][service_number-1]



def get_info(access_token):
    """
    Return patch url and swagger file content\n
    {
        "url",\n
        "patch_url,"\n
        "swagger_file",\n
        "api_details"
    }
    """
    env_details = select_env()

    # Replace these variables with your Azure details
    api_details = get_api_details(env_details,access_token)
    api_id = api_details.get('api_id')
    swagger_file = get_swagger_file(env_details.get('environment'),api_details.get('path'))

    # Azure management endpoint
    url = f"https://management.azure.com/subscriptions/{env_details.get('subscription_id')}/resourceGroups/{env_details.get('resource_group')}/providers/Microsoft.ApiManagement/service/{env_details.get('service_name')}/apis/{api_id}?import=true&api-version=2022-09-01-preview"
    patch_url = f"https://management.azure.com/subscriptions/{env_details.get('subscription_id')}/resourceGroups/{env_details.get('resource_group')}/providers/Microsoft.ApiManagement/service/{env_details.get('service_name')}/apis/{api_id}?api-version=2023-03-01-preview"

    # Detect the format dynamically
    try:
        swagger_format = detect_swagger_format(swagger_file)
    except ValueError as e:
        console.log(f"[red]{e} Exiting...[/red]")
        quit()

    return {
        "url":url,
        "patch_url":patch_url,
        "swagger_file":swagger_file,
        "api_details":api_details,
        "swagger_format": swagger_format,
        "environment": api_details.get('environment')
    }

def get_endpoint(env,api_suffix):
    """
    Returns endpoint for getting swagger file
    """
    normal_endpoints = {
        "UAT": f"http://20.31.196.178/{api_suffix}/v2/api-docs",
        "EUT": f"http://20.67.78.71/{api_suffix}/v2/api-docs",
        "PRE PROD": f"http://20.76.32.39/{api_suffix}/v2/api-docs",
        "US PROD": f"http://4.236.214.205/{api_suffix}/v2/api-docs",
        "US PROD 2": f"http://20.253.30.209/{api_suffix}/v2/api-docs",
        "EU PROD": f"http://52.236.148.125/{api_suffix}/v2/api-docs",
        "ACCORD EU PROD": f"http://172.211.182.240/{api_suffix}/v2/api-docs",
        "ACCORD UAT": f"http://9.163.203.4/{api_suffix}/v2/api-docs",
    }
        

    dcf_endpoints = {
        "UAT": f"http://20.31.196.178/dcf/api-docs",
        "EUT": f"http://20.67.78.71/dcf/api-docs",
        "PRE PROD": f"http://20.76.32.39/dcf/api-docs",
        "US PROD": f"http://4.236.214.205/dcf/api-docs",
        "US PROD 2": f"http://20.253.30.209/dcf/api-docs",
        "EU PROD": f"http://52.236.148.125/dcf/api-docs",
        "ACCORD EU PROD": f"http://172.211.182.240/dcf/api-docs",
        "ACCORD UAT": f"http://9.163.203.4/dcf/api-docs",
    }        

    if api_suffix == "dcf":
        return dcf_endpoints.get(env)
    
    return normal_endpoints.get(env)

def get_platform_access_token(env):
    """
    Returns X-AUTH-TOKEN from company platform login
    """
    login_urls = {
        "UAT": f"https://stringsuatapi.azure-api.net/gateway/open/login",
        "EUT": f"https://strings-it-apim-uat-west-eu.azure-api.net/gateway/open/login",
        "PRE PROD": f"https://strings-pre-prod-api.azure-api.net/gateway/open/login",
        "US PROD": f"https://strings-prod-us-region.azure-api.net/gateway/open/login",
        "US PROD 2": f"https://strings-us-prod2.azure-api.net/gateway/open/login",
        "EU PROD": f"https://stringsprodapi.azure-api.net/gateway/open/login",
        "ACCORD EU PROD": f"https://accord-euprod-api.azure-api.net/gateway/open/login",
        "ACCORD UAT": f"https://accord-uat-api.azure-api.net/gateway/open/login",
    }

    login_url = login_urls.get(env)

    body = {
        "username": "admin@73strings.com",
        "password": "92pWVu5C",
        "orgType": "vc"
    }

    headers = {
        "Content-Type": "application/json"
    }

    console.log("Getting platform access token...")
    response = requests.post(login_url,json=body,headers=headers)
    return response.headers.get('X-AUTH-TOKEN')

def get_swagger_file(env,api_suffix):
    """
    Fetches swagger file from endpoints, if swagger endpoint doesn't exists then read swagger from file
    """
    if env != "Automation Testing" and api_suffix != "":
        # first try making requests to endpoint
        endpoint = get_endpoint(env,api_suffix)
        platform_access_token = get_platform_access_token(env)

        if not platform_access_token:
                console.log("[red]Failed to get platform access token.[/red]")
                return None

        headers = {
            "X-AUTH-TOKEN": platform_access_token
        }

        console.log("Fetching swagger file...")
        response = requests.get(endpoint,headers=headers)

    if env != "Automation Testing" and api_suffix != "" and response.status_code == 200:
        swagger_file = response.json()
        if validate_swagger_file(swagger_file):
            # writing fetched swagger to a file for testing
            with open("fetched_swagger.txt", "w") as file:
                file.write(str(swagger_file))
            return swagger_file
        else:
            console.log("[red]Invalid Swagger file fetched. Exiting...[/red]")
            quit()
    else:
        # if we get 404 take swagger path as input to read file
        status_code = 404 if env == "Automation Testing" or api_suffix == "" else response.status_code
        console.log(f"[yellow]Failed to fetch Swagger file from endpoint. Status: {status_code}[/yellow]")
        console.log("Reading Swagger file from local path...")
        swagger_file = read_swagger_file()
        if validate_swagger_file(swagger_file):
            return swagger_file
        else:
            console.log("[red]Invalid Swagger file provided. Exiting...[/red]")
            quit()


def validate_swagger_file(swagger_content):
    """
    Validates the Swagger (OpenAPI) file content.
    """
    console.log("Validating Swagger file...")
    try:
        validate_spec(swagger_content)
        console.log("[green]Swagger file is valid![/green]")
        return True
    except OpenAPISpecValidatorError as e:
        console.log(f"[red]Swagger validation failed: {e}[/red]")
        return False
    except Exception as e:
        console.log(f"[red]Unexpected error during validation: {e}[/red]")
        return False

def get_api_details(info,access_token):
    """
    Returns API details\n
    {
        "api_id",\n
        "displayName",\n
        "serviceUrl",\n
        "path",\n
        "protocols",\n
        "subscriptionRequired"\n
    }
    """
    console.log("Select your API")
    all_apis_url = f"https://management.azure.com/subscriptions/{info.get('subscription_id')}/resourceGroups/{info.get('resource_group')}/providers/Microsoft.ApiManagement/service/{info.get('service_name')}/apis?api-version=2023-03-01-preview"

    headers = {
        "authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    # console.log(access_token)
    response = requests.get(all_apis_url,headers=headers)
    response = response.json()
    apis = response.get('value')
    count = response.get('count')
    for _index in range(len(apis)):
        console.log(f"  {_index+1}. {apis[_index].get('properties').get('displayName')}")
    
    api_number = int(input())
    selection = verify_selection()
    while True:
        if not selection:
            console.log(f"Enter the serial number of service")
            api_number = int(input())
            selection = verify_selection()
        elif(api_number>count or api_number <= 0):
            console.print(f"[red]Invalid API selected, Enter a valid serial number[/red]")
            api_number = int(input())
            selection = verify_selection()
        else:
            return {
                "api_id":apis[api_number-1].get('name'),
                "displayName":apis[api_number-1].get('properties').get('displayName'),
                "serviceUrl":apis[api_number-1].get('properties').get('serviceUrl'),
                "path":apis[api_number-1].get('properties').get('path'),
                "protocols":apis[api_number-1].get('properties').get('protocols'),
                "subscriptionRequired":apis[api_number-1].get('properties').get('subscriptionRequired'),
                "environment": info.get('environment')
            }


def check_azure_login():
    """
    Checks if the user is logged into Azure. If not, logs in.
    """
    console.log("Checking Azure login status...")

    try:
        result = os.popen("az account show").read().strip()
        if not result:
            raise ValueError("No output from 'az account show'.")
        
        account_info = json.loads(result)
        if "id" in account_info:
            console.log(f"[green]Logged into Azure as: {account_info['user']['name']}[/green]")
            return True

    except Exception:
        console.log("[yellow]User is not logged into Azure. Attempting to log in...[/yellow]")

    return azure_login()

def azure_login():
    """
    Logs into Azure CLI.
    """
    console.log("[blue]Opening browser for Azure login...[/blue]")
    
    try:
        os.system("az login")  # Runs Azure CLI login
        result = os.popen("az account show").read().strip()
        account_info = json.loads(result)

        if "id" in account_info:
            console.log(f"[green]Successfully logged into Azure as: {account_info['user']['name']}[/green]")
            return True
        else:
            raise ValueError("Login was unsuccessful.")

    except Exception:
        console.log("[red]Failed to log into Azure. Please run 'az login' manually and retry.[/red]")
        sys.exit(1)


# Function to get Azure access token using Azure CLI
def get_access_token():
    """
    Returns access token from azure
    """

    # Check if 'az' command exists
    if not shutil.which("az"):
        console.log("[red]Azure CLI is not installed. Please install it from:[/red] https://aka.ms/installazurecliwindows")
        sys.exit(1)  # Stop execution

    check_azure_login()

    console.log("Fetching Azure access token...")
    try:
        result = os.popen("az account get-access-token --query accessToken --output tsv").read().strip()
        if not result:
            raise ValueError("No access token returned. Ensure you're logged in to Azure.")
        console.log("[green]Access token fetched successfully![/green]")
        return result
    except Exception as e:
        console.log(f"[red]Error getting access token: {e}[/red]")
        sys.exit(1)
        # return None

# Function to read the Swagger (OpenAPI) file
def read_swagger_file():
    """
    Take path, read and return swagger file contents
    """
    console.log("Enter swagger file path")
    file_path = input()
    file_path = file_path.replace("\\","/")
    try:
        if file_path.index('"') == 0:
            file_path = file_path.split('"')[1]
    except ValueError:
        file_path = file_path
    console.log(f"Reading Swagger file from [blue]{file_path}[/blue]...")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            console.log("[green]Swagger file read successfully![/green]")
            return json.loads(file.read())
    except FileNotFoundError:
        console.log("[red]Swagger file not found![/red]")
        return None

def detect_swagger_format(swagger_content):
    """
    Detects the format of the Swagger/OpenAPI specification.
    Returns the format string to be used in the API update request.
    """
    if "swagger" in swagger_content:
        return "swagger-json"  # Swagger 2.0
    elif "openapi" in swagger_content:
        return "openapi+json"  # OpenAPI 3.x
    else:
        raise ValueError("Unsupported or unknown Swagger/OpenAPI format detected.")


# Main function to update Swagger in APIM
def update_swagger(info, access_token):   

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    api_details = info.get('api_details')

    body = {
        "name":api_details.get('api_id'),
        "properties": {
            "format": info.get('swagger_format'),
            "value": json.dumps(info.get('swagger_file'),ensure_ascii=False),
            "displayName": api_details.get('displayName'),
            "serviceUrl": api_details.get('serviceUrl'),
            "protocols": api_details.get('protocols'),
            "path": api_details.get('path'),
            "authenticationSettings": None,
            "subscriptionKeyParameterNames": None,
            "subscriptionRequired": api_details.get('subscriptionRequired')
        }
    }

    with Progress() as progress:
        task = progress.add_task(f"[cyan]Updating Swagger in {info.get('environment')} ...", total=100)

        response = requests.put(info.get('url'), headers=headers, json=body)
        progress.update(task, advance=100)

    if response.status_code >= 200 and response.status_code < 300:
        console.log("[green]Swagger file updated successfully![/green]")
    else:
        console.log(f"[red]Failed to update Swagger. Status code: {response.status_code}[/red]")
        console.log(f"Response: [red]{response.text}[/red]")
        quit()



# Run the script
if __name__ == "__main__":
    console.rule("[bold blue]Azure Swagger Updater[/bold blue]")

    access_token = get_access_token()

    if not access_token:
        console.log("[red]Failed to get access token.[/red]")

    info = get_info(access_token)


    update_swagger(info, access_token)
