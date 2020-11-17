from itertools import groupby

from quisby.sheet.sheet_util import (
    create_spreadsheet,
    append_to_sheet,
    read_sheet,
    get_sheet,
)
from quisby.util import combine_two_array_alternating
from quisby.benchmarks.fio.graph import graph_fio_data


def compare_fio_results(spreadsheets, test_name="fio"):
    spreadsheet_name = []
    values = []
    results = []

    for spreadsheetId in spreadsheets:
        values.append(read_sheet(spreadsheetId, range=test_name))
        spreadsheet_name.append(
            get_sheet(spreadsheetId, range=[])["properties"]["title"]
        )

    spreadsheet_name = " vs ".join(spreadsheet_name)

    for index, value in enumerate(values):
        values[index] = (list(g) for k, g in groupby(value, key=lambda x: x != []) if k)

    list_1 = list(values[0])
    list_2 = list(values[1])

    for value in list_1:
        results.append([""])
        for ele in list_2:
            if value[0] == ele[0]:
                results.append(value[0])
                results = combine_two_array_alternating(results, value[1:], ele[1:])

    spreadsheetId = create_spreadsheet(spreadsheet_name, test_name)
    append_to_sheet(spreadsheetId, results, test_name)
    graph_fio_data(spreadsheetId, test_name)

    print(f"https://docs.google.com/spreadsheets/d/{spreadsheetId}")

    return results
