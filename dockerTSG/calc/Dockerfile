#Dockerfile to Create an Ubuntu environment to run my Python Code
FROM python:latest

LABEL maintainer="bolajiagunbiade1@gmail.com"

#Make the /app Directory where the Calculator Code will run from
RUN mkdir /app

#Get the code from Github to the /app Direcory
ADD https://raw.githubusercontent.com/ibrolord/python/python/Calc.py /app

#Set the /app Directory as the Working Directory
WORKDIR /app

#Launch the Calculator App as an Executable within Docker
ENTRYPOINT [ "python3", "./Calc.py" ]


