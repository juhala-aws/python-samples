# CostWithTags

A sample Python script that collects billing information from AWS Cost Explorer for all accounts on a monthly basis. It will also get tag information from AWS Organizations service and integrate that with billing data.

Data is written into Pandas Dataframe for easier handling and optionally written out as CSV.

## Usage

Script expects aws-cli (https://aws.amazon.com/cli/) to be installed and credentials set.

Script needs access to AWS Organization account to get billing and tag information

**IAM Policy**
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "organizations:ListTagsForResource",
                "ce:GetCostAndUsage"
            ],
            "Resource": "*"
        }
    ]
}
```