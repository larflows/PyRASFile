# PyRASFile
A set of Python scripts designed to automatically produce and process key input and
output files for HEC-RAS.  Since HEC-RAS can run many flow profiles in parallel, this
allows users to run HEC-RAS on large volumes of data with minimal manual intervention.

See `main.py` for example usage (the developer's actual usage) of both writing profiles and reading
reports.

## Writing Profiles
The `profileWriter` script can be used to generate a flow profiles file (.fxx) with any number
of profiles and reaches and any set of flow volumes for each point.  The `buildFile` function
contains the main functionality and will build the complete contents of a flow file.

### General Notes
Minor manual intervention is currently required if the output file is not named to match an existing
set of flow data, as HEC-RAS will not be able to find it.  In order to fix this, edit the `.prj` project
file and add an entry for the new flow file in with the other flow file entries.

### `buildFile` Inputs Summary
`buildFile` requires the following inputs:

* `nprofiles`: the number of profiles to be generated
* `profiledata`: the data on flows for each profile; see below.
* `bounddata`: the data on boundary conditions; see below.
* `title` and `ver`: the title for the flow profile and the version of HEC-RAS in use.
* `end`: the data for the end of the file; this doesn't seem to require modification
for steady flows, so this can typically be left as the default.

### `buildFile` Input Details
#### `profiledata`
`profileData` needs to be in the form of a dictionary where the keys are a string specifying
the river, reach, and station, and the values are a list of the flows for each profile.  The key
strings can be made using the helper function `mkFlowHeader` to ensure the correct format.

The number of flows for each entry in `profiledata` must be identical and equal to the number
of profiles specified with `nprofines`.

#### `bounddata`
`bounddata` needs to be in the form of a dictionary where the keys are strings specifying the 
river and reach and the values are functions which will produce the appropriate boundary
information given two arguments, the profile number and the flow rate (though these may often
be ignored).

The keys should be in the format `"river,reach"`.

The boundary data functions should return strings
in the format used by `mkBoundaryData`, which accepts the arguments `upname`, `dname`, `uparam`, and
`dparam`.  `upname` and `dname` specify the type of boundary conditions, out of `Known WS`, `Critical Depth`,
`Normal Depth`, and `Junction`.  The two `param`s need only be specified if the boundary conditions are
`Known WS`, in which case they need to be a water depth appropriate to the flow rate, or `Normal Depth`,
in which case they need to be a slope.

## Reading Reports
After generating a HEC-RAS report, the `parseFile` function will parse the report file text to return a dictionary
of values for all reaches and profiles.  The `convertCSV` function will convert the report file into a CSV.