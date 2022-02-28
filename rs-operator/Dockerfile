FROM python:3.7-alpine
ADD ./controller /src
RUN pip install kopf boto3 kubernetes==20.13.0
CMD kopf run /src/rfconroller.py --verbose
