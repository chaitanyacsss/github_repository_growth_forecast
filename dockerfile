FROM python:3

ADD services.py /

ADD requirements.txt /

RUN pip install --trusted-host pypi.python.org -r requirements.txt

CMD [ "python", "./services.py" ]