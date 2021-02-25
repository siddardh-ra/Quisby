from quisby.sheet.sheetapi import sheet


def check_sheet_exists(sheet_info, test_name):
    """"""

    for sheet_prop in sheet_info:
        if test_name == sheet_prop["properties"]["title"]:
            return True

    return False


def create_spreadsheet(spreadsheet_name, test_name):
    """
    A new sheet is created if spreadsheetId is None

    :sheet: Google sheet API function
    :name: Spreadsheet title
    """
    spreadsheet = {
        "properties": {"title": spreadsheet_name},
        "sheets": {
            "properties": {
                "sheetId": 0,
                "title": test_name,
                "gridProperties": {
                    "frozenRowCount": 1,
                },
            }
        },
    }

    spreadsheet = sheet.create(body=spreadsheet, fields="spreadsheetId").execute()
    spreadsheetId = spreadsheet["spreadsheetId"]

    return spreadsheetId


def get_sheet(spreadsheetId, range="A:F"):

    return sheet.get(spreadsheetId=spreadsheetId, ranges=range).execute()


def create_sheet(spreadsheetId, test_name):
    """
    New sheet in spreadsheet is created

    :sheet: Google sheet API function
    :spreadsheetId
    :test_name: range to graph up the data, it will be mostly sheet name
    """
    sheet_info = get_sheet(spreadsheetId, [])["sheets"]

    # Create sheet if it doesn't exit
    if not check_sheet_exists(sheet_info, test_name):
        sheet_count = len(sheet_info)

        requests = {
            "addSheet": {
                "properties": {
                    "sheetId": sheet_count + 1,
                    "title": test_name,
                    "gridProperties": {
                        "frozenRowCount": 1,
                    },
                }
            }
        }

        body = {"requests": requests}

        sheet.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()


def read_sheet(spreadsheet_Id, range="A:F"):
    """"""
    result = sheet.values().get(spreadsheetId=spreadsheet_Id, range=range).execute()
    values = result.get("values", [])

    return values


def append_to_sheet(spreadsheet_Id, results, range="A:F"):
    """"""

    body = {"values": results}

    response = (
        sheet.values()
        .append(
            spreadsheetId=spreadsheet_Id,
            range=range,
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )
    return response


def apply_named_range(spreadsheetId, name, range="A:F"):

    sheetId = get_sheet(spreadsheetId, range)["sheets"][0]["properties"]["sheetId"]

    sheet_range = range.split("!")[1].split(":")

    body = {
        "requests": [
            {
                "addNamedRange": {
                    "namedRange": {
                        "namedRangeId": range,
                        "name": name + "_NR",
                        "range": {
                            "sheetId": sheetId,
                            "startRowIndex": int(sheet_range[0][1:]) - 1,
                            "endRowIndex": sheet_range[1][1:],
                            "startColumnIndex": ord(sheet_range[0][:1]) % 65,
                            "endColumnIndex": ord(sheet_range[1][:1]) % 65 + 1,
                        },
                    }
                },
            }
        ]
    }

    response = (
        service.spreadsheets()
        .batchUpdate(spreadsheetId=spreadsheetId, body=body)
        .execute()
    )

    print(response)


def clear_sheet_data(spreadsheetId, range="A2:Z1000"):
    # Clear values
    sheet.values().clear(spreadsheetId=spreadsheetId, range=range, body={}).execute()


def clear_sheet_charts(spreadsheetId, range="A2:Z1000"):
    # Clear charts
    sheet_properties = get_sheet(spreadsheetId, range)

    if "charts" in sheet_properties["sheets"][0]:
        for chart in sheet_properties["sheets"][0]["charts"]:

            requests = {"deleteEmbeddedObject": {"objectId": chart["chartId"]}}

            body = {"requests": requests}

            sheet.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()


def get_named_range(spreadsheetId, range="A:F"):
    spreadsheet = get_sheet(spreadsheetId, range)

    return spreadsheet['namedRanges']

def append_empty_row_sheet(spreadsheetId, rows, range="A:F"):
    
    sheetId = get_sheet(spreadsheetId, range)["sheets"][0]["properties"]["sheetId"]


    body = {
        "requests": [
            {
                "appendDimension":{
                    "sheetId": sheetId,
                    "dimension": "ROWS",
                    "length": rows
                }
            }
        ]
    }

    sheet.batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()