FROM python:3.9

# Set working directory inside the container
WORKDIR /app

# Copy dependency file first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files after installing dependencies
COPY . .

# Expose port 5000 for web applications
EXPOSE 5000

# Run the Python script
CMD ["python", "evaluateWritingModule.py"]
