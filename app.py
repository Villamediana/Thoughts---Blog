from flask import Flask, render_template, request, redirect, url_for
import json
import os
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')


if __name__ == "__main__":
    app.run()