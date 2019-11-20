from subprocess import PIPE, Popen

from flask import Flask, render_template, request
from flask_cors import cross_origin
from werkzeug.datastructures import FileStorage

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf'}
DO_NOT_PRINT = False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def print_view():
    return render_template('printsender.html')


@app.route('/print', methods=['POST'])
@cross_origin(headers=['Content-Type'])
def print_job():
    if 'file' not in request.files:
        return "false"
    file: FileStorage = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename

    if file.filename == '':
        return "false"
    if file and allowed_file(file.filename):
        # Create print process

        if DO_NOT_PRINT:
            print(file.stream.read())
            return "true"

        print_process = Popen('lp', stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)

        # Send file to print process via stdin
        while block := file.stream.read(1024):
            print_process.stdin.write(block)

        stdout, stderr = print_process.communicate()

        # Check of print process is happy
        exitcode = print_process.wait()

        if exitcode != 0:
            print(f'{exitcode}: {stderr.decode()}')
            return "false"

        return "true"


if __name__ == '__main__':
    app.run()
