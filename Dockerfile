# Use a specific version of the Python slim image
FROM python:3.12.4-slim

# Set the working directory
WORKDIR /app

# Create a non-root user
RUN useradd --create-home --uid 1000 appuser
USER appuser

# Copy only necessary files
COPY --chown=appuser:appuser requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the application code
COPY --chown=appuser:appuser parser/ /app/parser/

# Expose the server port
EXPOSE 5000

# Set the entrypoint
ENTRYPOINT ["python", "-m", "parser.cli"]
