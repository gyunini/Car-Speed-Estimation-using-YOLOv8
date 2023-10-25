from flask import Flask, render_template
import json

app = Flask(__name__)

# 저장된 데이터를 불러오는 함수
def load_data():
    try:
        with open('lat_long_data.json', 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}


@app.route('/')
def index():
    # 데이터 불러오기
    data = load_data()
    return render_template('index.html', lat_long_data=data)

if __name__ == '__main__':
    app.run()