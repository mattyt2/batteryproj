# batteryproj
This is a project to create an ideal solar and storage project and analyse yields and revvenues

Inputs: Irr.csv: a file containing 1 minute interval irradiation data for an entire year
        prices.csv: Hourly wholesale electricity price data

I have firstly created a very basic model of a solar farm, assuming that given a 5MW produces 5MW at 1000 w/m2 irradiation, the output for a given irradiation is irradiation/1000*output.
The user specifies the AC and DC components of
This power is then clipped: If it goes over the "AC capacity", the output is the AC capacity.
The user can then add an extension (CapDCext and CapACext) which, exports to the grid, charges a battery, or is controlled to respect the grid limit (assumed to be CapAC) 

The battery logic is very simple, it charges when there is surplus power (the extension and original solar farm are developing power above the value of the grid connection) up to a value of "Battfull",
discharges when the power from the solar panels is below the CapAC limit. Assumed that it charges and sicharges at the same rate. 

I then iterate for different sizes of extension and battery. introducing basic financial modelling parameters Cap Ex and opex,and a PPA price

THIS BIT DOESN'T WORK FOR THE MOMENT We then introduce price data from the wholesale electricity market.

To be honest this is a thought experiment because the costs have to be unrealistically low and PPA price so high to allow an optimisation.

Have fun!
