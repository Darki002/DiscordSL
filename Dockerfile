# ---- Stage 1: Builder ----
FROM python:3.12-slim as builder

WORKDIR /app

# Copy only requirements to leverage Docker cache
COPY requirements.txt .

# Create a virtual environment and install dependencies
RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of your application code (including .venv will be part of /app)
COPY . .

# ---- Stage 2: Runner ----
FROM python:3.12-slim

WORKDIR /app

# Copy everything from builder stage, including the .venv folder
COPY --from=builder /app /app

# Use the virtual environment's binaries
ENV PATH="/app/.venv/bin:$PATH"

# Start the application using main.py
CMD ["python", "main.py"]
