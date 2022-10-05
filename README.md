# agr_monitoring
Scripts and documentation related to server and container monitoring at the Alliance.

## Uploading scripts to AWS Lambda.
- Instructions for uploading Python-based .zip lambda programs can be found at AWS: 
https://docs.aws.amazon.com/lambda/latest/dg/python-package.html

-----------

## Specific scripts
### restart_es
- This scripts runs via a successful SNS message sent from AlertManager when the "EndpointDown" alarm is triggered.
- Variables are taken from AWS Parameter Store.
- Due to a bug in the paramiko package, this script requires both cryptography==3.4.8 and bcrypt==3.2.2 to be explicitly declared in the requirements.txt file. See these GitHub issues for more details:
  - https://github.com/pyca/cryptography/issues/6390
  - https://github.com/paramiko/paramiko/issues/2108
    - Specifically, this comment:
      - https://github.com/paramiko/paramiko/issues/2108#issuecomment-1251760882