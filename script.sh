# #!/bin/sh  
# python3 Audio/recording.py; python3 nvidia/transcribe_speech.py model_path=nvidia/stt_en_conformer_ctc_medium.nemo pretrained_name="stt_en_conformer_ctc_medium" cuda=-1 audio_dir=Assets/ output_filename="out.json" batch_size=128; mpv Assets/recorded.wav

while true
do
	echo "Press [CTRL+C] to stop.."
	sleep 1
done