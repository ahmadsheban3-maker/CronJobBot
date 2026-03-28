# 1. BUILD PHASE: Use Python 3.10
FROM python:3.10-slim

# 2. SET WORKING DIRECTORY
WORKDIR /app

# 3. INSTALL SYSTEM TOOLS (Required for Hugging Face)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# 4. INSTALL REQUIREMENTS
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. COPY ALL FILES
COPY . .

# 6. START COMMAND
CMD ["python", "main.py"]
