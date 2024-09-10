FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /code

# Copy project files into container
COPY . /code/

# Install pipenv
RUN pip install pipenv

# Install dependencies from Pipfile and Pipfile.lock
RUN pipenv install --deploy --ignore-pipfile

# Activate pipenv environment in the entrypoint
ENTRYPOINT ["pipenv", "run", "./entrypoint.sh"]
