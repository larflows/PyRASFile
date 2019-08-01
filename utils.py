"""
Written beginning July 22, 2019 by Daniel Philippus for the LAR Environmental Flows project at Colorado School of Mines.

This file is a collection of simple utilities to aid in tasks encountered with this semi-automated HEC-RAS usage
that are not large or complex enough to merit their own module.
"""

from profileWriter import mkFlowHeader
from itertools import permutations

def generatePermutedFlows(flows, nodes, upstreamNodes, write = False, path = "", debug = False):
    """
    Generate all possible permutations of the given flows across the relevant nodes,
    with the constraint that downstream nodes will have a flow that is the sum of the nodes
    upstream of them.  Optionally, write to a CSV compatible with the format specified in
    csvReader.py for later use.
    
    :param flows: A list of the flow rates (in cfs) to use
    :param nodes: A list of the nodes, each node being a dictionary of "river", "reach", and "rs"
    :param upstreamNodes: A dictionary of which nodes are upstream of which, in the format {node: [upstream nodes]},
                            where the nodes are in the format given by mkFlowHeader from profileWriter.py.
                            Note that the upstream nodes must be a list of the furthest-upstream nodes, none of which
                            are themselves downstream of any other nodes, or it will not work.
    :param write: Whether to write to a CSV file.
    :param path: The CSV path; required if write = True.
    :return: The flow data in the standard flow-data format used by the package, which is {node: [flows]}
    """

    nodeKeys = {}
    for node in nodes:
        key = mkFlowHeader(node["river"], node["reach"], node["rs"])
        nodeKeys[key] = {}
        # Need to keep the original data around for writing as CSV
        nodeKeys[key]["data"] = node
    # Nodes that don't have any nodes upstream of them
    noUpstream = [node for node in nodeKeys.keys() if (node not in upstreamNodes.keys()) or upstreamNodes[node] == []]
    # Number of unconstrained nodes
    nuc = len(noUpstream)
    nflows = len(flows)
    nperms = nflows ** nuc
    if debug:
        print("N. Permutations: %d" % nperms)
    # perms = permutations(flows, nuc)
    perms = [[]] * nuc
    """
    The idea here:
        First node: each flow in order repeated nperms / n. flows times, run once
        Second node: each flow in order repeated nperms / (n. flows)^2 times, run n. flows times
        nth node: each flow in order repeated nperms / (n. flows)^n times, run n.flows ^ n times
    Therefore, we iterate through the number of permutations first (0 to n.flows - 1), and within each loop,
    we iterate through the number of flows.
    
    For each entry in the permutations, the index in the flows needs to be (0 * nreps), (1 * nreps), etc, which should
    be... Let's look at it with 2 flows and 3 upstream locations.  Our permutations of indices are:
    0 0  0 0  1 1  1 1
    0 0  1 1  0 0  1 1
    0 1  0 1  0 1  0 1
    
    So for the first row, it's index // 4 = index // (nflows ^ 2) = index // (nflows ^ (nuc - 1))
    Second row, it's index // 2 mod 2 = index // nflows mod nflows = index // (nflows ^ (nuc - 2)) mod nflows
    Third row, it's index mod 2 = index // (nflows ^ (nuc - 3)) mod nflows
    
    So our overall formula should be... (index // (nflows ^ (nuc - row - 1))) mod nflows.
    
    This runs across the number of rows nuc, and within each row, index iterates from 0 to nperms
    """
    # Oddly, each index of permutations gets longer -- e.g. 125, 250, 375.  Why?
    # It seems like each set of these may be getting appended to *all* sets of
    # permutations.  This makes no sense at all.  It is what is happening, however,
    # as all the permutations end up the same.
    for nn in range(0, nuc):
        for ix in range(0, nperms):
            index = (ix // (nflows ** (nuc - nn - 1))) % nflows
            # Yes, this is weird, but otherwise it was appending it to *everything*
            # Because Pythonic weirdness, I guess?  I've seen it behave oddly before,
            # just not in this particular way.
            perms[nn] = perms[nn] + [flows[index]]
    if debug:
        for perm in perms:
            print("Permutation length: %d" % len(perm))
        permsEqual = True
        for perm in perms:
            for perm2 in perms:
                if perm != perm2:
                    permsEqual = False
        print("Permutations are equal: %s" % str(permsEqual))

    # Assign each set of flows to a node
    # BUG: for some reason these are getting written to 3x more than they should, and it's happening
    # here at the latest
    index = 0
    for key in noUpstream:
        nodeKeys[key]["flows"] = perms[index]
        index += 1

    # Now, set up the downstream nodes
    for key in nodeKeys.keys():
        if key in upstreamNodes.keys():
            nodeKeys[key]["flows"] = []
            upstream = upstreamNodes[key]
            for ix in range(0, nperms):
                # Sum of the upstream flows
                nodeKeys[key]["flows"].append(sum([nodeKeys[u]["flows"][ix] for u in upstream]))
    # Need to restructure the dict to be {node key: [flows]}
    output = {}
    # for key in nodeKeys.keys():
    for key in noUpstream:
        output[key] = nodeKeys[key]["flows"]

    # Set up the CSV, if needed
    if write:
        with open(path, "w") as outfile:
            lines = ["river,reach,rs,profilenumber,flow"]
            for entry in nodeKeys.values():
                data = entry["data"]
                datastr = "%s,%s,%s" % (data["river"], data["reach"], data["rs"])
                for index, flow in enumerate(entry["flows"]):
                    # Index is for the profile number
                    lines.append("%s,%d,%f" % (datastr, index + 1, flow))
            outfile.write("\n".join(lines))
    return output