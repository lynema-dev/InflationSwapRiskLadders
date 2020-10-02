import pandas as pd
import math
import copy
import matplotlib.pylab as plt
from pandas.plotting import register_matplotlib_converters

import clsFiles
import clsFunctions

def computepvandriskforinflationswaps(valuationdate, currency, aswapsfile, aunwindfile, acurvefile, 
                afixingsfile, aseasonalityfile, nominalindex, inflationindex, ShowRiskLadderCharts):

        if ShowRiskLadderCharts:
                register_matplotlib_converters()
                chartfigure = 1

        f =  clsFiles.filesToDataFrames('swaps.csv', 'unwinds.csv', 'curves.csv', 'fixings.csv', 'seasonality.csv')
        fc = clsFunctions.functions()

        dfnominalindex = f.curvesdf[f.curvesdf['indexname'] == nominalindex]
        dfinflationindex = f.curvesdf[f.curvesdf['indexname'] == inflationindex]

        valuationdate  = pd.to_datetime(valuationdate)

        columns = ['securityid', 'PV', 'PV01', 'IE01', 'Duration']
        rows = []

        riskcolumns = ['tenor', 'indexname', 'pv01']
        dfriskladdernominal = pd.DataFrame(columns=riskcolumns)

        riskcolumns = ['tenor', 'indexname', 'ie01']
        dfriskladderinflation = pd.DataFrame(columns=riskcolumns)
        riskrow = []

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
                fixedleg = fixednotional * ((1 + fixedrate/100) ** yearfrac)

                swapdetails = 'SwapID: ' + str(swapid) + ', ' + str(swap['direction']) + ' fixed @' \
                        + str(fixedrate) + ', maturity: ' \
                        + str(maturitydate.strftime('%d/%m/%Y')) + ', notional: ' + str(notional)

                #subfunction to determine the value of a swap for a given pair a curves
                def PresentValue(dfnominalindextarget, dfinflationindextarget):
                        maturitydiscountfactor = fc.discountFactor(maturitydate, 0, dfnominalindextarget, valuationdate)
                        finalcpilevel = fc.inflationProjection(finalcpidate, 0, dfinflationindextarget, valuationdate, currentcpilevel)
                        floatleg = floatnotional * (finalcpilevel * seasonalfactor) / basecpilevel
                        return (fixedleg + floatleg) * maturitydiscountfactor

                presentvalue = PresentValue(dfnominalindex, dfinflationindex)

                #loop through the nominal curve to calculate the pv01 ladder
                dfriskladdernominal = dfriskladdernominal[0:0]
                for index2, row in dfnominalindex.iterrows():
                        dfnominalindexbumped = copy.copy(dfnominalindex)
                        tenor = dfnominalindexbumped.loc[index2, 'tenor']
                        dfnominalindexbumped.loc[index2, 'rate'] += 0.01
                        presentvaluebumped = PresentValue(dfnominalindexbumped, dfinflationindex)
                        pv01 = presentvalue - presentvaluebumped
                        riskrow = [tenor, nominalindex, pv01]
                        dfriskladdernominal.loc[len(dfriskladdernominal)] = riskrow

                #loop through the inflation curve to calculate the ie01 ladder
                dfriskladderinflation  = dfriskladderinflation[0:0]
                for index2, row in dfinflationindex.iterrows():
                        dfinflationindexbumped = copy.copy(dfinflationindex)
                        tenor = dfinflationindexbumped.loc[index2, 'tenor']
                        dfinflationindexbumped.loc[index2, 'rate'] -= 0.01
                        presentvaluebumped = PresentValue(dfnominalindex, dfinflationindexbumped)
                        ie01 = presentvalue - presentvaluebumped
                        riskrow = [tenor, inflationindex, ie01]
                        dfriskladderinflation.loc[len(dfriskladderinflation)] = riskrow

                totalpv01 = round(dfriskladdernominal['pv01'].sum(),1)
                totalie01 =  round(dfriskladderinflation['ie01'].sum(),1)
                duration = abs(totalie01 / (notional - presentvalue)) * 10000

                if ShowRiskLadderCharts:
                        fig = plt.figure(num=chartfigure, figsize=(8,8))
                        fig.tight_layout(pad=3.0)
                        title = swapdetails + '\n' + 'Present Value: ' + format(round(presentvalue,0),',.0f') \
                                + ' ' + nominalindex + ' PV01: ' + format(round(totalpv01,0),',.0f') \
                                + ', ' + inflationindex + ' PV01: ' + format(round(totalie01,0),',.0f')
                        fig.suptitle(title, fontsize=10, fontweight='bold')
                        plt.subplot(2,1,1)
                        plt.bar(dfriskladderinflation['tenor'],dfriskladderinflation['ie01'], color = 'slategrey')
                        plt.title(inflationindex + ' IE01 Risk Ladder', fontsize=9, fontweight='bold')
                        plt.subplot(2,1,2)
                        plt.bar(dfriskladdernominal['tenor'],dfriskladdernominal['pv01'], color = 'slategrey')
                        plt.title(nominalindex + ' PV01 Risk Ladder', fontsize=9, fontweight='bold')
                        chartfigure += 1

                row = [swapid, int(round(presentvalue)), int(round(totalpv01)), int(round(totalie01)), round(duration,2)]
                rows.append(row)

        dfoutput = pd.DataFrame(rows, columns = columns)
        print(dfoutput)

        plt.show()
               

def main():

        computepvandriskforinflationswaps('31/03/2020', 'GBP', 'swaps.csv','unwinds.csv', 'curves.csv',
                         'fixings.csv', 'seasonality.csv', 'SONIA', 'UKRPI', True)

if __name__ == '__main__':
        main()
