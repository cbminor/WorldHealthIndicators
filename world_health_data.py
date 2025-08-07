import wbdata
import pandas as pd

INDICATOR_CODES = ["SP.DYN.LE00.IN", "SH.XPD.CHEX.PC.CD", "SH.DYN.MORT", "SH.IMM.POL3", "SH.MED.PHYS.ZS"]

class WorldHealthData:
    """ A class for accessing the World Health Data """

    def load_and_save_data(self, filepath: str = "data/world_health_indicators.csv"):
        """ Returns the world health data """
        data_tables = []
        for indicator in INDICATOR_CODES:
            data = wbdata.get_series(indicator, keep_levels=True, freq='M', name=indicator)
            data_tables.append(data)
        all_data = pd.DataFrame(data_tables).transpose()
        all_data.to_csv(filepath)

    def get_all_data(self, filepath: str = "data/world_health_indicators.csv"):
        """ Returns the pandas dataframe with all the data """
        return pd.read_csv(filepath)
