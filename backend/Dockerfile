# Architectural Choice: Using a slim Python image reduces the attack surface and container footprint 
# while still providing the necessary C-bindings and tools needed for data science packages.
FROM python:3.12-slim

# Architectural Choice: Setting a dedicated WORKDIR keeps our container filesystem organized 
# and prevents polluting the root directory.
WORKDIR /app

# Architectural Choice: Copying requirements.txt before the rest of the source code allows Docker 
# to cache the expensive `pip install` layer, drastically speeding up subsequent builds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Default command for the background worker
CMD ["python", "sentiment_pipeline.py"]
