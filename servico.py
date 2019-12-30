from flask import Flask
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# Instancia do servico para chamadas REST
app = Flask(__name__)

# Variaveis para acesso ao processo de consulta - TJPB
url_tjpb = "https://pje.tjpb.jus.br/pje/ConsultaPublica/listView.seam"
id_input_tjpb = "fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso"
id_button_tjpb = "fPP:searchProcessos"
id_table_tjpb = "fPP:processosTable:662540:j_id216"
id_table_docs = "j_id132:processoDocumentoGridTab:tb"
id_button_doc = "j_id132:processoDocumentoGridTab:0:j_id567:j_id569:j_id571"


# driver.switch_to_default_content() - Retornar para a pág principal
# driver.switch_to_window(window_name) - Alternar para pop up window


# Headless browser para navegacao sem abertura de interface
def instanciar_navegador(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    return driver


def obter_docs_processo(driver):
    try:
        print("Página atual: ", driver.title)

        table_tjpb = WebDriverWait(driver, 5).until(ec.presence_of_element_located(
            (By.ID, id_table_tjpb)))

        button_popup = table_tjpb.find_element_by_css_selector("[title^='Ver Detalhes']")
        button_popup.click()

        # Alterando para a janela mais recente
        driver.switch_to.window(driver.window_handles[-1])
        print("Página atual: ", driver.title)

        button_doc = WebDriverWait(driver, 5).until(ec.presence_of_element_located(
            (By.ID, id_button_doc)))
        button_doc.click()

        driver.switch_to.window(driver.window_handles[-1])

        return "Ok."
    except TimeoutException:
        return "Não foi possível identificar o elemento."


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

    dados = obter_docs_processo(driver)

    # print(driver.current_url)

    return "Página atual: %s" % driver.title, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
