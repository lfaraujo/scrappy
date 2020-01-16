from flask import Flask
import requests

app = Flask(__name__)

url_consultar = "http://localhost:5001/consultarProcesso/"


@app.route("/iniciarFluxo/<processo>", methods=["GET"])
def path_consultar(processo):
    response = requests.get(url_consultar + processo)

    return response.content, response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)