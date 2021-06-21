from itertools import groupby

import quisby.config as config
from quisby.sheet.sheet_util import (
    create_spreadsheet,
    append_to_sheet,
    read_sheet,
    get_sheet,
    create_sheet
)
from quisby.util import combine_two_array_alternating
from quisby.benchmarks.hammerdb.graph import graph_hammerdb_data


def compare_hammerdb_results(spreadsheets, spreadsheetId, test_name):
    spreadsheet_name = []
    values = []
    results = []

    for spreadsheet in spreadsheets:
        values.append(read_sheet(spreadsheet, range=test_name))
        spreadsheet_name.append(
            get_sheet(spreadsheet, range=[])["properties"]["title"]
        )

    for index, value in enumerate(values):
        values[index] = (list(g) for k, g in groupby(value, key=lambda x: x != []) if k)

    list_1 = list(values[0])
    list_2 = list(values[1])

    for value in list_1:
        results.append([""])
        for ele in list_2:

            if value[0][1].split(".")[0] == ele[0][1].split(".")[0]:
                results = combine_two_array_alternating(results, value, ele)

    create_sheet(spreadsheetId, test_name)
    append_to_sheet(spreadsheetId, results, test_name)
    graph_hammerdb_data(spreadsheetId, test_name)
