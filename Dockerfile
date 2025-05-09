FROM python

RUN apt-get update && apt-get install -y locales
RUN sed -i '/ru_RU/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG ru_RU
ENV LC_ALL ru_RU

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "alembic upgrade head && python main.py"]