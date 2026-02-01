FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Expose port 8505 to the host
EXPOSE 8505

CMD ["streamlit", "run", "__init__.py", "--server.port=8505"]
