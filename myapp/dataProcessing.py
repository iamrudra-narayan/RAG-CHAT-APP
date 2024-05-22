from pypdf import PdfReader
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .retrieval import get_embeddings, index
from langchain_core.documents.base import Document


def text_splitter(pdf_file):
    documents = []
    try:
        reader = PdfReader(pdf_file)
        print(len(reader.pages))
        for i in range(len(reader.pages)):
            pages = reader.pages[i]
            documents.append(Document(page_content= pages.extract_text(), metadata = {'page':i, 'source':pdf_file.filename}))

        print(documents[0])    
        
        recursive_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=["\n\n", "\n", " ", ""],
        )
        
        return recursive_text_splitter.split_documents(documents)
    except Exception as e:
        print(e)
        return None     
    
def data_preparation_and_upload(pdf_file, namespace):
    prepped_data = []
    try:
        rec_docs = text_splitter(pdf_file)
        for i in range(len(rec_docs)):
            embeddings = get_embeddings(rec_docs[i].page_content)
            prepped_data.append({'id':str(i), 
                            'values':embeddings.data[0].embedding,     
                            'metadata':{"doc":rec_docs[i].page_content, "page":rec_docs[i].metadata['page'], "source":rec_docs[i].metadata['source']}})
        if len(prepped_data) >= 1:
            index.upsert(prepped_data, namespace=namespace)
            print("Upload Done!") 

        return index.describe_index_stats()    
    except Exception as e:
        print(e)
        return None
