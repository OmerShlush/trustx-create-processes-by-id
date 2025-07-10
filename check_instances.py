from datetime import datetime
from dotenv import load_dotenv

import os
import requests
import pandas as pd

load_dotenv()

base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")

def get_bearer_token(api_key, base_url):
    issue_url = f"{base_url}/api/arthr/apiKeys/issue"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.post(issue_url, headers=headers)
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("token")
    else:
        print(f"Failed to issue API token: {response.status_code} {response.text}")
        exit()

def get_instances(base_url, bearer_token):
    endpoint = "/api/process-manager/processInstances"
    url = f"{base_url}{endpoint}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    query_params = {
        "page": 0,
        "size": 100
    }

    instances = []
    while True:
        response = requests.get(url, headers=headers, params=query_params)
        if response.status_code == 200:
            data = response.json()
            instances.extend(data.get("content", []))
            if data.get("last", True):
                break
            query_params["page"] += 1
        else:
            print(f"Error fetching instances: {response.status_code} {response.text}")
            break

    completed_success_instances = [
        instance for instance in instances if instance.get("status") == "COMPLETED_ENDED_SUCCESS"
    ]
    return completed_success_instances

def get_instance_details(base_url, bearer_token, instance_id):
    endpoint = f"/api/process-manager/processInstances/{instance_id}/withParameters"
    url = f"{base_url}{endpoint}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching details for instance {instance_id}: {response.status_code} {response.text}")
        return None

def get_user_data(base_url, bearer_token, process_def_id, process_instance_id):
    endpoint = f"/api/userdata-server/processDefinitions/{process_def_id}/processInstances/{process_instance_id}/userdata"
    url = f"{base_url}{endpoint}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching user data for instance {process_instance_id}: {response.status_code} {response.text}")
        return None

def extract_document_number(user_data):
    try:
        biographic_data = user_data.get("documents", {}).get("doc1", {}).get("biographicData", [])
        for entry in biographic_data:
            if entry.get("fieldName") == "Document Number":
                return entry.get("values", {}).get("visualZoneValue")
    except Exception as e:
        print(f"Error extracting document number: {e}")
    return None

def main():

    bearer_token = get_bearer_token(api_key, base_url)
    completed_success_instances = get_instances(base_url, bearer_token)

    matching_ids = []
    non_matching_ids = []

    for instance in completed_success_instances:
        instance_details = get_instance_details(base_url, bearer_token, instance.get("id"))
        valid_id = instance_details.get("processTokenParameters", {}).get("ID")
        instance_id = instance.get("id")
        process_def_id = instance.get("processDefnId")

        user_data = get_user_data(base_url, bearer_token, process_def_id, instance_id)

        if user_data:
            document_number = extract_document_number(user_data)

            if str(valid_id) == str(document_number) and document_number is not None:
                matching_ids.append({
                    "Instance ID": instance_id,
                    "Document Number": document_number,
                    "Valid ID": valid_id
                })
            else:
                non_matching_ids.append({
                    "Instance ID": instance_id,
                    "Document Number": document_number,
                    "Valid ID": valid_id
                })

    matching_df = pd.DataFrame(matching_ids)
    non_matching_df = pd.DataFrame(non_matching_ids)

    today_str = datetime.today().strftime("%d-%m-%Y")
    filename = f"process_instances_insights_{today_str}.xlsx"

    with pd.ExcelWriter(filename) as writer:
        matching_df.to_excel(writer, sheet_name="Matching IDs", index=False)
        non_matching_df.to_excel(writer, sheet_name="No1n-Matching IDs", index=False)

    print(f"Spreadsheet created: {filename}")

if __name__ == "__main__":
    main()
