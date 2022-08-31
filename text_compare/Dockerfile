FROM python:3 
WORKDIR /usr/src/app2
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install ./en_core_web_sm-3.3.0.tar.gz
CMD ["python", "app.py"]