## Helm Chart for EKS Operator for Migration Hub Refactor Spaces

This is the Helm Chart to EKS Operator for Migration Hub Refactyor Spaces

## installation

1. Enable OIDC provider in your EKS cluster if not done already.
eksctl utils associate-iam-oidc-provider --cluster <cluster-name> --approve

2. Create an IAM Role that will be used by the EKS operator to interact with the Migration Hub Refactyor Spaces service.

a. create role refactorspace-role-cluster with following policy
    - AWSMigrationHubRefactorSpacesFullAccess 
    - AWSResourceAccessManagerFullAccess

b. Make sure you edit the trust relartionship of the role as follows - 

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::{ACCOUNTID}:oidc-provider/oidc.eks.{REGION}.amazonaws.com/id/{OIDC_ID}"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "oidc.eks.{REGION}.amazonaws.com/id/{OIDC_ID}:sub": "system:serviceaccount:refactorspace-system:refactorspace-account",
                    "oidc.eks.{REGION}.amazonaws.com/id/{OIDC_ID}:aud": "sts.amazonaws.com"
                }
            }
        }
    ]
}

Replace placeholder {ACCOUNTID}, {OIDC_ID} and {REGION} with your own value. 

You can use the following command to get the OIDC_ID - 

aws eks describe-cluster --name <CLUSTER_NAME> --query "cluster.identity.oidc.issuer" --output text looks like 
>>>> https://oidc.eks.us-east-1.amazonaws.com/id/XXXXXXXXXXXXXXXXXXXXXXXXXXX


3. Edit the values.yaml

a. replace the value in image.repository with your own repository where you pushed the rs-operator image. Refer the rs-operator/README for detail.

b. replace the value of serviceAccount.iamRoleArn with the ROle ARN that you have created in step 2

4. Run the following command to install the helm chart
helm install re-operator .

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.








