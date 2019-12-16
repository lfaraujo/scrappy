from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Instancia do servico para chamadas REST
app = Flask(__name__)

# Variaveis para acesso ao processo de consulta - TJPB
url_tjpb = "https://pje.tjpb.jus.br/pje/ConsultaPublica/listView.seam"
id_input_tjpb = "fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso"
id_button_tjpb = "fPP:searchProcessos"


# Headless browser para navegacao sem abertura de interface
def instanciar_navegador(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    return driver


# Consulta de processo atraves da automacao
@app.route("/consultarProcesso/<processo>", methods=["GET"])
def consultar_processo(processo):
    driver = instanciar_navegador(url_tjpb)

    # Buscando o input do form e preenchendo com o numero do processo
    input_form = driver.find_element_by_name(id_input_tjpb)
    input_form.send_keys(processo)

    # Buscando o button para submissao do form e clicando
    button_form = driver.find_element_by_id(id_button_tjpb)
    button_form.click()

    print(driver.current_url)

    driver.quit()

    return "ok", 200


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5001)
