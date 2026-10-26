FROM python:3.11-slim
WORKDIR /app
COPY . /app
EXPOSE 8080
ENV PORT=8080
CMD ["python3", "server.py", "8080"]
