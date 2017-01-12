import os
import io
import json
import base64
from semantic.numbers import NumberService
import pyqrcode as QR
import speech_recognition as SR
from flask import Flask, request, jsonify, send_file
application = Flask(__name__)

@application.route('/')
def index():
    return "o shit whaddup"


@application.route('/api/testqr', methods=['GET'])
def api_testqr():
    args = request.args
    QR.create('hello jared').png('qr.png', scale=8)
    with open('qr.png', 'rb') as f:
        data = f.read()
    os.remove('qr.png')
    return jsonify({'QR': base64.b64encode(data).decode()})
    # return send_file(io.BytesIO(data), mimetype='image/png')


@application.route('/api/qr', methods=['POST'])
def api_qr():
    r_engine = SR.Recognizer()
    with SR.AudioFile(request.files['recording']) as src:
        audio = r_engine.record(src)

    results = []

    with open('wit_credentials.txt', 'r') as f:
        wit_key = f.read().strip()

    '''
    try:
        results.append(r_engine.recognize_google_cloud(audio, credentials_json='gcs_credentials.json'))
    except SR.UnknownValueError:
        results.append("Google Cloud Speech could not understand audio")
    except SR.RequestError as e:
        results.append("Could not request results from Google Cloud Speech service; {0}".format(e))
    '''

    try:
        results.append(r_engine.recognize_wit(audio, key=wit_key))
    except SR.UnknownValueError:
        results.append("Wit.ai could not understand audio")
    except SR.RequestError as e:
        results.append("Could not request results from Wit.ai service; {0}".format(e))

    # TODO add more engines and take an average string

    print('Original query: ', results[0])
    amt = str(_extract_amount(results[0]))
    uid = request.files['uid'].read().decode()
    print('Returning encoded QR code: ', amt, uid)

    QR.create(' '.join((amt, uid))).png('qr.png', scale=8)
    with open('qr.png', 'rb') as f:
        data = f.read()
    os.remove('qr.png')
    return jsonify({'QR': base64.b64encode(data).decode()})
    # return send_file(io.BytesIO(data), mimetype='image/png')


@application.route('/api/verify', methods=['POST'])
def api_verify():
    data = request.get_json()
    return 'verify'


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
