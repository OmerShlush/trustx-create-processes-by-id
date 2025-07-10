import requests
import uuid
import csv
from urllib.parse import urlparse, parse_qs
import os
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
ids = list(map(int, os.getenv("IDS", "").split(",")))
pdName = os.getenv("PD_NAME")
pdVer = os.getenv("PD_VER")
countryCode = os.getenv("COUNTRY_CODE")



issue_url = f"{base_url}/api/arthr/apiKeys/issue"
headers = {
    "X-Api-Key": api_key,
    "Content-Type": "application/json"
}


response = requests.post(issue_url, headers=headers)
if response.status_code == 200:
    token_data = response.json()
    api_token = token_data.get("token")
    print(f"API token received: {api_token}")
else:
    print(f"Failed to issue API token: {response.status_code} {response.text}")
    exit()


csv_filename = "process_tokens.csv"
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Applicant ID", "Formatted Process URL"])

    process_token_url = f"{base_url}/api/process-manager/processTokens"
    for id_number in ids:
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        unique_name = str(uuid.uuid4())

        payload = {
            "name": unique_name,
            "description": "A process token",
            "status": "ACTIVE",
            "type": "UNLIMITED",
            "processDefnName": pdName,
            "processDefnVersion": pdVer,
            "uiUrl": f"{base_url}/web/trustweb",
            "parameters": {
                "countryCode": countryCode,
                "documentType": "ID_CARD",
                "ID": id_number 
            }
        }

        # Create process token
        response = requests.post(process_token_url, headers=headers, json=payload)
        if response.status_code == 201:
            process_data = response.json()
            start_process_url = process_data.get("startProcessAddress", "N/A")

            # Parse the 'pt' parameter from the original URL
            parsed_url = urlparse(start_process_url)
            pt_parameter = parse_qs(parsed_url.query).get('pt', [None])[0]

            if pt_parameter:
                # Reformat the URL as requested
                formatted_url = f"{base_url}/web/trustweb/?pt={pt_parameter}"
                print(f"Process token created for ID {id_number}: {formatted_url}")

                # Write to CSV
                writer.writerow([id_number, formatted_url])
            else:
                print(f"Failed to extract 'pt' parameter from {start_process_url}")
                writer.writerow([id_number, "Failed to format URL"])
        else:
            print(f"Failed to create process token for ID {id_number}: {response.status_code} {response.text}")

print(f"Process tokens saved to {csv_filename}")