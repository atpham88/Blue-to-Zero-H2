# About
Macro-energy model of joint power and hydrogen systems for long-term planning for power and hydrogen infrastructure following the blue to zero carbon hydrogen pathways.
![model_chart2](https://user-images.githubusercontent.com/56058936/233448635-48dd42eb-469c-457c-be8d-30a7afddeb3a.png)

# Model Overview
![model_chart](https://user-images.githubusercontent.com/56058936/233443256-9aca0dab-de9d-4478-b04d-646cf2a03487.png)

# Programming language
The model is programmed in GAMS and Python and solved using CPLEX.

# Running model
Run model from MASTER.py. Main options to choose from:
| Option | Description |
| --- | --- |
| `runOnSC` | `False` if run locally, `True` if run on supercomputer|
| `coOptH2` | `False` if run power system only, `True` if run joint power and hydrogen system|
| `h2DemandScr` | `Reference` if use **Reference** scenario for hydrogen demand |
| `interconn` | Three options `WECC`, `EI` (Eastern Interconnection), and `ERCOT` |
| `reSourceMERRA` | `True` if use weather data from **MERRA**, otherwise use weather data from **NSRDB** and **WIND Toolkit*|
| `metYear`| Year of meteorogical data. Dafult is `2012`|
| `h2Pathway` | `blueToZero` or `Zero`|
| `buildLimitsCase` | `1`: Reference, `2`: limited nuclear, `3`: limited CCS and nuclear, `4`:limited hydrogen storage, `5`:limited transmission|
| `electrifiedDemand` | `True` if import electrified demand futures from NREL's EFS |
| `elecDemandScen` | Level of demand electrification. Options: `REFERENCE`, 'HIGH', 'MEDIUM'|
| `balAuths` | `full` if run for all BAs in interconn, `state` if run at state resolution|
| `yearIncDACS` | Default is `2100`- Year to include DACS - set beyond end period if don't want DACS|
| `startYear`, `endYear`, `yearStepCE` | Year that planning starts, year that planning ends, and timestep (in years). Default is `2020`, `2051`, `15` |
