from .vector_db import get_index

index = get_index()
query_engine = index.as_query_engine(similarity_top_k=1)
