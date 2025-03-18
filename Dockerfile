FROM python:3.9

# Set working directory inside the container
WORKDIR /app

# Copy dependency file first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files after installing dependencies
COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "evaluateWritingModule:app"]

