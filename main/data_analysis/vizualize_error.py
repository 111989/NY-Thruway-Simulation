import pandas as pd
from matplotlib import pyplot as plt

ANALYSIS_SAVE_PATH = '/home/capstone/Documents/AMS_553_Final_Project/Original_simulation_results/2019_analysis_2.csv'
ADJUSTED_SAVE_PATH = '/home/capstone/Documents/AMS_553_Final_Project/Original_simulation_results/2019_adjusted.csv'

orig_data = pd.read_csv(ANALYSIS_SAVE_PATH)['Mean Perc. Err.']
print(orig_data.describe())
orig_data.hist()
plt.show()
adjust_data = pd.read_csv(ADJUSTED_SAVE_PATH)['Mean Perc. Err.']
print(adjust_data.describe())
print("Adjusted 95th",adjust_data.quantile(.95))
adjust_data.hist()
plt.show()