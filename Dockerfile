FROM python:3

WORKDIR /usr/src/app

ENV HOST=0.0.0.0
ENV PORT=8080
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE ${PORT}
COPY . .

CMD [ "python", "-m", "band"]
