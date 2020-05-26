import pandas as pd

raw_data = pd.read_csv('cloud_communication_results.csv')

raw_data['dC'] = raw_data['MessageCount'].diff()
print(raw_data)
result = raw_data[raw_data['dC'] > 1]
print(result)

result.to_csv('missing_frames.csv', index=False)