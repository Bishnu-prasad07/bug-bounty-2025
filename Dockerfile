FROM kalilinux/kali-rolling

WORKDIR /app
COPY . .

RUN apt update -y \
    && apt install wget -y \
    && apt install curl -y \
    && apt install iputils-ping -y \
    && apt install python3 -y \
    && apt install pip -y \
    && apt install nmap -y

RUN wget https://go.dev/dl/go1.22.1.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf go1.22.1.linux-amd64.tar.gz
RUN rm go1.22.1.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin

RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

RUN go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

ENV PATH=$PATH:/root/go/bin

RUN ln -s /root/go/bin/httpx /usr/local/bin/httpxx

RUN pip install Flask
RUN pip install flask-socketio
RUN pip install python-whois
RUN pip install python-telegram-bot

EXPOSE 5000

CMD python3 app.py