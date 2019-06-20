# tgrss

Plug-and-play Telegram Channels to RSS - Without Telegram Account or API keys  
It scrape telegram channels just-in-time from the [Channel public web interface](https://telegram.org/blog/privacy-discussions-web-bots) (Telegram's 2019-05-31 update)

## Usage

- `git clone` the repo then `cd` into it

```

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py

```

- In your favorite RSS reader, add telegram channels as a new feed : http://localhost:1234/tgrss/*channel_handle*, as http://localhost:1234/tgrss/telegram for https://t.me/telegram

### Notes

- Telegram seems to ban some channels from the web interface, maybe because of some copyrights legal thing ّ🙄

- You may use this software as a public service (i.e: on a VPS). Using this software as a public service may lead to get your public IP banned by Telegram if they found that number of requests is abusive, especially if you do not use a cache proxy server like nginx or varnish. Some files in `examples/` directory may be useful in this case.  

- This Software was only tested on Linux, if it works on your Windows / Mac, please tell me.

### Liked it?

I do not accept donations (yet?), but I will appreciate any nice words received on noureddinex(at)protonmail(dot)com  

