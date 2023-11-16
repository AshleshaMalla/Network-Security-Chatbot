# pip -q install langchain openai tiktoken chromadb pypdf sentence_transformers InstructorEmbedding faiss-cpu gpt4all
# venv\Scripts\activate

from langchain.chains import RetrievalQA
from langchain.llms import GPT4All

# embedding
import pickle
import textwrap

def load_embeddings(sotre_name, path):
    with open(f"{path}/faiss_{sotre_name}.pkl", "rb") as f:
        VectorStore = pickle.load(f)
    return VectorStore


def wrap_text_preserve_newlines(text, width=110):
    # Split the input text into lines based on newline characters
    lines = text.split("\n")

    # Wrap each line individually
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]

    # Join the wrapped lines back together using newline characters
    wrapped_text = "\n".join(wrapped_lines)

    return wrapped_text


def process_llm_response(llm_response):
    print(wrap_text_preserve_newlines(llm_response["result"]))
    print("\nSources:")
    for source in llm_response["source_documents"]:
        print(source.metadata["source"])
        if "page" in source.metadata:
            print("Page: ", source.metadata["page"])


Embedding_store_path = "./Embedding_store"
db_instructEmbedd = load_embeddings(
    sotre_name="instructEmbeddings", path=Embedding_store_path
)
retriever = db_instructEmbedd.as_retriever(search_kwargs={"k": 5})

# create the chain to answer questions
# qa_chain_instrucEmbed = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0.2, ),
#                                   chain_type="stuff",
#                                   retriever=retriever,
#                                   return_source_documents=True)
# callbacks = [StreamingStdOutCallbackHandler()]
local_path = "./models/nous-hermes-llama2-13b.Q4_0.gguf"

qa_chain = RetrievalQA.from_chain_type(
    llm=GPT4All(model=local_path, backend="gptj"),
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
)

## Answer with source

print("-------------------Q/A------------------\n")
query = input("Please enter your question: ")
print("Question: ", query)
llm_response = qa_chain(query)
# print("All response: ", llm_response)
process_llm_response(llm_response)