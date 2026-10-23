# Google Colab (development/testing only)
In a Colab notebook: clone/copy this folder, `!pip install -r requirements.txt`,
`!apt-get install -y ffmpeg`, set env vars in the notebook (never commit keys),
run `!python -m backend.run` in a background cell and use the Colab proxy URL.
Sessions stop when Colab disconnects, so scheduled automation (10 AM / 10 PM
Masai checks, daily emails) requires persistent hosting — see DEPLOYMENT.md.
