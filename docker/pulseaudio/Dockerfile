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
	--no-install-recommends \
	&& rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y mpd
RUN apt-get install -y mpc

ENV HOME /home/pulseaudio
RUN useradd --create-home --home-dir $HOME pulseaudio \
	&& usermod -aG audio,pulse,pulse-access pulseaudio \
	&& chown -R pulseaudio:pulseaudio $HOME


# RUN mkdir /home/.mpd
# RUN usermod -aG audio,pulse,pulse-access mpd \
#     && chown -R mpd /home/.mpd
# USER mpd

COPY mpd.conf /etc/mpd.conf

# RUN mpd --stdout

WORKDIR $HOME
USER pulseaudio

VOLUME /var/lib/mpd

COPY default.pa /etc/pulse/default.pa
# COPY client.conf /etc/pulse/client.conf
# COPY daemon.conf /etc/pulse/daemon.conf

ENTRYPOINT [ "pulseaudio" ]
CMD [ "--log-level=4", "--log-target=stderr", "-v" ]
