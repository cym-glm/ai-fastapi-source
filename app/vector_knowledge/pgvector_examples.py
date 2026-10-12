"""
pgvector 示例文件。

说明：
1. 这是生产环境思路示例，不在本章默认运行。
2. 需要 PostgreSQL 安装 pgvector 扩展。
3. 需要根据真实 embedding 维度修改 vector(128)。
"""


PGVECTOR_TABLE_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(128) NOT NULL,
    document_id VARCHAR(128) NOT NULL,
    chunk_id VARCHAR(255) NOT NULL UNIQUE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding_model VARCHAR(128) NOT NULL,
    embedding_dimension INT NOT NULL,
    embedding vector(128),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
"""


PGVECTOR_SEARCH_SQL = """
SELECT
    chunk_id,
    document_id,
    content,
    metadata,
    1 - (embedding <=> %(query_embedding)s) AS score
FROM knowledge_chunks
WHERE tenant_id = %(tenant_id)s
ORDER BY embedding <=> %(query_embedding)s
LIMIT %(top_k)s;
"""


def print_pgvector_sql():
    print("建表 SQL:")
    print(PGVECTOR_TABLE_SQL)

    print("=" * 80)

    print("查询 SQL:")
    print(PGVECTOR_SEARCH_SQL)


if __name__ == "__main__":
    print_pgvector_sql()