import io
import os
from flask import Flask, send_file
from flask import make_response
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
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
id_table_docs = "j_id132:processoDocumentoGridTab:tb"
id_button_pdf = "j_id40:downloadPDF"

# Diretorio de arquivos
diretorio_docs = "C:\\Users\\felli\\Documents"


# Consulta de processo atraves da automacao
@app.route("/consultarProcesso/<processo>", methods=["GET"])
def consultar_processo(processo):
    try:
        driver = instanciar_navegador(url_tjpb)

        # Buscando o input do form e preenchendo com o numero do processo
        input_form = driver.find_element_by_name(id_input_tjpb)
        input_form.send_keys(processo)

        # Buscando o button para submissao do form e clicando
        button_form = driver.find_element_by_id(id_button_tjpb)
        button_form.click()

        # Obtendo documentos atrelados ao processo
        documentos = obter_docs_processo(driver, processo)

        return documentos

        # if documentos[1] == 200:
        #     return "Consulta finalizada (servico)", 200
        # else:
        #     return documentos
    except UnexpectedAlertPresentException as ua:
        return ua.alert_text, 500


# Headless browser para navegacao sem abertura de interface
def instanciar_navegador(url):
    profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
               "download.default_directory": diretorio_docs, "download.prompt_for_download": False}
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    return driver


# Baixa documentos contidos na tabela
def efetuar_download_docs(tabela_documentos, driver, processo):
    # Identifica o botao do documento, acessa a tela, efetua download e volta a pagina
    for aux in range(len(tabela_documentos)):
        button_doc = driver.find_element_by_id("j_id132:processoDocumentoGridTab:%i:j_id531:idView" % aux)
        button_doc.click()

        driver.switch_to.window(driver.window_handles[-1])

        gerar_pdf = WebDriverWait(driver, 5).until(ec.presence_of_element_located(
            (By.ID, id_button_pdf)))
        gerar_pdf.click()

        driver.switch_to.window(driver.window_handles[1])

    return organizar_docs_retorno(processo)


# Organiza documentos para retornar pdf e apagar do disco
def organizar_docs_retorno(processo):
    docs = []
    pdf = ""

    for r, d, f in os.walk(diretorio_docs):
        for file in f:
            if processo[0:7] in file:
                # docs.append(os.path.join(r, file))
                pdf = open(os.path.join(r, file), 'rb')
                return send_file(pdf, mimetype='application/pdf', as_attachment=True,
                                 attachment_filename=file)

    # for f in docs:
    # print(f.split("\\")[4])


# Obtem acesso a pagina que contem a tabela dos documentos atrelados ao processo
def obter_docs_processo(driver, processo):
    try:
        table_tjpb = WebDriverWait(driver, 5).until(ec.presence_of_element_located(
            (By.XPATH, '//*[@id="fPP:processosTable:tb"]/tr')))

        button_detalhes = table_tjpb.find_element_by_css_selector("[title^='Ver Detalhes']")
        button_detalhes.click()

        driver.switch_to.window(driver.window_handles[-1])

        table_docs = WebDriverWait(driver, 5).until(ec.presence_of_all_elements_located(
            (By.XPATH, '//*[@id="j_id132:processoDocumentoGridTab:tb"]/tr')))

        return efetuar_download_docs(table_docs, driver, processo)

        # return "Finalizado"
    except TimeoutException:
        return "A busca pelo elemento levou muito tempo e não obteve retorno.", 504
    except NoSuchElementException:
        return "Não foi possível identificar o elemento na página.", 500
    except IndexError:
        return "Não foi possível obter a lista de processos.", 500
    except UnexpectedAlertPresentException as ua:
        return ua.alert_text, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
