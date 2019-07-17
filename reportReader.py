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