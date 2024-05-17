import boto3
import json
import os
from dotenv import load_dotenv
import botocore.config
import base64
import streamlit as st
from uuid import uuid4 as uuid
import requests
from time import sleep

# Carregar variáveis de ambiente
load_dotenv()
API_URL = "https://m1ragczl27.execute-api.us-east-1.amazonaws.com"

def main():
    st.title(f""":rainbow[Interface de Extração de Informações de Imagem Utilizando o Bedrock]""")

    st.header('Envie uma ou mais imagens:')
    files = st.file_uploader('Envie as imagens', type=["PNG", "PDF"], accept_multiple_files=True, key="new")
    
    prompt = st.text_input("Digite o prompt:")
    
    if files is not None and prompt is not None:
        if st.button("Obter Resposta"):
            for file in files:
                process_id = str(uuid())
                print(f'file {file}')
                filename = file.name
                file_type = file.type
                print(f'file_type: {file_type}')
                name = filename.rpartition('.')[0]
                print(f'name: {name}')
                signed_url = get_signed_url(process_id, filename, file_type, name)
                upload_file(signed_url[name], file, file_type)
                key = signed_url[name]["key"]
                start_process(prompt, key, process_id)
                interval_get_process(process_id)

def get_signed_url(process_id, file_name, file_type, name):
    payload = {
        "process_id": process_id,
        "files": [
            {
                "name": name,
                "type": file_type,
                "filename": file_name
            }
        ]
    }
    response = requests.post(API_URL + "/dev/signed-url", json=payload)
    response_body = response.json()
    return response_body

def upload_file(signed_url, file, type):
    try:
        url = signed_url["url"]  # Alterado para acessar a URL do arquivo específico
        with file as f:  # Use o arquivo fornecido diretamente
            files = {"file": f}
            headers = {"Content-Type": type}  # Adicionando o cabeçalho Content-Type
            response = requests.put(url, files=files, headers=headers)
        return response
    except Exception as e:
        return f"Erro ao fazer upload do arquivo: {e}"

def start_process(prompt, key, process_id):
    payload = {
        "process_id": process_id,
        "source_pdf_key": key,
        "operation": "textract",
        "webhook_url": "https://webhook-test.com/d53e84f440670f8f4840a6f49883a664",
        "prompt": prompt
    }
    response = requests.post(API_URL + "/dev/process", json=payload)
    return response

def interval_get_process(process_id):
    while True:
        response = requests.get(API_URL + f"/dev/get-response/{process_id}")
        print(response)
        print(process_id)
        if response.status_code != 200:
            print("Erro na requisição")
            sleep(5)
        else:
            print("Requisição bem-sucedida")
            data = response.json()
            if "error" in data:
                print("Erro no processamento")
                sleep(5)
            else:
                print("Processamento concluído com sucesso")
                print(data["textractPayload"])
                st.write(data["textractPayload"])
                break
    
if __name__ == "__main__":
    main()
