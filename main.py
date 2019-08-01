from profileWriter import *
from reportReader import *
from utils import *

# Entries to look for
ENTRIES = ["Q Total (cfs)", "Avg. Vel. (ft/s)", "Max Chl Dpth (ft)"]

# File path for current development
PATH = "V:\\LosAngelesProjectsData\\HEC-RAS\\Full MODEL\\FullModel.rep"
OUTPATH = "Z:\\adit\\Desktop\\LARFlows\\Data Processing\\Calibration\\HecRasOutput.csv"


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

flowNodes = [
    riverNode("Compton Creek", "CC", "52494.08"),
    riverNode("LA River", "Below CC", "29266"),
    riverNode("Rio Hondo Chnl", "RHC", "44113"),
    riverNode("Upper LA River", "Above RH", "225805.0"),
    riverNode("Upper LA River", "RH to CC", "63900.3*")
]


flowRanges = [1, 10, 100, 1000, 10000]
upstreamFlows = [[], [], []]
for i in flowRanges:
    for j in flowRanges:
        for k in flowRanges:
            upstreamFlows[0].append(i)
            upstreamFlows[1].append(j)
            upstreamFlows[2].append(k)

downstreamFlows = [
    [upstreamFlows[0][i] + upstreamFlows[1][i] for i in range(0, 125)],
    [upstreamFlows[0][i] + upstreamFlows[1][i] + upstreamFlows[2][i] for i in range(0, 125)]
]

"""
The flow range at the bottom appears to be about up to 70,000 cfs; let's say up to
50,000 cfs in each of the upstream reaches.  If I run 100 profiles on a log scale,
this makes powers of about 1.12.
"""

upstreamFlowRange = [1.12 ** i for i in range(0, 100)]

flowdata = {}
for node in flowNodes:
    river = node["river"]
    reach = node["reach"]
    rs = node["rs"]
    key = mkFlowHeader(river, reach, rs)
    # Upstream and downstream flows
    flows = {
        "Above RH": upstreamFlowRange,
        "RHC": upstreamFlowRange,
        "CC": upstreamFlowRange,
        "RH to CC": [2 * i for i in upstreamFlowRange],
        "Below CC": [3 * i for i in upstreamFlowRange]
    }[reach]
    flowdata[key] = flows

"""flowdata = {
    "River Rch & RM=Compton Creek,CC              ,52494.08": upstreamFlows[0],
    "River Rch & RM=LA River,Below CC        ,29266": downstreamFlows[1],
    "River Rch & RM=Rio Hondo Chnl,RHC             ,44113": upstreamFlows[1],
    "River Rch & RM=Upper LA River,Above RH        ,225805.0": upstreamFlows[2],
    "River Rch & RM=Upper LA River,RH to CC        ,63900.3*": downstreamFlows[0]
}"""

def mkRegBound(pn, flow):
    return mkBoundaryData("Junction", "Junction", "", "")

def mkBottomBound(pn, flow):
    return mkBoundaryData("Junction", "Known WS", "", "1.4")
    # F319 seems to always be around 1.3-1.5 ft deep
    # F319 = LAR 21500, just a few miles above the estuary, so probably a reasonable basis

bounds = {
    "Compton Creek,CC": mkRegBound,
    "LA River,Below CC": mkBottomBound,
    "Rio Hondo Chnl,RHC": mkRegBound,
    "Upper LA River,Above RH": mkRegBound,
    "Upper LA River,RH to CC": mkRegBound
}

text = buildFile(100, flowdata, bounds, title="GenFlow Preliminary 1-100")

if __name__ == "__main__":
    generate = False
    parse = True
    makeCSV = False
    if generate:
        with open("V:\\LosAngelesProjectsData\\HEC-RAS\\Full Model\\FullModel.f05", "w") as f:
            f.write(text)
    if parse:
        convertCSV(NODES, entries = ENTRIES, inpath = PATH, outpath = OUTPATH, selective = True, swmm = True)
    if makeCSV:
        flows = [1, 10, 100, 1000, 10000]
        nodes = [
            {"river": "Compton Creek", "reach": "CC", "rs": "52494.08"},
            {"river": "LA River", "reach": "Below CC", "rs": "29266"},
            {"river": "Rio Hondo Chnl", "reach": "RHC", "rs": "44113"},
            {"river": "Upper LA River", "reach": "Above RH", "rs": "225805.0"},
            {"river": "Upper LA River", "reach": "RH to CC", "rs": "63900.3*"}
        ]
        upstreamNodes = {
            mkFlowHeader(nodes[1]["river"], nodes[1]["reach"], nodes[1]["rs"]):
                [mkFlowHeader(nodes[0]["river"], nodes[0]["reach"], nodes[0]["rs"]),
                                     mkFlowHeader(nodes[2]["river"], nodes[2]["reach"], nodes[2]["rs"]),
                                     mkFlowHeader(nodes[3]["river"], nodes[3]["reach"], nodes[3]["rs"])],
            mkFlowHeader(nodes[4]["river"], nodes[4]["reach"], nodes[4]["rs"]):
                [mkFlowHeader(nodes[2]["river"], nodes[2]["reach"], nodes[2]["rs"]),
                                     mkFlowHeader(nodes[3]["river"], nodes[3]["reach"], nodes[3]["rs"])]
        }
        path = "Z:\\adit\\Desktop\\LARFlows\\code\\pyRasFile\\FlowPerms.csv"
        perms = generatePermutedFlows(flows, nodes, upstreamNodes, write = True, path = path, debug = True)
        for key in perms:
            print("%s: %d" % (key, len(perms[key])))