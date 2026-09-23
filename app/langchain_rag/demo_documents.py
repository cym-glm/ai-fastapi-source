
from app.langchain_rag.documents import (
    load_markdown_documents,
    print_documents
)

def main():
    documents = load_markdown_documents()
    print(f"Loaded {len(documents)} documents")
    print_documents(documents)

if __name__ == "__main__":
    main()