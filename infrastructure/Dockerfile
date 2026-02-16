# Use a lightweight Python base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# 1. Install Dependencies first (Caching layer)
# We copy the requirements file from the host's backend folder
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
RUN pip install python-dotenv

# 2. Copy the Application Code
# We copy the 'backend' folder
COPY backend /app/backend
# We copy the 'frontend' folder (so Flask can find the HTML/CSS)
COPY frontend /app/frontend
# We copy the 'hardware-node' folder (for shared modules if needed)
COPY hardware-node /app/hardware-node

# 3. Network & Environment
ENV PYTHONPATH=/app
ENV FLASK_APP=backend.app
EXPOSE 5000

# 4. The Launch Command
# We use the module flag (-m) to ensure imports work correctly
CMD ["python", "-m", "backend.app"]