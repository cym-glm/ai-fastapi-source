from app.langchain_rag.documents import load_markdown_documents
from app.langchain_rag.splitters import split_documents

def main():
    documents = load_markdown_documents()
    chunks = split_documents(documents)
    print("document counts:", len(documents))
    print("document chunks  :", len(chunks))
    print('==================')

    for chunk in chunks:
        print("metadata", chunk.metadata)
        print("content")
        print(chunk.page_content[:100])
        print('==================')

if __name__ == "__main__":
    main()
