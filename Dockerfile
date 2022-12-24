FROM python:3.8-alpine

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# install the dependencies and packages in the requirements file
RUN pip install -r /app/requirements.txt

# copy every content from the local file to the image
COPY ./app /app

WORKDIR /app/src

ENV FLASK_APP=main.py

CMD  [ "python", "-m" , "flask", "run", "--host", "0.0.0.0"]