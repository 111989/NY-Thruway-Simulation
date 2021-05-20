import pandas as pd
from matplotlib import pyplot as plt

PATH = "/home/capstone/Documents/AMS_553_Final_Project/expanded_results.csv"

data = pd.read_csv(PATH)
means = data.mean()
print(means.describe())
means.hist()
plt.show()