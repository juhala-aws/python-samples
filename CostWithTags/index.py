#!/usr/bin/env python3

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import boto3
import pandas as pd

ce_client = boto3.client('ce')
org_client = boto3.client('organizations')

# Set for time periods in CE response
time_periods = {}

# Get billing data for all linked accounts on monthly basis.
response = ce_client.get_cost_and_usage(
    TimePeriod={
        'Start': '2023-01-01',
        'End': '2023-03-31'
    },
    Granularity='MONTHLY',
    Metrics=[
        'BlendedCost'
    ],
    GroupBy=[
        {
            'Type': 'DIMENSION',
            'Key': 'LINKED_ACCOUNT'
        }
    ]
)

# Write response data to temporary dict for better structure
data = {}

for result in response['ResultsByTime']:
    # print(result)
    time_period = f'{result["TimePeriod"]["Start"]} - {result["TimePeriod"]["End"]}'

    # Store time periods in set for later use
    if time_periods == {}:
        time_periods = {time_period}
    else:
        time_periods.add(time_period)

    # Loop through groups which contain the accounts and accrued cost
    for group in result['Groups']:
        account_id = group['Keys'][0]
        cost = group['Metrics']['BlendedCost']['Amount']

        if account_id in data:
            data[account_id].update({time_period: cost})
        else:
            data[account_id] = {time_period: cost}
        

# Enrich data with tag information. This searches for tag with
# key BU and takes it value.
for account_id in data:
    response = org_client.list_tags_for_resource(
        ResourceId=account_id
    )

    for tag in response['Tags']:
        if tag['Key'] == 'BU':
            data[account_id].update({'BU': tag['Value']})


# Sort time periods 
time_periods = list(time_periods)
time_periods.sort()

# Create column structure for dataframe
columns = ['AccountId']
columns.extend(time_periods)
columns.append('BU tag')

# Initialise dataframe with columns
df = pd.DataFrame(columns=columns)

# Loop through data and create rows to dataframe
for account_id in data:
    row = [account_id]
    for time in time_periods:
        if time in data[account_id]:
            row.append(data[account_id][time])
        else:
            row.append(0)
    if 'BU' in data[account_id]:
        row.append(data[account_id]['BU'])
    else: 
        row.append('NA')
    
    df.loc[len(df)] = row

# Print dataframe
print(df)

# Write dataframe to CSV
df.to_csv('data.csv')

