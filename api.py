from flask import Flask, request, send_from_directory, redirect, url_for, render_template

import interestingizer
from PIL import Image

import md5
import random
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #16Mb upload file limit

TMP_DIR = "./tmp"
ITEMS_BASE = "./images/"
items = [Image.open(os.path.join(ITEMS_BASE, filename)).convert("RGBA") for filename in os.listdir(ITEMS_BASE)]


@app.route("/ping")
def ping():
    return "OK"


def cache_image(pil_img):
    global TMP_DIR
    key = md5.md5(pil_img.tostring()).hexdigest()
    with open(os.path.join(TMP_DIR, key), "w+") as fd:
        pil_img.save(fd, 'JPEG', quality=70)
    return key


@app.route("/cache/<key>")
def cache(key):
    global TMP_DIR
    return send_from_directory(TMP_DIR, key, mimetype='image/jpeg')


@app.route("/test")
def test_form():
    return render_template("simple_form.html")


@app.route("/interestingize", methods=["POST",])
def interestingize():
    image_raw = request.files.get("image")
    if image_raw:
        try:
            image = Image.open(image_raw)
        except IOError:
            return "Could not decode image", 500

        item = random.choice(items).copy()
        try:
            better_image = interestingizer.interestingize(image, item)
        except Exception, e:
            print "Could not run interestingize algorithm: %s" % e
            return "Could not interestingize", 500

        key = cache_image(better_image)
        return redirect(url_for('cache', key=key))
    else:
        return "Must provide image in form field 'image'", 500


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
