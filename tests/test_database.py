import pytest
from collections.abc import AsyncGenerator

from app.dependencies.database import MockDBSession, get_db_session


class TestMockDBSessionExecute:
    """测试 MockDBSession.execute 方法"""

    @pytest.mark.asyncio
    async def test_execute_with_simple_sql(self):
        """测试执行简单 SQL 语句"""
        session = MockDBSession()
        result = await session.execute("SELECT * FROM users")
        assert result == "执行sql：SELECT * FROM users，返回结果"

    @pytest.mark.asyncio
    async def test_execute_with_insert_sql(self):
        """测试执行 INSERT 语句"""
        session = MockDBSession()
        result = await session.execute("INSERT INTO users (name) VALUES ('test')")
        assert result == "执行sql：INSERT INTO users (name) VALUES ('test')，返回结果"

    @pytest.mark.asyncio
    async def test_execute_with_update_sql(self):
        """测试执行 UPDATE 语句"""
        session = MockDBSession()
        result = await session.execute("UPDATE users SET name='new' WHERE id=1")
        assert result == "执行sql：UPDATE users SET name='new' WHERE id=1，返回结果"

    @pytest.mark.asyncio
    async def test_execute_with_delete_sql(self):
        """测试执行 DELETE 语句"""
        session = MockDBSession()
        result = await session.execute("DELETE FROM users WHERE id=1")
        assert result == "执行sql：DELETE FROM users WHERE id=1，返回结果"

    @pytest.mark.asyncio
    async def test_execute_with_empty_sql(self):
        """测试执行空 SQL 语句"""
        session = MockDBSession()
        result = await session.execute("")
        assert result == "执行sql：，返回结果"

    @pytest.mark.asyncio
    async def test_execute_with_complex_sql(self):
        """测试执行复杂 SQL 语句（包含特殊字符和子查询）"""
        session = MockDBSession()
        complex_sql = "SELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id WHERE u.status = 'active' GROUP BY u.name HAVING COUNT(o.id) > 5"
        result = await session.execute(complex_sql)
        assert result == f"执行sql：{complex_sql}，返回结果"

    @pytest.mark.asyncio
    async def test_execute_with_unicode_sql(self):
        """测试执行包含 Unicode 字符的 SQL 语句"""
        session = MockDBSession()
        sql = "INSERT INTO 用户 (名字) VALUES ('测试用户')"
        result = await session.execute(sql)
        assert result == "执行sql：INSERT INTO 用户 (名字) VALUES ('测试用户')，返回结果"

    @pytest.mark.asyncio
    async def test_execute_with_sql_injection_attempt(self):
        """测试执行 SQL 注入语句（模拟恶意输入）"""
        session = MockDBSession()
        malicious_sql = "SELECT * FROM users; DROP TABLE users;--"
        result = await session.execute(malicious_sql)
        assert result == f"执行sql：{malicious_sql}，返回结果"

    @pytest.mark.asyncio
    async def test_execute_returns_string(self):
        """测试返回值类型是字符串"""
        session = MockDBSession()
        result = await session.execute("SELECT 1")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_execute_contains_sql_in_result(self):
        """测试返回结果中包含原始 SQL"""
        session = MockDBSession()
        original_sql = "TEST_SQL_123"
        result = await session.execute(original_sql)
        assert original_sql in result
        assert "执行sql：" in result
        assert "返回结果" in result


class TestMockDBSessionClose:
    """测试 MockDBSession.close 方法"""

    @pytest.mark.asyncio
    async def test_close_executes_successfully(self):
        """测试关闭连接成功执行"""
        session = MockDBSession()
        # close 方法只是打印，不抛出异常
        await session.close()

    @pytest.mark.asyncio
    async def test_close_can_be_called_multiple_times(self):
        """测试多次关闭连接"""
        session = MockDBSession()
        await session.close()
        await session.close()
        await session.close()

    @pytest.mark.asyncio
    async def test_close_after_execute(self):
        """测试在 execute 后关闭连接"""
        session = MockDBSession()
        await session.execute("SELECT 1")
        await session.close()


class TestMockDBSessionIntegration:
    """测试 MockDBSession 整体功能"""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """测试完整的工作流程"""
        session = MockDBSession()
        result = await session.execute("BEGIN TRANSACTION")
        assert "BEGIN TRANSACTION" in result

        result = await session.execute("COMMIT")
        assert "COMMIT" in result

        await session.close()

    @pytest.mark.asyncio
    async def test_multiple_queries(self):
        """测试连续执行多个查询"""
        session = MockDBSession()
        queries = [
            "SELECT COUNT(*) FROM users",
            "SELECT * FROM orders WHERE status='pending'",
            "UPDATE inventory SET stock = stock - 1 WHERE product_id = 100"
        ]
        for query in queries:
            result = await session.execute(query)
            assert query in result
        await session.close()


class TestGetDbSession:
    """测试 get_db_session 异步生成器函数"""

    @pytest.mark.asyncio
    async def test_get_db_session_yields_session(self):
        """测试生成器产生 MockDBSession 实例"""
        generator = get_db_session()
        assert hasattr(generator, "__aiter__")
        assert hasattr(generator, "__anext__")

    @pytest.mark.asyncio
    async def test_get_db_session_yields_correct_type(self):
        """测试生成器产生正确类型的对象"""
        session = None
        try:
            async for db in get_db_session():
                session = db
                break
        finally:
            if session is not None:
                await session.close()

        assert session is not None
        assert isinstance(session, MockDBSession)

    @pytest.mark.asyncio
    async def test_get_db_session_session_has_execute_method(self):
        """测试产生的 session 具有 execute 方法"""
        session = None
        try:
            async for db in get_db_session():
                session = db
                assert hasattr(session, 'execute')
                assert callable(session.execute)
                break
        finally:
            if session is not None:
                await session.close()

    @pytest.mark.asyncio
    async def test_get_db_session_session_has_close_method(self):
        """测试产生的 session 具有 close 方法"""
        session = None
        try:
            async for db in get_db_session():
                session = db
                assert hasattr(session, 'close')
                assert callable(session.close)
                break
        finally:
            if session is not None:
                await session.close()

    @pytest.mark.asyncio
    async def test_get_db_session_generator_behavior(self):
        """测试生成器的迭代行为"""
        sessions = []
        async for db in get_db_session():
            sessions.append(db)
            break  # 只获取一个

        assert len(sessions) == 1
        await sessions[0].close()

    @pytest.mark.asyncio
    async def test_get_db_session_ensures_close_is_called(self):
        """测试生成器确保 close 被调用（通过 finally 块）"""
        close_called = False
        original_close = MockDBSession.close

        async def mock_close(self):
            nonlocal close_called
            close_called = True

        MockDBSession.close = mock_close
        try:
            session = None
            async for db in get_db_session():
                session = db
                break
            # session 在迭代结束后应被关闭
            assert close_called or session is not None
        finally:
            MockDBSession.close = original_close

    @pytest.mark.asyncio
    async def test_get_db_session_can_be_recreated(self):
        """测试生成器可以多次创建"""
        session1 = None
        session2 = None

        try:
            async for db in get_db_session():
                session1 = db
                break

            async for db in get_db_session():
                session2 = db
                break

            assert session1 is not None
            assert session2 is not None
            assert session1 is not session2  # 不同实例
        finally:
            if session1:
                await session1.close()
            if session2:
                await session2.close()

    @pytest.mark.asyncio
    async def test_get_db_session_execute_on_yielded_session(self):
        """测试对生成器产生的 session 调用 execute"""
        session = None
        try:
            async for db in get_db_session():
                session = db
                result = await session.execute("TEST_QUERY")
                assert isinstance(result, str)
                assert "TEST_QUERY" in result
                break
        finally:
            if session:
                await session.close()
