import pandas as pd
import math

import clsFiles
import clsFunctions

def computepvandriskforinflationswaps(valuationdate, currency, aswapsfile, aunwindfile, acurvefile, 
                afixingsfile, aseasonalityfile, nominalindex, inflationindex):

        f =  clsFiles.filesToDataFrames('swaps.csv', 'unwinds.csv', 'curves.csv', 'fixings.csv', 'seasonality.csv')
        fc = clsFunctions.functions()

        dfnominalindex = f.curvesdf[f.curvesdf['indexname'] == nominalindex]
        dfinflationindex = f.curvesdf[f.curvesdf['indexname'] == inflationindex]

        valuationdate  = pd.to_datetime(valuationdate)

        totalpresentvalue = 0
        totalpv01 = 0
        totalie01 = 0

        columns = ['securityid', 'PV', 'PV01', 'IE01', 'Duration']
        rows = []

        #determine the current cpi level from the fixing file
        lag = fc.inflationLag(currency)
        currentcpidate = valuationdate + pd.DateOffset(months = -lag)
        strdate = currentcpidate.strftime('%Y%m')

        f.fixingsdf['date2'] = pd.to_datetime(f.fixingsdf['date']).dt.strftime('%Y%m')
        currentcpilevel = f.fixingsdf.loc[f.fixingsdf['date2'] == strdate, 'indexlevel'].values[0]

        #adjust the swaps df for any unwinds that have taken place
        for index, row in f.swapsdf.iterrows():
                unwindsubtotal = f.unwinddf.loc[f.unwinddf['securityid'] == index, 'notional'].sum()
                if unwindsubtotal > 0:
                        f.swapsdf.loc[[index], ['notional'] ] -= unwindsubtotal

        for index, swap in f.swapsdf.iterrows():
                swapid = index
                notional = float(swap['notional'])

                if str(swap['direction']).upper() == 'PAY':
                        fixednotional = -notional
                else:
                        fixednotional = notional
                
                floatnotional = -fixednotional
                fixedrate = float(swap['fixedrate'])
                effectivedate = pd.to_datetime(swap['effectivedate'])
                initialcpidate = effectivedate + pd.DateOffset(months = -lag)
                strdate = initialcpidate.strftime('%Y%m')
                maturitydate = pd.to_datetime(swap['maturitydate'])

                basecpilevel = f.fixingsdf.loc[f.fixingsdf['date2'] == strdate, 'indexlevel'].values[0]
                finalcpidate = maturitydate + pd.DateOffset(months = -lag)
                yearfrac = (maturitydate - valuationdate).days / 365.25
                seasonalfactor = fc.seasonalityfactor(currentcpidate.month, finalcpidate.month, f.seasonalitydf)
                        
                #present value
                maturitydiscountfactor = fc.discountFactor(maturitydate, 0, dfnominalindex, valuationdate)
                fixedleg = fixednotional * ((1 + fixedrate/100) ** yearfrac)
                finalcpilevel = fc.inflationProjection(finalcpidate, 0, dfinflationindex, valuationdate, currentcpilevel)
                floatleg = floatnotional * (finalcpilevel * seasonalfactor) / basecpilevel
                presentvalue = (fixedleg + floatleg) * maturitydiscountfactor
                
                #price value of a basis point shift in the discount curve (pv01)
                presentvalueup1bp =  (fixedleg + floatleg) * fc.discountFactor(maturitydate, 0.01, dfnominalindex, valuationdate)
                pv01 = presentvalue - presentvalueup1bp

                #price value of a basis point shift in the inflation curve (ie01)
                finalcpilevel1bpup = fc.inflationProjection(finalcpidate, 0.01, dfinflationindex, valuationdate, currentcpilevel)
                floatlegup1bp = floatnotional * (finalcpilevel1bpup * seasonalfactor) / basecpilevel
                ie01 = (floatlegup1bp - floatleg) * maturitydiscountfactor
                duration = abs(ie01 / (notional - presentvalue)) * 10000

                row = [swapid, int(round(presentvalue)), int(round(pv01)), int(round(ie01)), round(duration,2)]
                rows.append(row)

        dfoutput = pd.DataFrame(rows, columns = columns)
        print(dfoutput)
               

def main():

        computepvandriskforinflationswaps('31/03/2020', 'GBP', 'swaps.csv','unwinds.csv', 'curves.csv',
                         'fixings.csv', 'seasonality.csv', 'SONIA', 'UKRPI')

if __name__ == '__main__':
        main()
