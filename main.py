from profileWriter import *
from reportReader import *

# Entries to look for
ENTRIES = ["Q Total (cfs)", "Avg. Vel. (ft/s)", "Max Chl Dpth (ft)"]

# File path for current development
PATH = "V:\\LosAngelesProjectsData\\HEC-RAS\\Full MODEL\\FullModel.rep"
OUTPATH = "Z:\\adit\\Desktop\\LARFlows\\Data Processing\\ReportOutput.csv"


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

flowdata = {
    "River Rch & RM=Compton Creek,CC              ,52494.08": upstreamFlows[0],
    "River Rch & RM=LA River,Below CC        ,29266": downstreamFlows[1],
    "River Rch & RM=Rio Hondo Chnl,RHC             ,44113": upstreamFlows[1],
    "River Rch & RM=Upper LA River,Above RH        ,225805.0": upstreamFlows[2],
    "River Rch & RM=Upper LA River,RH to CC        ,63900.3*": downstreamFlows[0]
}

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

text = buildFile(125, flowdata, bounds, title="GenFlow 1-10Kcfs 1-125")

if __name__ == "__main__":
    generate = False
    parse = True
    if generate:
        with open("V:\\LosAngelesProjectsData\\HEC-RAS\\Full Model\\FullModel.f05", "w") as f:
            f.write(text)
    if parse:
        convertCSV(NODES, entries = ENTRIES, inpath = PATH, outpath = OUTPATH, selective = True)
