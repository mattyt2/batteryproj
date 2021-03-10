# -*- coding: utf-8 -*- 
"""
Created on Mon Mar  1 21:20:32 2021

@author: Matt
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def add_date_columns_to_file(input_file, output_file):
    # Load in the file...
    irr_timestamp = pd.read_csv("irr.csv")
    irr_timestamp = np.asarray(irr_timestamp)

    # Create 1D array of day of the month, month of the year, and year...
    day = [int(np.fromstring(date,sep='/',dtype=int)[0]) for date in irr_timestamp[:,0]]
    month = [int(np.fromstring(date,sep='/',dtype=int)[1]) for date in irr_timestamp[:,0]]
    year = [int(np.fromstring(date,sep='/',dtype=int)[2]) for date in irr_timestamp[:,0]]

    # Put these 3 indivdual 1D arrays together into an array of shape (N,3)...
    date_columns = np.swapaxes([day,month,year],0,1)

    # Add the date columns up into the full array...
    irr_timestamp = np.concatenate((irr_timestamp, date_columns), axis=1)
   
    # Save the array...
    np.savetxt(output_file, irr_timestamp, fmt='%s', delimiter=',')
'''
Line to convert an input file with columns ['date string', power] to ['date string', power, day, month, year]
Only really need to use the above function once, can comment it out afterwards...
'''
#add_date_columns_to_file("irr.csv", "irr_dates.csv")
##################################################################################################################################

def plot_mean_day(variables, variables_names, plot_name='averge_day_profile_by_month.png'):

    if len(variables) != len(variables_names):
        print('Each variable needs a corresponding variable name.')

    months_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    color_list = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:grey', 'tab:olive', 'tab:cyan']

    minutes_in_a_day = int(60*24)
    plot_data = np.empty((12,minutes_in_a_day,3,len(variables))) # 12: months, 3: Mean, mean-std, mean+std
    for i in range(1, 13):

        where_month = np.where((power[:,3]==i)&(power[:,4]==2020))

        print('Computing',months_list[i-1],'...')

        day_stack = np.empty((int(power[where_month][-1][2]),minutes_in_a_day, len(variables)))

        for ii in range(1, int(power[where_month][-1][2]+1)):

            where_day = np.where(power[where_month][:,2]==ii)
            # day_i = power[where_month][where_day][:,1]

            for var_i, var in enumerate(variables):

                day_i = var[np.squeeze(where_month)][np.squeeze(where_day)]

                if np.shape(day_i)[0] < minutes_in_a_day:
                    # Pad with 0s
                    size_to_pad = minutes_in_a_day - np.shape(day_i)[0]
                    day_i = np.concatenate((day_i,np.zeros(size_to_pad)))
                if np.shape(day_i)[0] > minutes_in_a_day:
                    # Cut array
                    day_i = day_i[:minutes_in_a_day]

                if np.shape(day_i)[0] != minutes_in_a_day:
                    print("Something wrong...")
                    quit()

                day_i[np.argwhere(day_i!=day_i)] = 0. # Remove nans

                day_stack[ii-1,:,var_i] = day_i
       
        for var_i in range(0,len(variables)):
            plot_data[i-1,:,0,var_i] = np.mean(day_stack[:,:,var_i],axis=0)
            plot_data[i-1,:,1,var_i] = plot_data[i-1,:,0,var_i] - (np.std(day_stack[:,:,var_i],axis=0)/np.sqrt(int(power[where_month][-1][2])))
            plot_data[i-1,:,2,var_i] = plot_data[i-1,:,0,var_i] + (np.std(day_stack[:,:,var_i],axis=0)/np.sqrt(int(power[where_month][-1][2])))


    ymax = np.amax(plot_data)
    figdims = 4
    plt.figure(figsize=(4*figdims, 3*figdims))
    subplot = 0
    for index_i, month in enumerate(months_list):
        subplot += 1
        ax = plt.subplot(3,4,subplot)

        for var_i in range(0,len(variables)):
            plt.plot(np.arange(0,minutes_in_a_day)/60., plot_data[index_i,:,0,var_i], c=color_list[var_i], label='%s'%variables_names[var_i])
            plt.fill_between(np.arange(0,minutes_in_a_day)/60., plot_data[index_i,:,1,var_i], plot_data[index_i,:,2,var_i],alpha=0.5, color=color_list[var_i])

        if subplot == 1: plt.legend()
       
        plt.text(0.04, 0.96,'%s'%months_list[index_i],horizontalalignment='left',verticalalignment='top',transform = ax.transAxes, fontsize=15)
   
        plt.ylabel('Average power')
        plt.xlabel('Hour')
        plt.xlim(0, 24)
        plt.ylim(0, ymax*1.1)  

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3, wspace=0.3)
    plt.savefig('%s'%plot_name)
    # plt.show()





#import irradiation data from file called irr.csv
fname = "irr_dates.csv"
irr_timestamp = pd.read_csv(fname)
irr_timestamp = np.asarray(irr_timestamp)
where0 = np.where(irr_timestamp[:,1] < 0)
irr_timestamp[where0, 1] = 0


#smooth data to remove noise. Entering 5 here means data is averaged
#into 5 minute blocks
def moving_average(a, n=1):
    '''
        inputs: a 1D array of power data, and a number of steps to average over... defaults to 10 minutes
        example:
                P_Ext_Clipped[:,1] = moving_average(P_Ext_Clipped[:,1], 10)
    '''
    return np.convolve(a, np.ones((n,))/n, mode='same')

   
#Define resolution of model eg n=15
irr_timestamp[:,1] = moving_average(irr_timestamp[:,1], 5)


#Create arrays called "ields" and "revenues" to contain monthly yields*PPA
revenues = np.empty((0,4))
yields = np.empty((0,4))


CapDC = 4990.
CapAC = 3850.
PPA = 0.15 #ppa price in pence per kWh

###################################################################
# for j_index, j in enumerate(range(0,5000,500)):

#####################################################################
#Model of plant
CapDCExt = 500
CapACExt = 500

#Battery info
BattP = 1000 #Battery power in kW
BattFull = 1000 #Battery cap in kWh


#convert irradiation to theoretical power based on DC capacity
power = irr_timestamp.copy()
power[:,1] = power[:,1]/1000.* CapDC

#Limit power to AC limit (assumed to be the same as GC)
P_clipped = power.copy()
P_clipped[np.where(P_clipped[:,1]>CapAC)]= CapAC

#Work out power of extension
P_Ext = irr_timestamp.copy()
P_Ext[:,1] = irr_timestamp[:,1]/1000*CapDCExt
P_Ext_Clipped = P_Ext.copy()
P_Ext_Clipped[np.where(P_Ext_Clipped[:,1]>CapACExt)] = CapACExt

P_tot = irr_timestamp.copy()
P_tot[:,1] = P_clipped[:,1] + P_Ext_Clipped[:,1]
#######################################################
# =============================================================================
# This is the model of the battery. Really simple, it charges when there is AC
# power available that would otherwise be curtailed by the control system. Then
# it discharges as soon as it can! 
# =============================================================================


SoC = np.zeros(len(P_tot))
disCharge = np.zeros(len(SoC))

for k in range(1, len(P_tot)):

    surplus_power = False
    battery_full = False
    power_close_to_limit = False

    if SoC[k-1] == BattFull:
        battery_full = True
    if P_tot[k,1] > CapAC:
        surplus_power = True
    if np.abs(CapAC - P_tot[k,1])<BattP:
        power_close_to_limit = True

    charge = False
    charge_reduced_rate = False
    discharge = False
    discharge_reduced_rate = False

    if battery_full == False and surplus_power:
        charge = True
        if power_close_to_limit:
            charge_reduced_rate = True

    elif surplus_power == False:
        discharge = True # If no surplus power want to discharge as soon as possible...

        if power_close_to_limit:
            discharge_reduced_rate = True

    elif surplus_power and battery_full:
        SoC[k] = SoC[k-1]

    if charge == True and discharge == True:
        print('charge == True and discharge == True')
        quit()

    if charge_reduced_rate:
        SoC[k] = SoC[k-1] + (P_tot[k,1] - CapAC)/60

    elif charge:
        SoC[k] = SoC[k-1] + BattP/60

    elif discharge_reduced_rate:
        SoC[k] = SoC[k-1] - (CapAC - P_tot[k,1])/60

    elif discharge:
        SoC[k] = SoC[k-1] - BattP/60


    if SoC[k] < 0:
        SoC[k] = 0
    if SoC[k] > BattFull:
        SoC[k] = BattFull

    if (SoC[k] - SoC[k-1]) < 0:
        disCharge[k] = -(SoC[k] - SoC[k-1])




# quit(0)
#     # if SoC[timestep-1] == 0: # If empty..

P_controlled = P_Ext_Clipped.copy()
where = np.where(np.add(P_Ext_Clipped[:,1],P_clipped[:,1])>CapAC)[0]
P_Ext_Clipped[where,1] = CapAC-P_clipped[where,1]
P_controlled[:,1] = P_Ext_Clipped[:,1] + P_clipped[:,1]

outflow = disCharge*60 + P_controlled[:,1]
print(np.amax(outflow))
   
#calculate monthly yields in kWhs, 2nd column is of original plant, 3rd is extension, 4th is battery
monthly_yields = np.empty([12,4])
for i in range(1, 13):
    where = np.where(irr_timestamp[:,3]==i)
    monthly_yields[i-1][1] = np.nansum(P_clipped[where,1])/60
    monthly_yields[i-1][2] = np.nansum(P_Ext_Clipped[where,1])/60
    monthly_yields[i-1][3] = np.nansum(disCharge[where])
    monthly_yields[i-1][0] = i
# print(disCharge, np.sum(disCharge))
# quit()
#Sum monthly yields for annual (slightly pointless bit :) )
annual_yield = np.nansum(monthly_yields[:,1])
annual_yield_ext = np.nansum(monthly_yields[:,2])
annual_yield_batt  = np.nansum(monthly_yields[:,3])
annual_revenue = annual_yield * PPA
annual_revenue_ext = annual_yield_ext * PPA
annual_revenue_batt = annual_yield_batt * PPA
revenues = np.append(revenues, [['j',annual_revenue, annual_revenue_ext, annual_revenue_batt]], axis=0)
yields = np.append(yields, [['j', annual_yield, annual_yield_ext, annual_yield_batt]], axis =0)

print(annual_yield_ext)
print(annual_yield_batt)
    
    #print(revenues)

variables = [P_tot[:,1], SoC]
variables_names = ['Power', 'SoC']

plot_mean_day(variables, variables_names, plot_name='mean_plot.png')    

###########################################################################
#Indent up to here for iteration


############################################################################
plot_start = 150000
plot_end = 160000

plt.figure(figsize=(8,4))

#plt.subplot(1,2,1)
plt.plot(P_tot[plot_start:plot_end,1],label='P_tot')
#plt.plot(power[plot_start:plot_end,1],label='power')
#plt.plot(P_controlled[plot_start:plot_end,1],label='P_controlled')
plt.plot(SoC[plot_start:plot_end],label='SoC')
plt.plot(outflow[plot_start:plot_end],label='Export')
plt.axhline(y=BattFull,c='k')
plt.axhline(y=CapAC,c='k')
plt.legend()
plt.ylabel('Power (kW)?')
plt.xlabel('Time (mins)')

# plt.subplot(1,2,2)
# plt.plot(outflow[plot_start:plot_end]-P_clipped[plot_start:plot_end,1],label='benefit')
# plt.legend()
# plt.ylabel('Power (kW)?')
# plt.xlabel('Time (mins)')


plt.savefig('SoC.pdf')
plt.show()

# plt.close('all')
################################################################################

###############################################################################
plt.figure(figsize=(8,4))
plt.plot(yields[:,0], yields[:,3])
#plt.plot(revenues[:,0], revenues[:,3])
#plt.savefig('revenues_from_ext_and_batt.png')
plt.savefig('battery_optimiser.png')
plt.show()
# plt.close('all')
##############################################################################


