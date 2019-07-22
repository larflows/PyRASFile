"""
Written beginning July 22, 2019 by Daniel Philippus for the LAR Environmental Flows project at Colorado School of Mines.

This component of the program parses a CSV file to produce the appropriate flow inputs for the profile writer.  As
of the present state of development, the user must still manually specify boundary conditions and the other inputs.
The flow data is expected to typically be the most complex, and therefore the part which would benefit the most from
automated input from a format which other programs can conveniently generate.

The CSV format is expected to be as follows:

river,reach,rs,profilenumber,flow

Where flow is a floating-point value in cubic feet per second, profilenumber is an integer,
and the remaining entries are strings.

The order of these can be varied (if specified in the relevant functions or if a header is included,
but the names must remain the same.
"""

from profileWriter import mkFlowHeader

def readCSVList(path):
    # Utility function - convert CSV into list
    with open(path, "r") as f:
        # stripping in case of Windows-style (cr-lf) newlines
        return [l.strip("\r").split(",") for l in f.read().split("\n")]

def parseCSV(csvList, header = True, columns = [], types = False, coltypes = {}, allowEmpty = False, emptyCols = []):
    """
    Given a CSV parsed into a list of lists, convert it into a list of dictionaries, either with the first line
    as headers or with a specified column order.

    If types is true, it will also parse the entries according to the parsing functions in coltypes; if not,
    it will leave them all as strings.  coltypes must be specified if types is True.  coltypes should be a dictionary
    of {column: parser}, e.g. {"profilenumber": int}.

    The empty-related parameters are ignored unless types is True.  If types are being used, then, if an entry is empty:
        * If allowEmpty is false, then the function will throw an error if the column name is not in emptyCols, or
            if it is, then the value will be set to None.
        * If allowEmpty is true, then the value will be set to None.
    This does not apply if the specified type is string.
    """
    if header:
        columns = csvList[0]
    cols = len(columns)
    result = []
    start = 1 if header else 0
    for row in csvList[start:]:
        count = len(row)
        if count != cols:
            raise ValueError("Error: number of columns is not consistent in row: %s" % row)
        out = {}
        for i in range(0, count):
            val = row[i]
            col = columns[i]
            if types:
                if val == "":
                    if coltypes[col] == str:
                        out[col] = val
                    elif allowEmpty == True or col in emptyCols:
                        out[col] = None
                    else:
                        raise ValueError("Error: empty entry not allowed in row: %s" % row)
                else:
                    out[col] = coltypes[col](val)
            else:
                out[col] = val
        result.append(out)
    return result

def parseCSVfile(path, toDict=True, header=True, columns=[], types=False, coltypes={}, allowEmpty=False, emptyCols=[]):
    # Parse from a file and read into a dictionary by default; if toDict = False, this just calls
    # readCSVList
    if toDict:
        return parseCSV(readCSVList(path), header, columns, types, coltypes, allowEmpty, emptyCols)
    else:
        return readCSVList(path)

def parseFlowCSV(path, header = True, columns = ["river", "reach", "rs", "profilenumber", "flow"]):
    coltypes = {
        "river": str,
        "reach": str,
        "rs": str,
        "profilenumber": int,
        "flow": float
    }
    return parseCSVfile(path, header = header, columns = columns, types = True, coltypes = coltypes)

def makeFlowData(csvDict):
    result = {}
    for entry in csvDict:
        key = mkFlowHeader(entry["river"], entry["reach"], entry["rs"])
        if not key in result.keys():
            # the final format will be a list of lists, but we need to keep the profile numbers for now
            # to make sure the order is correct
            result[key] = {entry["profilenumber"]:entry["flow"]}
        else:
            result[key][entry["profilenumber"]] = entry["flow"]
    for key in result.keys():
        # Make sure they're in the correct order
        entry = result[key]
        keys = entry.keys()
        keys.sort()
        result[key] = [entry[k] for k in keys]
    return result

def csvToFlowData(path, header = True, columns = ["river", "reach", "rs", "profilenumber", "flow"]):
    return makeFlowData(parseFlowCSV(path, header, columns))