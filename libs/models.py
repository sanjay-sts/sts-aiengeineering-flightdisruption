
import asyncio
import os
from libs.errors import UnknownProviderError
from langchain.chat_models import init_chat_model, BaseChatModel

from dotenv import load_dotenv

load_dotenv()

MODEL_DETAIL = os.environ["MODEL_DEFAULT"]

def get_model(model_detail: str) -> BaseChatModel:
    provider ,sep,  model = model_detail.partition(":")

    if not sep: raise UnknownProviderError(f"model detail '{model_detail}' is not in the expected format 'provider:model'")
    if provider == 'bedrock':
        langchain_provider = "bedrock_converse"
    elif provider == 'ollama':
        langchain_provider = "ollama"
    else:
        raise UnknownProviderError(f"unknown provider '{provider}'")
    return init_chat_model(model_provider=langchain_provider, model=model)





async def main():
    results = await get_model(MODEL_DETAIL).ainvoke("One sentence about Calgary weather.")
    print(results)
    print(results.content)


if __name__ == "__main__":
    asyncio.run(main())
