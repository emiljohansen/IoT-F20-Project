import pandas as pd

raw_data = pd.read_csv('cloud_communication_results.csv')

result = raw_data['LoggerBefore'].diff()
#result = result - 1
print(result)
result.to_csv('simple_reception_calculation.csv', index=False, header=False)