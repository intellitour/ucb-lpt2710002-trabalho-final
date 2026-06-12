FROM ubuntu:26.04

ENV DEBIAN_FRONTEND=noninteractive

ENV STREAMLIT_SERVER_ENABLE_CORS=true
ENV STREAMLIT_SERVER_CORS_ALLOWED_ORIGINS="*"
ENV STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false

ENV TZ=America/Sao_Paulo

ENV LANG=pt_BR.UTF-8
ENV LANGUAGE=pt_BR.UTF-8
ENV LC_CTYPE="pt_BR.UTF-8"
ENV LC_NUMERIC="pt_BR.UTF-8"
ENV LC_TIME="pt_BR.UTF-8"
ENV LC_COLLATE="pt_BR.UTF-8"
ENV LC_MONETARY="pt_BR.UTF-8"
ENV LC_MESSAGES="pt_BR.UTF-8"
ENV LC_PAPER="pt_BR.UTF-8"
ENV LC_NAME="pt_BR.UTF-8"
ENV LC_ADDRESS="pt_BR.UTF-8"
ENV LC_TELEPHONE="pt_BR.UTF-8"
ENV LC_MEASUREMENT="pt_BR.UTF-8"
ENV LC_IDENTIFICATION="pt_BR.UTF-8"
ENV LC_ALL=pt_BR.UTF-8

RUN apt-get update &&  \
    apt-get -y install locales locales-all tzdata python3 python3-pip libpython3-dev libpython3-stdlib wget

RUN apt clean && apt autoclean && apt autoremove --purge && du -sh /var/cache/apt/archives

RUN mkdir /app && cd /app
RUN wget https://bucket.getinsight.tech/public/accidents_2017_to_2023_portugues.csv

ADD streamlit_design_matplotlib.py /app

RUN pip install streamlit pandas matplotlib numpy folium seaborn streamlit-folium --break-system-packages

EXPOSE 8501

WORKDIR /app

CMD ["streamlit",  "run", "streamlit_design_matplotlib.py"]