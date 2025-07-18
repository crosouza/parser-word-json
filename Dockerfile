# Use the official Python image.
FROM python:3.12-slim

# Set the working directory.
WORKDIR /app

# Copy the requirements file.
COPY requirements.txt .

# Install the dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY parser/ /app/parser/

# Set the entrypoint.
ENTRYPOINT ["python", "-m", "parser.cli"]
