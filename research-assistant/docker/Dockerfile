# Stage 1: Build the React frontend
FROM node:18-alpine as builder
WORKDIR /app/frontend
COPY research-assistant-ui/package*.json ./
RUN npm install
COPY research-assistant-ui/. .
RUN npm run build

# Stage 2: Build the FastAPI backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Copy the built frontend to the static directory
COPY --from=builder /app/frontend/build /app/static

EXPOSE 8000
CMD ["uvicorn", "app.main_enhanced:app", "--host", "0.0.0.0", "--port", "8000"]