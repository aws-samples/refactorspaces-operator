## Source code for EKS Operator for Migration Hub Refactor Spaces

This is the Helm Chart to EKS Operator for Migration Hub Refactyor Spaces

## Build Instruction

1. Edit the build.sh file

a. Replace {repo} with your own repository url, where you want to push the docker image

2. Run the build script
./build.sh

The build script creates the docker image and push into the repository. To install the operator in EKS cluster, use the Helm Chart.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.


## License

This library is licensed under the MIT-0 License. See the LICENSE file.








