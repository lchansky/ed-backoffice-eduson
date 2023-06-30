FROM python:3.10

RUN apt update -y && apt upgrade -y
RUN apt install -y apt-transport-https
RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install 'poetry==1.5.0'
COPY poetry.lock pyproject.toml /proj/
WORKDIR /proj
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

COPY . /proj/
WORKDIR /proj/src

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]
