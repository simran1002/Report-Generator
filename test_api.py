import json
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def login(username="user", password="user"):
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def get_headers(token):
    """Get headers with authorization"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def list_files(token, file_type=None):
    """List files"""
    url = f"{BASE_URL}/files/list"
    if file_type:
        url += f"/{file_type}"
    
    response = requests.get(url, headers=get_headers(token))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to list files: {response.text}")
        return None

def generate_report(token, input_file, reference_file):
    """Generate a report"""
    payload = {
        "input_file": input_file,
        "reference_file": reference_file,
        "output_format": "csv",
        "rule_set_id": None
    }
    
    response = requests.post(
        f"{BASE_URL}/reports/generate",
        headers=get_headers(token),
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to generate report: {response.text}")
        return None

def get_report(token, report_id):
    """Get report metadata"""
    response = requests.get(
        f"{BASE_URL}/reports/{report_id}",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get report: {response.text}")
        return None

def download_report(token, report_id, output_path):
    """Download a report"""
    response = requests.get(
        f"{BASE_URL}/reports/{report_id}/download",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Report downloaded to {output_path}")
        return True
    else:
        print(f"Failed to download report: {response.text}")
        return False

def get_rules(token):
    """Get transformation rules"""
    response = requests.get(
        f"{BASE_URL}/rules",
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get rules: {response.text}")
        return None

def main():
    print("Logging in...")
    token = login()
    if not token:
        return
    
    print("\nListing input files:")
    input_files = list_files(token, "input")
    if not input_files:
        print("No input files found")
        return
    
    print("\nListing reference files:")
    reference_files = list_files(token, "reference")
    if not reference_files:
        print("No reference files found")
        return
    
    input_file = input_files[0]["filename"]
    reference_file = reference_files[0]["filename"]
    
    print(f"\nUsing input file: {input_file}")
    print(f"Using reference file: {reference_file}")
    
    print("\nGetting transformation rules:")
    rules = get_rules(token)
    if rules:
        print(f"Rule set version: {rules['version']}")
        print("Rules:")
        for rule in rules["rules"]:
            print(f"  - {rule['output_field']} = {rule['expression']}")
    
    print("\nGenerating report...")
    report = generate_report(token, input_file, reference_file)
    if not report:
        return
    
    report_id = report["id"]
    print(f"Report generated with ID: {report_id}")
    print(f"Status: {report['status']}")
    
    if report["status"] == "processing":
        print("Waiting for report to complete...")
        max_attempts = 10
        attempts = 0
        
        while attempts < max_attempts:
            time.sleep(1)
            report = get_report(token, report_id)
            if report["status"] == "completed":
                print("Report completed!")
                break
            elif report["status"] == "failed":
                print(f"Report failed: {report.get('error_message', 'Unknown error')}")
                return
            
            attempts += 1
            print(f"Still processing... (attempt {attempts}/{max_attempts})")
    
    print("\nDownloading report...")
    output_path = f"./reports/downloaded_report_{report_id}.csv"
    download_report(token, report_id, output_path)

if __name__ == "__main__":
    main()
