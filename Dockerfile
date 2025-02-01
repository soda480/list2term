ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /code
COPY . /code/
RUN pip install --upgrade pip && \
    pip install pybuilder faker mock
RUN pyb -X