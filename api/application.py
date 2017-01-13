import os
import io
import json
import base64
import requests
import datetime
from semantic.numbers import NumberService
import pyqrcode as QR
import speech_recognition as SR
from flask import Flask, request, jsonify, send_file
application = Flask(__name__)


@application.route('/api/parseaudio', methods=['POST'])
def api_parseaudio():
    r_engine = SR.Recognizer()
    with SR.AudioFile(request.files['recording']) as f:
        audio = r_engine.record(f)

    results = []

    with open('wit_credentials.txt', 'r') as f:
        wit_key = f.read().strip()

    try:
        results.append(r_engine.recognize_wit(audio, key=wit_key))
    except SR.UnknownValueError:
        results.append("Wit.ai could not understand audio")
    except SR.RequestError as e:
        results.append("Could not request results from Wit.ai service; {0}".format(e))

    # Was going to add more engines and take a string average for increased accuracy,
    # ran out of time.

    print('Original query: ', results[0])
    return jsonify({'amount': _extract_amount(results[0])})


@application.route('/api/qr', methods=['POST'])
def api_qr():
    data = request.get_json()
    print(data)
    amt, aid = data['amount'], data['aid']
    print('Returning encoded QR code for', amt, aid)

    QR.create(' '.join((amt, aid))).png('qr.png', scale=24)
    with open('qr.png', 'rb') as f:
        data = f.read()
    os.remove('qr.png')
    return jsonify({'QR': base64.b64encode(data).decode()})
    # return send_file(io.BytesIO(data), mimetype='image/png')


@application.route('/api/verify', methods=['POST'])
def api_verify():
    data = request.get_json()['data'].strip()
    amt, account_id = data.split()
    with open('nessie_credentials.txt', 'r') as f:
        nkey = f.read().strip()
    url = "http://api.reimaginebanking.com/accounts/{}?key={}".format(account_id, nkey)
    r = requests.get(url)
    if r.status_code == 200:
        account = r.json()
        url = "http://api.reimaginebanking.com/accounts/{}/withdrawals?key={}".format(account['_id'], nkey)
        payload = {
          "medium": "balance",
          "transaction_date": str(datetime.date.today()),
          "amount": int(amt),
          "description": "dank memes"
        }
        r = requests.post(url, json=payload)
        return jsonify(r.json())
    else:
        return 'ERROR: ' + r.json()['message']


def _extract_amount(query):
    whitelist = ['eight', 'eighteen', 'eighty', 'eleven', 'fifteen', 'fifty', 'five',
        'forty', 'four', 'fourteen', 'nine', 'nineteen', 'ninety', 'one', 'seven',
        'seventeen', 'seventy', 'six', 'sixteen', 'sixty', 'ten', 'thirteen', 'thirty',
        'three', 'twelve', 'twenty', 'two', 'zero', 'hundred', 'thousand', 'million', 'billion']
    num_strings = list(filter(lambda w: w in whitelist, query.replace('-', ' ').split()))
    try:
        return NumberService().parse(' '.join(num_strings))
    except Exception as e:
        return 'Error extracting numeric string tokens from audio string.'


if __name__ == "__main__":
    application.run(debug=True)
