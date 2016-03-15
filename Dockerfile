FROM python:3.4.4-onbuild
EXPOSE 5522 8080
ENTRYPOINT [ "python", "./Backend/src/main.py" ]
