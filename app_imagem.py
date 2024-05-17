import boto3
import json
import os
from dotenv import load_dotenv
import botocore.config
import base64
import streamlit as st

# loar the environment variables 
load_dotenv()

# Configure AWS boto3 section
boto3.setup_default_session(profile_name=os.getenv("profile_name"))
config = botocore.config.Config(connect_timeout=120, read_timeout=120)
bedrock = boto3.client('bedrock-runtime', 'us-east-1', endpoint_url='https://bedrock-runtime.us-east-1.amazonaws.com', config=config)

def main():
    # aplication title
    st.title(f""":rainbow[Interface de Extração de Informações de Imagem Utilizando o Bedrock]""")

    # upload file 
    st.header('Envie uma ou mais imagens:')
    files = st.file_uploader('Envie as imagens', type=["JPG", "JPEG", "PNG", "GIF", "BMP"], accept_multiple_files=True, key="new")
    
    # prompt insert sesion
    prompt = st.text_input("Digite o prompt:")
    
    if files is not None:
        if st.button("Obter Resposta"):
            # create a list
            imagens = []
            # run for the files in files variable
            for file in files:
                # tranform file in base64
                image_base64 = base64.b64encode(file.read()).decode("utf-8")
                # create a dictionary
                imagem = {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                # add dictionary to the list
                imagens.append(imagem)
            # invoke bedrock model
            content = imagens
            content.append({
                        "type": "text",
                        "text": prompt
                    })
            response = invoke_bedrock_model(content)
            
            # show the answar
            st.write(f"Resposta do modelo:")
            st.write(response)


def invoke_bedrock_model(content):
    """
    Invoca o modelo Claude 3 Haiku no Bedrock com a imagem e o prompt.
    
    Args:
        image_base64 (str): A representação em base64 da imagem.
        prompt (str): O prompt a ser enviado para o modelo.
    
    Returns:
        str: A resposta gerada pelo modelo.
    """
    # create the body of solicitation
    prompt = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }

    # tranform the prompt in json
    json_prompt = json.dumps(prompt)

    # invoke the bedrock model
    response = bedrock.invoke_model(body=json_prompt, modelId="anthropic.claude-3-haiku-20240307-v1:0",
                                    accept="application/json", contentType="application/json")

    # get the answer of model
    response_body = json.loads(response.get('body').read())
    answer = response_body['content'][0]['text']

    return answer

if __name__ == "__main__":
    main()