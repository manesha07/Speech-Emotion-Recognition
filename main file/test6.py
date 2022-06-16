import json

from flask import request

from flask import Flask, render_template

test1 = Flask(__name__)

@test1.route('/')
def index():
    return render_template('index.html')

@test1.route('/test1', methods=['POST'])
def test():
    output = request.get_json()
    print(output) # This is the output that was stored in the JSON within the browser
    result = json.loads(output) #this converts the json output to a python dictionary
    return result

if __name__ == "__main__":
    test1.run(debug=True)
