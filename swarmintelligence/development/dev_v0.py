import os
from openai import AzureOpenAI
from eigenlib.utils.project_setup import ProjectSetupClass
ProjectSetupClass(project_folder='swarm-intelligence', test_environ=True)
################################################################################################################
client = AzureOpenAI(azure_endpoint=os.environ['OAI_SUBS_2'], api_key=os.environ['OAI_API_KEY_2'], api_version=os.environ['OAI_API_VERSION_2'])
user_prompt = "Que modelo eres?"
history = [{'role': 'user', 'content': user_prompt}]
answer = client.chat.completions.create(model="o3", reasoning_effort='high', messages=history).choices[0].message.content
print(answer)

