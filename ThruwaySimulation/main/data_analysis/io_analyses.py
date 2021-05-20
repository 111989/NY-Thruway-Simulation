"""
    Determining parameters required to generate inputs
    for the simulations by fitting Poisson & 
    Negative Binomial Distributions to Vehicle Count, 
    and evaluating Chi-Square Goodness-of-Fit statistics
    
    Producing .csv files for simulation inputs 
    
    Computing Coverage Percentages over 10000 runs 
    by means of Maximum Likelihood Estimation
"""

import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm 
import statsmodels.formula.api as smf
from scipy import stats

"""
    Input Analysis
"""

file = pd.read_csv("final_study_data.csv")
file_copy = file.copy()

vehicle_class = file["vehicle_class"].unique()
vehicle_class.sort()

entrance_site = file["entrance_site"].unique()
entrance_site.sort()

entrance, vclass, lambda_parameter, intercept, alpha, chisqstat, pvalue \
    = [], [], [], [], [], [], []
    
for i in range(len(entrance_site)):
    for j in range(len(vehicle_class)):
        file = file_copy[(file_copy["entrance_site"] \
            == entrance_site[i]) & (file_copy["vehicle_class"] \
                == vehicle_class[j]) & (file_copy["year"] == 2019) \
                    & (file_copy["payment_type"] == "E-ZPass")]
        x = file["week_of_year"].unique()
        x.sort()
        dataframe = file.drop(["exit_site","payment_type","profit","year"],\
             axis = 1).groupby("week_of_year").mean()
        y = dataframe["vehicle_count"].values
        
        model_p = smf.poisson("vehicle_count ~ 1", data = dataframe)
        result_p = model_p.fit()
        lambda_ = float(np.exp(result_p.params))
        
        entrance.append(entrance_site[i])
        vclass.append(vehicle_class[j])
        lambda_parameter.append(lambda_)
        
        minimum = int(y.min())
        maximum = int(y.max())
        while minimum % 10 != 0:
            minimum -= 1
        while maximum % 10 != 0:
            maximum += 1
        X = stats.poisson(lambda_)
        v, k = np.histogram(y, range = (minimum, maximum), density = True)
        chisquare_ = stats.chisquare(v, f_exp = X.pmf(k[:-1]))[0]
        pvalue_ = stats.chisquare(v, f_exp = X.pmf(k[:-1]))[1]
        chisqstat.append(chisquare_)
        pvalue.append(pvalue_)
        
        model_nb = smf.negativebinomial("vehicle_count ~ 1", \
            data = dataframe, loglike_method='nb2')
        result_nb = model_nb.fit()
        intercept.append(float(result_nb.params.values[0]))
        alpha.append(float(result_nb.params.values[1]))
        
dataframe = {
    "entrance_site": entrance,
    "vehicle_class": vclass,
    "lambda": lambda_parameter,
    "intercept": intercept,
    "alpha": alpha,
    "chisquare": chisqstat,
    "pvalue": pvalue
}
dataframe = pd.DataFrame(dataframe, columns = ["entrance_site", "vehicle_class", "lambda", "intercept", "alpha", "chisquare", "pvalue"])
dataframe.to_csv(r"C:\Users\16315\Desktop\Projects\AMS 553\dataframe19.txt", sep = "\t")

"""
    Output Analysis
"""

fileT2 = pd.read_csv(r"C:\Users\16315\Desktop\Projects\AMS 553\Outputs\Expanded_Simulation_results_final\expanded_results_T2.csv")
dataframeT2 = fileT2.copy()

# Average profits observed in each week
weekly_profitT2 = dataframeT2.mean(axis = 0)

# Average profits observed in each run
runs_profitT2 = dataframeT2.mean(axis = 1)

# 90% Confidence Interval and Coverage
# MLE estimator for mean(X)
Xbar = runs_profitT2.mean()
std = runs_profitT2.std()
constant = 1.645/100
lowT2 = Xbar - constant*std
highT2 = Xbar + constant*std
# print("90% CI = (", lowT2, ",", highT2, ")")

# Confidence Intervals
mean = dataframeT2.describe().values[1]
std = dataframeT2.describe().values[1]

count = 0
counts, low_, high_ = [], [], []
for i in range(52):
    for j in range(10000):
        Xi = dataframeT2[weeks[i]][j]
        std_ = std[i]
        constant = 1.645/100
        low = Xi - constant*std_
        high = Xi + constant*std_
        low_.append(low)
        high_.append(high)
        if mean[i] >= low and mean[i] <= high:
            count += 1
    counts.append(count)
    count = 0
    
counts_ = np.array(counts)
coverageT2 = counts_/100
