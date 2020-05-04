import os
import pandas as pd

class filesToDataFrames():

        def __init__(self, aSwapFile, aUnwinds, aCurves, aFixings, aSeasonality):

            #get the working diectory from which __main__ is being executed from, subdirectory of \dataFiles\ required
            curdirectory = str(os.path.dirname(os.path.realpath(__file__))) + '\\dataFiles\\'
            print(curdirectory)
            
            swapsfile = curdirectory + aSwapFile
            unwindfile = curdirectory  + aUnwinds
            curvesfile = curdirectory  + aCurves
            fixingfile = curdirectory + aFixings
            seasonalityfile = curdirectory + aSeasonality

            files = [swapsfile, unwindfile, curvesfile, fixingfile, seasonalityfile]
            for file in files:
                    if os.path.exists(file) == False:
                            print ('missing file! : ' + file)
                            print ('Ending Process')
                    
            self.swapsdf = pd.read_csv(swapsfile, index_col='securityid')
            self.unwinddf = pd.read_csv(unwindfile)
            self.fixingsdf = pd.read_csv(fixingfile)
        
            self.curvesdf = pd.read_csv(curvesfile)
            self.curvesdf['tenor'] = self.curvesdf['tenor'].str.replace('y','')
        
            self.seasonalitydf = pd.read_csv(seasonalityfile, index_col='month')
            self.seasonalitydf.sort_index(inplace=True)



