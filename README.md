## EKS Operator for Migration Hub RefactorSpaces

The solution uses a custom built Kubernetes operator which looks for Kubernetes services of type LoadBalancer, Ingress and NodePort in the EKS cluster where the operator is installed, and then uses APIs to manage the service and route configuration in Migration Hub Refactor Spaces.

The helm chart to installation the operator is in the "helm" folder. Refer README file in the "helm" folder for the instruction.

You can find source code of the operator in the "rs-operator" folder. Refer README file for build.


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

