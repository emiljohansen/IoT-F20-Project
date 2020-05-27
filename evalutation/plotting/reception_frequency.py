import pandas as pd

raw_data = pd.read_csv('simple_reception_calculation.csv')

average_reception = raw_data['reception_time'].mean()
median_reception = raw_data['reception_time'].median()
print(average_reception)
print(median_reception)
variance = raw_data['reception_time'].var()
print(variance)
precision = 1/variance
print(precision)