# Install required libraries
# !pip install pathway llama-index python-dotenv openai

# Mount Google Drive for accessing files
# from google.colab import drive
# drive.mount('/content/drive')

# Set up environment variables
import os
from dotenv import load_dotenv
import logging
from pathway.xpacks.llm.parsers import ParseUnstructured
os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/4.00/tessdata"
import pathway as pw
import pathway as pw
from pathway.xpacks.llm import llms, parsers, prompts

from pathway.udfs import DiskCache, ExponentialBackoffRetryStrategy
from pathway.xpacks.llm import embedders, llms, parsers, prompts
from pathway.xpacks.llm.question_answering import BaseRAGQuestionAnswerer
from pathway.xpacks.llm.vector_store import VectorStoreServer
# parser = parsers.OpenParse()
import nltk
nltk.download('averaged_perceptron_tagger_eng')
parser = ParseUnstructured(mode="best")
print("I am here")
# Create a .env file in Colab or directly set the environment variables
os.environ['GDRIVE_LINK'] = "1-0zoV_RNPFyUXDL_n-dVHcgdmgOv_zye"  # Reduced dataset
# os.environ['GDRIVE_LINK'] = "1yt4j8b6ykFlg29NyVCbmqrfy0dxJYKqv"  # 2 files, testing client request error
os.environ['PATHWAY_HOST'] = "0.0.0.0"
os.environ['PATHWAY_PORT'] = "8788"
os.environ['OPENAI_API_KEY'] = "OPENAI_API_KEY"

# Load environment variables
load_dotenv()

import pathway as pw
from pathway.xpacks.llm.vector_store import VectorStoreServer
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import TokenTextSplitter

# Define the data source
data_sources = []
data_sources.append(
    pw.io.gdrive.read(
        object_id=os.getenv("GDRIVE_LINK"),
        service_user_credentials_file="creds.json",  # Replace with your creds.json path
        with_metadata=True,
    )

)

embedder = embedders.OpenAIEmbedder()

pipeline = VectorStoreServer(
    *data_sources,
    embedder=embedder,
      splitter=None,
        parser=parser,

)
# Run the server
pipeline.run_server(
    host=os.getenv("PATHWAY_HOST"),
    port=int(os.getenv("PATHWAY_PORT")),
    with_cache=False
)
# pipeline.run_server(
#     host=os.getenv("PATHWAY_HOST"),
#     port=int(os.getenv("PATHWAY_PORT")),
#     with_cache=True,
#     cache_backend=pw.persistence.Backend.filesystem("./Cache")
# )

# Add a delay to ensure the server is running
import time
time.sleep(30)

# If additional threaded server setup is needed, uncomment this:
# pipeline.run_server(
#     host="127.0.0.1",
#     port=8754,
#     with_cache=False,
#     threaded=True
# )
