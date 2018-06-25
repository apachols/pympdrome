#
# Dockerfile for mpd
#

FROM ubuntu:16.04

RUN apt-get update && apt-get install -y mpd
RUN apt-get install -y mpc

# RUN apt-get install -y pulseaudio
# COPY default.pa /etc/pulse/default.pa

COPY mpd.conf /etc/mpd.conf
COPY mpd.sh /home/mpd.sh
VOLUME /var/lib/mpd

EXPOSE 6600
CMD ["/home/mpd.sh"]
