from flask import Flask, render_template, request, send_file, jsonify
from scraper import run_scraper
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    username = data.get('target_user')
    gender_filter = data.get('gender_filter')  # 'male', 'female', or 'all'

    results = run_scraper(username, gender_filter)

    return jsonify(results)

@app.route('/download')
def download():
    path = 'output.csv'
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
