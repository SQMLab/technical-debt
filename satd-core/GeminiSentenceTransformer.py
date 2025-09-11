import ast
from util import sha1
import pandas as pd
import numpy as np
import google.generativeai as genai
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.api_core.exceptions


@retry(
    stop=stop_after_attempt(10),  # Stop after 5 retries
    wait=wait_exponential(multiplier=2, min=60, max=2 * 60),
    retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted))
def create_embedding(uri, text):
    return genai.embed_content(
        model=uri,
        content=text,
        task_type="classification")


class GeminiSentenceTransformer:
    def __init__(self, uri: str, use_cache=False):
        self.uri = uri
        self.use_cache = use_cache
        self.file = f'./cache/{uri.split("/")[-1]}.csv'
        if not os.path.exists(self.file):
            with open(self.file, "w") as file:
                file.write("text,hash,embedding")
                file.flush()
        self.cache_df = pd.read_csv(self.file)
        self.encoding_map = {r['hash']: np.array(ast.literal_eval(r['embedding']), dtype=np.float32) for row_index, r in
                             self.cache_df.iterrows()}
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def encode(self, features):
        encoded_features = []
        rows = []
        try:
            for text in features:
                if self.use_cache:
                    hash = sha1(text)
                    # embedding_df = self.cache_df[self.cache_df['hash'] == hash]['embedding']
                    if hash not in self.encoding_map:
                        # if embedding_df.empty:
                        response = create_embedding(self.uri, text)
                        embedding_value = response["embedding"]
                        rows.append([text, hash, embedding_value])
                        # self.cache_df.loc[len(self.cache_df)] = [text, hash, embedding_value]
                        # self.cache_df.to_csv(self.file, index=False)
                        # self.cache_df = pd.read_csv(self.file)
                        self.encoding_map[hash] = np.array(embedding_value)
                    encoded_features.append(self.encoding_map[hash])

                    # else:
                    # encoded_features.append(np.array(ast.literal_eval(embedding_df.iloc[0]), dtype=np.float32))
                else:
                    raise Exception('Not Implemented Yet')
        except Exception as e:
            raise e
        finally:
            self.checkpoint(rows)
        return encoded_features

    def checkpoint(self, rows):
        if len(rows) > 0:
            new_df = pd.DataFrame(rows, columns=self.cache_df.columns)
            pd.concat([self.cache_df, new_df]).to_csv(self.file, index=False)
            self.cache_df = pd.read_csv(self.file)
