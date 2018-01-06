
default: pip-requirements test-assets

create-venv:
	python3 -m venv .venv

pip-requirements: create-venv
	.venv/bin/pip3 requirements.txt

test-assets:
	# Grab ALL of the samples from the ffmpeg site.
	cd tests/assets
	wget --no-clobber https://vjs.zencdn.net/v/oceans.mp4
