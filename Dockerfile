FROM python:3.9.7

WORKDIR /app

COPY . .

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0
RUN apt-add-repository https://cli.github.com/packages
RUN apt update
RUN apt intall gh
RUN echo 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 > gh_token
RUN gh auth login --with-token < gh_token
# INSTALL poetry 0.12.11

RUN . ./scripts/refresh.sh init

CMD python3 src/server.py
