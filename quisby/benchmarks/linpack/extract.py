import csv
import glob
import re
import os.path

from quisby.pricing.cloud_pricing import get_cloud_pricing, get_cloud_cpu_count
import quisby.config as config


def linpack_format_data(**kwargs):
    """
    Add data into format to be shown in spreadsheets
    Supports linpack like data. eg: autohpl
    """
    results = kwargs["results"] if kwargs["results"] else []
    system_name = kwargs["system_name"] if kwargs["system_name"] else None
    if kwargs["gflops"]:
        gflops = float(kwargs["gflops"])
    else:
        return None

    price_per_hour = get_cloud_pricing(
        system_name, config.region, config.cloud_type.lower()
    )

    no_of_cores = get_cloud_cpu_count(
        system_name, config.region, config.cloud_type.lower()
    )

    results.append(
        [
            "System",
            "Cores",
            f"GFLOPS-{config.OS_RELEASE}",
            f"GFLOP Scaling-{config.OS_RELEASE}",
            "Cost/hr",
            f"Price/Perf-{config.OS_RELEASE}",
        ]
    )
    results.append(
        [
            system_name,
            no_of_cores,
            gflops,
            1,
            price_per_hour,
            float(gflops) / float(price_per_hour),
        ]
    )

    return results


def extract_linpack_data(path, system_name):
    """
    Make shift function to handle linpack summary data
    till a resolution is reached
    """

    results = []
    no_of_cores = None
    gflops = None

    summary_file = path

    if not os.path.isfile(summary_file):
        return None

    with open(summary_file) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=":")
        last_row = list(csv_reader)[-2]
        gflops = last_row["MB/sec"]
        threads = last_row["threads"]

    for file_path in glob.glob(path + f"/linpack*_threads_{threads}_*"):
        with open(file_path) as txt_file:
            data = txt_file.readlines()
            for row in data:
                if re.findall(r"Number of cores: (\d+)", row):
                    no_of_cores = re.findall(r"Number of cores: (\d+)", row)[0]
                    break

    if gflops:
        results = linpack_format_data(
            results=results,
            system_name=system_name,
            no_of_cores=no_of_cores,
            gflops=gflops,
        )

        return results