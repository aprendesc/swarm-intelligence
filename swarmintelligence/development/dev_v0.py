import os
from openai import AzureOpenAI
from eigenlib.utils.project_setup import ProjectSetupClass
ProjectSetupClass(project_folder='swarm-automations', test_environ=True)
################################################################################################################
client = AzureOpenAI(azure_endpoint=os.environ['OAI_SUBS_1'], api_key=os.environ['OAI_API_KEY_1'], api_version=os.environ['OAI_API_VERSION_1'])
user_prompt = "Que modelo eres?"
history = [{'role': 'user', 'content': user_prompt}]
answer = client.chat.completions.create(model="gpt-5", messages=history).choices[0].message.content
print(answer)