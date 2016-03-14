FROM python:3-onbuild
EXPOSE 5522 8080
CMD [ "python", "./Backend/src/main.py" ]
