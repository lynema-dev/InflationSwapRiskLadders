import numpy as np

class functions():

    def __init__(self):
        pass

    def inflationLag(self, currency):

        if currency == 'GBP':
            lag = 2
        elif currency == 'EUR':
            lag = 3
        else:
            lag = 2
        return lag


    def discountFactor(self, date, shift, curvesdf, valuationdate):
        
        x = curvesdf['tenor']
        y =  curvesdf['rate'] + shift

        tenorpoint = (date - valuationdate).days / 365.25
        rate = np.interp(tenorpoint, x, y)
        return 1 / ((1 + rate/100) ** tenorpoint)
        

    def inflationProjection(self, date, shift, curvesdf, valuationdate, currentcpilevel):
        
        x = curvesdf['tenor']
        y = curvesdf['rate'] + shift

        tenorpoint = (date - valuationdate).days / 365.25
        rate = np.interp(tenorpoint, x, y)
        return currentcpilevel * (1 + rate/100) ** tenorpoint


    def seasonalityfactor(self, monthfrom, monthto, seasonalitydf):
        
        seasonalproduct = 1

        if monthfrom == monthto:
            seasonalproduct = 1
        else:
            for i in range(12):
                if (i+1) >=  monthfrom or (i+1) <= monthto:
                    seasonalproduct = seasonalproduct * float(seasonalitydf.loc[seasonalitydf.index == (i+1),'factor'])

        return float(seasonalproduct)



        
        






