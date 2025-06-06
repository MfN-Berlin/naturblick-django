#!/bin/sh

show_usage() {
	echo "Usage: $0 audio_path.mp3 audio_path.wav spec_path.png" 1>&2
	exit 1
}

if [ $# -ne 3 ]; then
	show_usage
else
	mp3=$1
	wav=$2
	spec=$3

	ffmpeg -y -i $mp3 $wav && sox $wav -n remix 1 rate 22.05k spectrogram -m -r -x 700 -y 129 -o - | convert - -alpha copy -fill white -colorize 100% -gravity north -chop x10 - $spec
	rm -f $wav
fi