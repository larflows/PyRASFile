"""
Written beginning July 17, 2019 by Daniel Philippus for the LAR Environmental Flows project at Colorado School of Mines.

This component of the program reads HEC-RAS Report (.rep) files to extract relevant information and can, optionally,
write the data to a CSV file (e.g. for use in R scripts).

It is designed to look specifically for cross sections by river and reach, but within cross-section data is designed
to be extensible in terms of which data it looks for.  While the data is simply specified in a variable as only specific
data is necessary as of the program's writing, this should be easy to modify if necessary.
"""

"""
HEC-RAS Report Format for relevant entries (example taken from a .rep file):
This is repeated for each cross-section.

CROSS SECTION          


RIVER: Compton Creek   
REACH: CC                 RS: 52494.08


CROSS SECTION OUTPUT  Profile #PF 1  
                                                                                               
  E.G. Elev (ft)            114.48    Element                   Left OB    Channel   Right OB  
  Vel Head (ft)               0.35    Wt. n-Val.                            0.011              
  W.S. Elev (ft)            114.13    Reach Len. (ft)            29.51      29.51      29.51   
  Crit W.S. (ft)            114.13    Flow Area (sq ft)                     20.99              
  E.G. Slope (ft/ft)      0.002285    Area (sq ft)                          20.99              
  Q Total (cfs)             100.00    Flow (cfs)                           100.00              
  Top Width (ft)             30.00    Top Width (ft)                        30.00              
  Vel Total (ft/s)            4.76    Avg. Vel. (ft/s)                       4.76              
  Max Chl Dpth (ft)           0.70    Hydr. Depth (ft)                       0.70              
  Conv. Total (cfs)         2092.2    Conv. (cfs)                          2092.2              
  Length Wtd. (ft)           29.51    Wetted Per. (ft)                      31.40              
  Min Ch El (ft)            113.43    Shear (lb/sq ft)                       0.10              
  Alpha                       1.00    Stream Power (lb/ft s)                 0.45              
  Frctn Loss (ft)             0.07    Cum Volume (acre-ft)                  44.31              
  C & E Loss (ft)             0.00    Cum SA (acres)                        58.14              
                                                                                               

Warning: The energy equation could not be balanced within the specified number of iterations.  The program used critical 
         depth for the water surface and continued on with the calculations.
Warning: During the standard step iterations, when the assumed water surface was set equal to critical depth, the calculated 
         water surface came back below critical depth.  This indicates that there is not a valid subcritical answer.  The 
         program defaulted to critical depth.

CROSS SECTION OUTPUT  Profile #PF 2  
                                                                                               
<... same items as PF 1>
CROSS SECTION OUTPUT  Profile #PF 3  
                                                                                               
<... same items as PF 1>
Warning: The cross-section end points had to be extended vertically for the computed water surface.
"""

# Entries to look for
ENTRIES = ["Q Total (cfs)", "Avg. Vel. (ft/s)", "Max Chl Dpth (ft)"]

# File path for current development
PATH = "V:\\LosAngelesProjectsData\\HEC-RAS\\Full MODEL\\FullModel.rep"
OUTPATH = "Z:\\adit\\Desktop\\LARFlows\\ReportOutput.csv"


def riverNode(river, reach, rs, swmm = ""):
    # This just makes a dict; defining a function purely for convenience
    # swmm = corresponding SWMM node; this is specific to the LARFlows project and can be ignored by other users
    return {"river": river, "reach": reach, "rs": rs, "swmm": swmm}


# Nodes to look for
NODES = [
    riverNode("Upper LA River", "Above RH", "70185*", "F34D"),
    riverNode("Rio Hondo Chnl", "RHC", "7000", "F45B"),
    riverNode("Upper LA River", "Above RH", "157606.4", "GLEN"),
    riverNode("LA River", "Below CC", "21500", "F319"),
    riverNode("Compton Creek", "CC", "22616", "F37B"),
    riverNode("Upper LA River", "Above RH", "195289.1", "F300"),
    riverNode("Upper LA River", "Above RH", "168989.7", "LA14"),
    riverNode("Upper LA River", "Above RH", "199036.7", "LA17"),
    riverNode("LA River", "Below CC", "15700", "LA2"),
    riverNode("Rio Hondo Chnl", "RHC", "15600", "RHD2"),
    riverNode("Upper LA River", "Above RH", "213974.*", "LA19"),
    riverNode("Upper LA River", "Above RH", "207769", "LA18"),
    riverNode("Upper LA River", "Above RH", "186920.5", "LA16"),
    riverNode("Upper LA River", "Above RH", "177244", "LA15"),
    riverNode("Upper LA River", "Above RH", "161809", "LA13"),
    riverNode("Upper LA River", "Above RH", "150089.6", "LA12"),
    riverNode("Upper LA River", "Above RH", "143272.1", "LA11"),
    riverNode("Upper LA River", "Above RH", "137061.4", "LA10"),
    riverNode("Upper LA River", "Above RH", "115507", "LA8"),
    riverNode("Upper LA River", "Above RH", "107352", "LA7"),
    riverNode("Upper LA River", "Above RH", "88311", "LA5"),
    riverNode("Upper LA River", "RH to CC", "52928", "LA4"),
    riverNode("Upper LA River", "RH to CC", "38700", "LA3"),
    riverNode("Upper LA River", "Above RH", "96076", "LA6"),
    riverNode("LA River", "Below CC", "1600", "LA1"),
    riverNode("Compton Creek", "CC", "33669.4*", "CP2"),
    riverNode("Compton Creek", "CC", "44173.9*", "CP3"),
    riverNode("Upper LA River", "Above RH", "127537.6", "LA9"),
    riverNode("Compton Creek", "CC", "52494.08", "CP4"),
    riverNode("Rio Hondo Chnl", "RHC", "30500", "RHD3"),
    riverNode("Upper LA River", "Above RH", "225805", "11092450"),
    riverNode("Rio Hondo Chnl", "RHC", "44113", "11102300")
]

def getDataForNodes(xsData, nodes):
    # Extract the relevant data from the parsed-out data
    keys = [" ".join([node["river"], node["reach"], node["rs"]]) for node in nodes]
    availKeys = [key for key in keys if key in xsData.keys()]
    entries = [xsData[key] for key in availKeys]
    for key in [key for key in keys if not key in availKeys]:
        print("Warning: node %s not found in report data--skipping." % key)
    return entries

def makeNodePfDataString(nodeData, pf, riverNode, entries = ENTRIES):
    # Make a CSV line of the relevant data from the node, for the given profile number
    # In order to not be selective, just set entries to be all of the keys for an arbitrary cross-section;
    # specifying entries is necessary, however, to ensure a consistent order
    outData = [riverNode["river"], riverNode["reach"], riverNode["rs"], pf]
    for entry in entries:
        if entry in nodeData.keys():
            outData.append(nodeData[entry])
        else:
            outData.append("")
    return ",".join(outData)

def buildCSV(xsData, nodes, selective = False, entries = ENTRIES):
    # Build the CSV file for the relevant nodes and, if selective, relevant entries
    # If not selective, entries will simply be the entries of the first node
    entriesSet = selective
    data = getDataForNodes(xsData, nodes)
    output = []
    for datum in data:
        pfs = [k for k in datum.keys() if not k in ["river", "reach", "rs"]] # PF numbers only
        for pf in pfs:
            nodeData = datum[pf]
            if not entriesSet:
                entries = nodeData.keys() # To keep a specific order
                entriesSet = True
            output.append(makeNodePfDataString(nodeData, pf, datum, entries))
    output = ["River,Reach,RS,Profile," + ",".join(entries)] + output
    return "\n".join(output)

def convertCSV(nodes, selective = False, entries = ENTRIES, inpath = PATH, outpath = OUTPATH):
    with open(outpath, "w") as f:
        f.write(buildCSV(parseFile(getReportFile(inpath)), nodes, selective, entries))

def getReportFile(filename):
    with open(filename, "r") as f:
        return f.read()

def crossSections(text):
    # Split file content into separate cross sections
    # CROSS SECTION on its own shows up a lot, but it's only followed by two blank spaces when it's a new XS
    return text.split("CROSS SECTION  ")

def nodeData(xs):
    # Get the node information (river, reach, rs) for a given cross-section
    # Information is on the first two lines after CROSS SECTION
    lines = [ln for ln in xs.split("\n") if ln.strip() != ""][0:2]
    river = " ".join([i for i in lines[0].split(" ") if i != ""][1:])   # The first thing is RIVER:;
                                                                        # the rest is the river name
    ln2dat = [i for i in lines[1].split(" ") if i != ""]
    ln2splitIndex = ln2dat.index("RS:") # Where the reach stops and the RS begins
    reach = " ".join(ln2dat[1:ln2splitIndex]) # Everything before RS: except for REACH:, which starts the line
    rs = ln2dat[ln2splitIndex + 1] # No spaces in RS, it's a number
    return {"river": river, "reach": reach, "rs": rs}

def profiles(xs):
    # Split a cross section into profiles
    return xs.split("Profile #PF")

def entries(profile):
    # Data starts on row 3 and continues through row 17
    data = profile.split("\n")[2:17]
    output = {}
    for row in data:
        items = [i.strip() for i in row.split("  ") if i != ""] # Separate items are always separated by multiple spaces
        # There are two rows that have three entries for the right-hand items, but we don't need either, so
        # we can ignore that.
        # Otherwise, they are all two key-value pairs.
        if len(items) >= 4: # Sometimes something seems to be missing from the row
            output[items[0]] = items[1]
            output[items[2]] = items[3]
    return output

def parseXs(xs):
    # Parse the cross-section, returning node data, profile number, and entries
    data = nodeData(xs)
    profs = profiles(xs)[1:]
    for prof in profs:
        pnum = prof.split("\n")[0].strip() # First line has the profile number
        data[pnum] = entries(prof)
    return data

def parseFile(text):
    # Extract cross-section data from file
    xses = crossSections(text)
    xses = [xs for xs in xses if "CROSS SECTION OUTPUT" in xs] # Filter out non-cross-section entries at beginning
    data = {}
    for xs in xses:
        xsData = parseXs(xs)
        data[" ".join([xsData["river"], xsData["reach"], xsData["rs"]])] = xsData
    return data

if __name__ == "__main__":
    convertCSV(NODES, selective = True)