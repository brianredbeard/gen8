FROM python:3.7-alpine
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["waitress-serve", "--call", "gen8:create_app"]
