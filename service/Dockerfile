FROM python:3.12-alpine
WORKDIR /service
# Install pipenv
RUN pip install --no-cache-dir pipenv
COPY . .
# Install dependencies using pipenv
RUN pipenv install --deploy --ignore-pipfile
CMD ["pipenv", "run", "python", "main.py"]