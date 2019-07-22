"""
Written beginning July 18, 2019 by Daniel Philippus for the LAR Environmental Flows project at Colorado School of Mines.

This component of the program writes a set of flows to a HEC-RAS steady state flow file under the relevant profiles.

Between this and reportReader, a set of profiles can be automatically generated, after which HEC-RAS is run, a report
generated, and the report automatically converted into a machine-friendly CSV format for further processing (e.g.
statistical analysis with R).
"""

"""
HEC-RAS flow file format (saved as *.f01, etc):

Flow Title=Flow 01
Program Version=5.07
Number of Profiles= 125
Profile Names=PF 1,PF 2,PF 3,...
River Rch & RM=Compton Creek,CC              ,52494.08
       1       1       1       1       1       1       1       1       1       1
       1       1       1       1       1       1       1       1       1       1
       1       1       1       1       1      10      10      10      10      10
      10      10      10      10      10      10      10      10      10      10
      10      10      10      10      10      10      10      10      10      10
     100     100     100     100     100     100     100     100     100     100
     100     100     100     100     100     100     100     100     100     100
     100     100     100     100     100    1000    1000    1000    1000    1000
    1000    1000    1000    1000    1000    1000    1000    1000    1000    1000
    1000    1000    1000    1000    1000    1000    1000    1000    1000    1000
   10000   10000   10000   10000   10000   10000   10000   10000   10000   10000
   10000   10000   10000   10000   10000   10000   10000   10000   10000   10000
   10000   10000   10000   10000   10000
<Other reaches>
Boundary for River Rch & Prof#=Compton Creek,CC              , 1 
Up Type= 0 
Dn Type= 0
<Other reaches>
DSS Import StartDate=
DSS Import StartTime=
DSS Import EndDate=
DSS Import EndTime=
DSS Import GetInterval= 0 
DSS Import Interval=
DSS Import GetPeak= 0 
DSS Import FillOption= 0 
"""

"""
Format notes:
* The end of one number is always exactly 8 characters to the right of the end of the previous (columns width 8), i.e.
    the last digit is always the 8th character
* There are at most 10 columns
* The comma before the profile number in the boundary condition is 17 columns to the right of the comma
    before the reach name, e.g. in columns 45 and 62 respectively, i.e. 16 characters (including reach name) in between
* The boundary condition type 0 means junction or no particular boundary condition (for upstream reaches)
* BC 1,2,3,4 presumably mean, respectively, Known W.S., Critical Depth, Normal Depth, and Rating Curve.  Formats
are as follows:

Known WS:
Up Type= 0 
Dn Type= 1 
Dn Known WS=10

Crit Depth:
Up Type= 0 
Dn Type= 2 

Norm. Depth:
Up Type= 0 
Dn Type= 3 
Dn Slope=0.05

Rating Curve doesn't seem to be specified in the flow profiles file.

Note that the boundary conditions are duplicated for each profile, thus a long sequence of:

Boundary for River Rch & Prof#=Upper LA River,RH to CC        , 125 
Up Type= 0 
Dn Type= 0 
"""

# I think this is just for unsteady flow, no need for now to support modifications to it
FILE_END = """DSS Import StartDate=
DSS Import StartTime=
DSS Import EndDate=
DSS Import EndTime=
DSS Import GetInterval= 0 
DSS Import Interval=
DSS Import GetPeak= 0 
DSS Import FillOption= 0"""

def mkBoundaryHeader(river, reach, profile):
    # River/reach/profile specification for boundary conditions
    return "Boundary for River Rch & Prof#=%s,%s%s, %d" % (river,reach, " " * (16 - len(reach)), profile)

def mkBoundaryData(upname, dname, uparam="", dparam=""):
    # boundary condition data
    types = {"Known WS": 1, "Critical Depth": 2, "Normal Depth": 3, "Junction": 0}
    data = {1: "Known WS", 3: "Slope"}
    utype = types[upname]
    dtype = types[dname]
    items = ["Up Type= %d" % utype, "Dn Type= %d" % dtype]
    if utype in [1, 3]:
        items.append("Up %s=%s" % (data[utype], uparam))
    if dtype in [1,3]:
        items.append("Dn %s=%s" % (data[dtype], dparam))
    return items

def mkBoundary(river, reach, profile, upname, dname, uparam, dparam):
    # Full boundary condition
    return "\n".join([mkBoundaryHeader(river, reach, profile)] + mkBoundaryData(upname, dname, uparam, dparam))

def mkFlowHeader(river, reach, station):
    # River, reach, station specification for flow data
    return "River Rch & RM=%s,%s%s,%s" % (river, reach, " " * (16 - len(reach)), station)

def mkFlowData(flows):
    # Flow data
    flowStrs = [str(flow) for flow in flows]
    flowStrs = [" " * (8-len(flow)) + flow for flow in flowStrs]
    flowRows = []
    prev = 0
    for ix in range(1, len(flowStrs)):
        if ix % 10 == 0:
            flowRows.append(flowStrs[prev:ix])
            prev = ix
    if prev < len(flowStrs) - 1:
        flowRows.append(flowStrs[prev:])
    return ["".join(row) for row in flowRows]

def mkHeader(nprofiles, title="Flow 01", ver="5.0.7"):
    # File header - title,version,profile information
    return "Flow Title=%s\nProgram Version=%s\nNumber of Profiles= %d\nProfile Names=%s" % (
        title,
        ver,
        nprofiles,
        ",".join(["PF %d" % pn for pn in range(1, nprofiles + 1)])
    )

def buildFile(nprofiles, profiledata, bounddata, title="Flow 01", ver="5.0.7", end=FILE_END):
    """
    profiledata format: a dictionary of the necessary data.
        {flowheader: [flows]}
    bounddata: a dictionary of the necessary boundary condition generators, as functions
        {"River,Reach": function}
            The function accepts the profile number and the flow volume (though it need not use the latter),
            and returns the appropriate boundary data as a string
    """
    header = mkHeader(nprofiles, title, ver)
    flowdata = []
    bounds = []
    # Build flow data and boundary data
    for pheader in profiledata.keys():
        flowdata.append(pheader)
        flows = profiledata[pheader]
        if len(flows) != nprofiles:
            raise ValueError("Number of flow profiles given does not match specified profile count!")
        fd = mkFlowData(flows)
        flowdata = flowdata + fd
        boundspec = pheader.split("=")[1].split(",")[0:2] # This grabs the river and reach
        boundspec[1] = boundspec[1].strip()
        for pn in range(0, nprofiles):
            bheader = mkBoundaryHeader(boundspec[0], boundspec[1], pn + 1)
            bdata = bounddata[",".join(boundspec)](pn + 1, flows[pn])
            bounds.append(bheader)
            bounds = bounds + bdata
    return "\n".join([header] + flowdata + bounds + [end])

