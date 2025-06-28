FROM python:3.12-alpine3.19

LABEL authors="zaheed"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install required system packages including SQLite and build tools
RUN apk update && \
    apk add --no-cache sqlite sqlite-dev gcc musl-dev libffi-dev

# Install Poetry globally and disable virtualenv creation
RUN pip install poetry && \
    poetry config virtualenvs.create false

# Copy dependency files first to cache layer
COPY pyproject.toml poetry.lock* /app/

# Install dependencies without dev dependencies and avoid installing the package itself
RUN poetry install --without dev --no-root

# Copy the entire app after dependencies are installed
COPY . .

# Expose Django default port
EXPOSE 8000

# Create a non-root user
RUN addgroup appgroup && adduser -S appuser -G appgroup

USER appuser

# Run the Django development server
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]
