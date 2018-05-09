# Zotero Translation Server

```bash
git clone --recursive https://github.com/zotero/translation-server
cd translation-server
sudo docker build -t translation-server .
sudo docker run -p 1969:1969 -ti --rm translation-server
```

```bash
sudo apt install docker.io
sudo docker pull zotero/translation-server
sudo docker run --rm -p 1969:1969 zotero/translation-server
```

# PRAW
The current version of [PRAW][] has a bug that limits the number of submissions to 100. I have fixed the error on [my fork][]. After I follow the proper pull procedure, I hope the devs will include my changes in the next release. Until then, you can build the dev version yourself:

```bash
git clone https://github.com/ekdunn/praw.git
cd praw
python setup.py install
```


<!--links-->
[PRAW]: https://github.com/praw-dev/praw/
[my fork]: https://github.com/ekdunn/praw.git
