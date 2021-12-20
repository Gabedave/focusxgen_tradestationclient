FROM python:3.8-slim-buster
RUN mkdir /app
COPY pyproject.toml /app 
WORKDIR /app
COPY requirements.txt requirements.txt
ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
RUN apt-get update && apt-get install -y git
RUN pip install -r requirements.txt
COPY . .
EXPOSE 3000
CMD ["poetry", "run", "./run.sh"]