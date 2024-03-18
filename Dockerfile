FROM python:3.11
ADD main.py .
ADD Pipfile .
ADD Pipfile.lock .
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile
CMD ["pipenv", "run", "python", "-u", "./main.py"] 