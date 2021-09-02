FROM python:3

LABEL maintainer="Kayla Iacovino: kaylaiacovino@gmail.com"

RUN apt-get update
RUN apt-get install -y build-essential libgtk-3-dev
RUN pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/debian-9 wxPython
RUN pip install ftir-background-subtract

# Make sure the contents of our repo are in ${HOME}
# COPY . ${HOME}
# USER root
# RUN chown -R ${NB_UID} ${HOME}
# RUN pip install --no-cache-dir appmode
# RUN pip install --no-cache-dir ftir-background-subtract
# RUN jupyter nbextension enable --py --sys-prefix appmode
# RUN jupyter serverextension enable --py --sys-prefix appmode
# USER ${NB_USER}

# create a user called 1000 (binder cannot run as root)
# ARG NB_USER=jovyan
# ARG NB_UID=1000
# ENV USER ${NB_USER}
# ENV NB_UID ${NB_UID}
# ENV HOME /home/${NB_USER}

# RUN adduser --disabled-password \
#     --gecos "Default user" \
#     --uid ${NB_UID} \
#     ${NB_USER}