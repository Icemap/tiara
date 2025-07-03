# Use the official Python image as the base image
FROM python:3.11

RUN pip install poetry

# Set the working directory to /app
WORKDIR /app

# Copy the poetry.lock and pyproject.toml files
COPY poetry.lock pyproject.toml ./

# Install dependencies
RUN poetry install

# Copy the Flask application code into the container
COPY . /app

# Expose the port that the Flask app will run on
EXPOSE 5000

# Define the command to run the Flask application
CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--no-reload"]
