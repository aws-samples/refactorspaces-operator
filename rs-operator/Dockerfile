FROM python:3.7-alpine
ADD ./controller /src
RUN pip install kopf boto3 kubernetes
CMD kopf run /src/rfconroller.py --verbose
