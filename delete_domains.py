import boto3
from botocore.config import Config
from typing import Any, Dict, List

DOMAINS_NOT_DELETE = ['hkr-test-workshop023']
REGION = 'eu-west-3'

my_config = Config(
    region_name = REGION
)

client = boto3.client('sagemaker', config=my_config)

# Retrive the Domain Ids

response = client.list_domains(MaxResults=100)

def get_domain_ids(response: Dict[str, Any]) -> List[str]:
    """Function to retrieve the domain id from the list_domains() command.
    """
    domain_ids: List[str] = []
    for domain in response['Domains']:
        # Do not collect one domain that we want to exclude
        if domain['DomainName'] not in DOMAINS_NOT_DELETE:
            domain_ids.append(domain['DomainId'])

    return domain_ids

domain_ids = get_domain_ids(response=response)

# List User Profiles
def get_user_profiles(domain_ids: List[str]) -> Dict[str, str]:
    """Function to retrieve the user profiles for each domain
    """
    user_profile_names: Dict[str, str] = {}
    for domain_id in domain_ids:
        response = client.list_user_profiles(
            MaxResults=100,
            DomainIdEquals=domain_id,
        )
        user_profiles = response['UserProfiles']
        assert len(user_profiles) <= 1 
        if len(user_profiles) == 1:
            user_profile_name = user_profiles[0]['UserProfileName']
            user_profile_names[domain_id] = user_profile_name
    
    return user_profile_names

user_names = get_user_profiles(domain_ids=domain_ids)
# Get user apps

def delete_user_apps(domain_ids: List[str], user_profile_names: Dict[str, str]) -> None:
    """Function to delete all user apps"""
    for domain in domain_ids:
        user_profile_name = user_profile_names.get(domain)
        if user_profile_name:
            response = client.list_apps(
                MaxResults=100,
                DomainIdEquals=domain,
                UserProfileNameEquals=user_profile_name,
            )
            apps = response['Apps']
            for app in apps:
                app_name = app['AppName']
                app_type = app['AppType']
                if app['Status'] == 'InService':
                    print(f"Deleting app {app_name} in {domain} for user {user_profile_name}")
                    response = client.delete_app(
                        DomainId=domain,
                        UserProfileName=user_profile_name,
                        AppName=app_name,
                        AppType=app_type
                    )

    return None

delete_user_apps(domain_ids=domain_ids, user_profile_names=user_names)
# Delete each user profile

def delete_user_profile(domain_ids: List[str], user_profile_names: Dict[str, str]) -> None:
    """Function to delete the user profiles"""
    for domain_id in domain_ids:
        user_profile_name = user_profile_names.get(domain_id)
        if user_profile_name:
            print(f"Deleting user profile {user_profile_name} in {domain_id}")
            response = client.delete_user_profile(
                DomainId=domain_id,
                UserProfileName=user_profile_name
            )
    
    return None

delete_user_profile(domain_ids=domain_ids, user_profile_names=user_names)


def list_spaces(domain_ids: List[str]) -> Dict[str, List[str]]:
    """Function to list the spaces. DELETES THE SPACE!"""
    spaces: Dict[str, List[str]] = {}
    for domain in domain_ids:
        response = client.list_spaces(
            MaxResults=100,
            DomainIdEquals=domain,
        )
        if response.get('Space'):
            for space in response['Space']:
                if space['Status'] == 'InService':
                    space_name = space['SpaceName']
                    known_spaces = spaces.get(domain)
                    if known_spaces:
                        spaces[domain] = known_spaces + [space_name]
                    else:
                        spaces[domain] = [space_name]
                    response = client.delete_space(
                        DomainId=domain,
                        SpaceName=space_name
                    )
    
    return spaces

spaces = list_spaces(domain_ids=domain_ids)


def delete_domain(domain_ids: List[str]) -> None:
    """Function to delete domains"""
    for domain in domain_ids:
        print(f"Deleting domain {domain}.")
        client.delete_domain(
            DomainId=domain,
            RetentionPolicy={
                'HomeEfsFileSystem': 'Delete'
            }
        )

delete_domain(domain_ids=domain_ids)
