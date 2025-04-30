# Last modified: 2025-03-30 12:59:33
# Version: 0.0.3
from openai import OpenAI

def buildOpenAiModelList(appVars):
    oaClient = OpenAI(api_key=appVars["api_key"])
    models = {}
    openAiModelList = []
    models = oaClient.models.list()
    for i in models.data:
        openAiModelList.append(i.id)

    appVars["openAiModelList"] = openAiModelList
    
    return openAiModelList, appVars