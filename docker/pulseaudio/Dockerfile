#
# Dockerfile for pulseaudio
#

FROM debian:sid

RUN apt-get update && apt-get install -y \
	alsa-utils \
	libasound2 \
	libasound2-plugins \
	pulseaudio \
	pulseaudio-utils \
	mpd mpc \
	python-pip python-dev build-essential python-setuptools \
	--no-install-recommends \
	&& rm -rf /var/lib/apt/lists/*

ARG color

ENV HOME /home/$color
RUN useradd --create-home --home-dir $HOME pulseaudio \
	&& usermod -aG audio,pulse,pulse-access pulseaudio \
	&& chown -R pulseaudio:pulseaudio $HOME

COPY mpd.conf /etc/mpd.conf

COPY requirements.txt /home/requirements.txt
RUN pip install -r /home/requirements.txt

WORKDIR $HOME
USER pulseaudio

VOLUME /var/lib/mpd

COPY default.pa /etc/pulse/default.pa
# COPY client.conf /etc/pulse/client.conf
# COPY daemon.conf /etc/pulse/daemon.conf

ENTRYPOINT [ "pulseaudio" ]
CMD [ "--log-level=4", "--log-target=stderr", "-v" ]
