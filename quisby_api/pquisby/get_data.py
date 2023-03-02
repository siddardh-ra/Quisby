import configparser
import json
import os.path
import requests
from benchmarks.uperf.uperf import extract_uperf_data
from process_result import process_results

payload = ""
headers = {'Authorization': '' }
pbench_server_url = "http://intlab-002.ctrl.perf-infra.lab.eng.rdu2.redhat.com:8080"

def get_benchmark_details(resourceid, test_name):
    url = f"{pbench_server_url}/api/v1/datasets/inventory/{resourceid}/metadata.log"
    print(url)
    response = requests.get(url, headers=headers, data=payload,stream=True)
    decoded_response = response.content.decode("UTF-8")
    parser = configparser.ConfigParser(allow_no_value=True)
    parser.read_string(decoded_response)
    benchmark_name = parser.get("pbench", "script")
    controller_name = parser.get("run", "controller")
    return benchmark_name, controller_name


def register_details_json(test_name, spreadsheet_id):
    filename = "/Users/soumyasinha/.config/pquisby/charts.json"
    if not os.path.exists(filename):
        data = {"chartlist": {test_name: spreadsheet_id}}
        with open(filename, "w") as f:
            json.dump(data, f)
    else:
        with open(filename, "r") as f:
            data = json.load(f)
        data["chartlist"][test_name] = spreadsheet_id
        with open(filename, "w") as f:
            json.dump(data, f)


def check_if_chart_exists(test_name):
    filename = "/Users/soumyasinha/.config/pquisby/charts.json"
    if not os.path.exists(filename):
        return ""
    else:
        with open(filename, "r") as f:
            data = json.load(f)
        try:
            id = data["chartlist"][test_name]
        except ValueError:
            return ""
        return id


def fetch_test_data(resourceid, run_name):
    results = []
    benchmark_name, controller_name = get_benchmark_details(resourceid, run_name)
    spreadsheet_name = run_name
    url = f"{pbench_server_url}/api/v1/datasets/inventory/{resourceid}/result.csv"
    response = requests.get(url, headers=headers, data=payload,stream=True)
    decoded_data = response.content.decode("UTF-8")
    split_rows = decoded_data.split("\n")
    csv_data = []
    for row in split_rows:
        csv_data.append(row.split(","))
    if benchmark_name == "uperf":
        test_name = "uperf"
        ret_val = extract_uperf_data(controller_name, csv_data)
        if ret_val:
            results += ret_val
    spreadsheet_id = check_if_chart_exists(test_name)
    if spreadsheet_id == "":
        spreadsheet_id = process_results(results, test_name, spreadsheet_name, spreadsheet_id)
        register_details_json(test_name, spreadsheet_id)
    else:
        spreadsheet_id = process_results(results, test_name, spreadsheet_name, spreadsheet_id)
    return spreadsheet_id


fetch_test_data("e8b03087a03c5986b47b58f6ad84a907","uperf__2023.03.01T05.17.05")