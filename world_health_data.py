import wbdata
import pandas as pd
import numpy as np
from datetime import date

INDICATOR_CODES = ["SP.DYN.LE00.IN", "SH.XPD.CHEX.PC.CD", "SH.DYN.MORT", "SH.IMM.POL3", "SH.MED.PHYS.ZS"]

class WorldHealthData:
    """ A class for accessing the World Health Data """

    def load_and_save_data(self, filepath: str = "data/world_health_indicators.csv"):
        """ Returns the world health data """
        country_map = {c['name']: c['id'] for c in wbdata.get_countries()}
        data_tables = []
        for indicator in INDICATOR_CODES:
            data = wbdata.get_series(indicator, keep_levels=True, freq='M', name=indicator)
            data_tables.append(data)
        all_data = pd.DataFrame(data_tables).transpose()
        # all_data["CountryId"] = all_data.index.get_level_values("country").map(country_map)
        all_data["CountryId"] = [country_map.get(x) for x in all_data.index.get_level_values("country")]
        all_data.to_csv(filepath)

    def get_all_data(self, filepath: str = "data/world_health_indicators.csv"):
        """ Returns the pandas dataframe with all the data """
        return pd.read_csv(filepath, header=0, names=["Country", "Date", "Life Expectancy", "Health Expenditure", "Mortality Rate", 
                                            "Polio Immunization", "Physician Count", "CountryId"], index_col=["Country", "CountryId", "Date"], dtype={"Date": np.int64})
