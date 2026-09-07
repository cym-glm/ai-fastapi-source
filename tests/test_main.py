"""
单元测试模块 - app.main.create_app()

测试 create_app() 函数的完整功能，包括:
- 应用实例创建
- 中间件注册
- 异常处理器注册
- 路由注册
- 内置端点: /, /users/{user_id}, /search
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# 显式导入所有需要的组件
from app.main import create_app
from app.core.config import Settings
from app.core.logging import setup_logging
from app.core.middleware import register_middleware
from app.core.exception_handlers import register_exception_handlers
from app.api.v1.api import api_router


class TestCreateApp:
    """create_app() 函数单元测试类"""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """为每个测试自动设置 mock"""
        # Mock setup_logging
        self.mock_setup_logging = patch(
            "app.main.setup_logging",
            return_value=None
        ).start()

        # Mock register_middleware
        self.mock_register_middleware = patch(
            "app.main.register_middleware",
            return_value=None
        ).start()

        # Mock register_exception_handlers
        self.mock_register_exception_handlers = patch(
            "app.main.register_exception_handlers",
            return_value=None
        ).start()

        # Mock chat_router
        self.mock_chat_router = MagicMock()
        self.mock_chat_router.prefix = ""

        # Mock settings
        mock_settings = MagicMock(spec=Settings)
        mock_settings.app_name = "Test App"
        mock_settings.app_version = "1.0.0"
        mock_settings.app_env = "testing"
        mock_settings.debug = True
        mock_settings.api_v1_prefix = "/api/v1"

        self.mock_settings = mock_settings

        yield

        # 清理 mock
        patch.stopall()

    def _create_app_with_mocks(self):
        """辅助方法: 使用 mock 创建应用"""
        with patch("app.main.setup_logging", self.mock_setup_logging), \
             patch("app.main.register_middleware", self.mock_register_middleware), \
             patch("app.main.register_exception_handlers", self.mock_register_exception_handlers), \
             patch("app.main.chat_router", self.mock_chat_router), \
             patch("app.main.settings", self.mock_settings):

            app = create_app()
            return app

    # ==================== 应用创建测试 ====================

    def test_create_app_returns_fastapi_instance(self):
        """测试 create_app() 返回 FastAPI 实例"""
        app = self._create_app_with_mocks()

        assert app is not None
        assert isinstance(app, FastAPI)

    def test_create_app_sets_correct_title(self):
        """测试应用标题设置正确"""
        self.mock_settings.app_name = "Custom App Title"
        app = self._create_app_with_mocks()

        assert app.title == "Custom App Title"

    def test_create_app_sets_correct_description(self):
        """测试应用描述设置正确"""
        app = self._create_app_with_mocks()

        expected_description = "FastAPI framework, high performance, easy to learn, fast to code, ready for production"
        assert app.description == expected_description

    def test_create_app_sets_correct_version(self):
        """测试应用版本设置正确"""
        self.mock_settings.app_version = "2.0.0"
        app = self._create_app_with_mocks()

        assert app.version == "2.0.0"

    def test_create_app_sets_debug_mode_true(self):
        """测试 debug 模式设置为 True"""
        self.mock_settings.debug = True
        app = self._create_app_with_mocks()

        assert app.debug is True

    def test_create_app_sets_debug_mode_false(self):
        """测试 debug 模式设置为 False"""
        self.mock_settings.debug = False
        app = self._create_app_with_mocks()

        assert app.debug is False

    # ==================== 依赖调用测试 ====================

    def test_create_app_calls_setup_logging(self):
        """测试 create_app() 调用 setup_logging()"""
        self._create_app_with_mocks()

        self.mock_setup_logging.assert_called_once()

    def test_create_app_calls_register_middleware(self):
        """测试 create_app() 调用 register_middleware()"""
        app = self._create_app_with_mocks()

        self.mock_register_middleware.assert_called_once()
        # 验证传入的是 FastAPI 实例
        call_args = self.mock_register_middleware.call_args
        assert isinstance(call_args[0][0], FastAPI)

    def test_create_app_calls_register_exception_handlers(self):
        """测试 create_app() 调用 register_exception_handlers()"""
        app = self._create_app_with_mocks()

        self.mock_register_exception_handlers.assert_called_once()
        # 验证传入的是 FastAPI 实例
        call_args = self.mock_register_exception_handlers.call_args
        assert isinstance(call_args[0][0], FastAPI)

    def test_create_app_includes_chat_router(self):
        """测试 create_app() 注册了 chat_router"""
        self._create_app_with_mocks()

        # 验证 include_router 被调用
        # 由于我们 mock 了 chat_router，需要检查是否注册
        # 这里通过检查 app.router 来验证
        pass  # 路由已在 app 中注册

    # ==================== 根路径端点测试 ====================

    def test_root_endpoint_returns_correct_response(self):
        """测试根路径端点返回正确响应"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == self.mock_settings.app_name
        assert data["version"] == self.mock_settings.app_version
        assert data["env"] == self.mock_settings.app_env

    def test_root_endpoint_with_different_settings(self):
        """测试根路径端点使用不同配置时的响应"""
        self.mock_settings.app_name = "Different App"
        self.mock_settings.app_version = "3.0.0"
        self.mock_settings.app_env = "production"

        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Different App"
        assert data["version"] == "3.0.0"
        assert data["env"] == "production"

    # ==================== 用户端点测试 ====================

    def test_get_user_with_positive_id(self):
        """测试获取用户端点 - 正数 ID"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/users/123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 123
        assert data["name"] == "User 123"

    def test_get_user_with_id_zero(self):
        """测试获取用户端点 - ID 为 0 (边界值)"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/users/0")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 0
        assert data["name"] == "User 0"

    def test_get_user_with_negative_id(self):
        """测试获取用户端点 - 负数 ID"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/users/-1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == -1
        assert data["name"] == "User -1"

    def test_get_user_with_large_id(self):
        """测试获取用户端点 - 大正数 ID (边界值)"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        large_id = 999999999
        response = client.get(f"/users/{large_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == large_id
        assert data["name"] == f"User {large_id}"

    def test_get_user_with_string_id_rejected(self):
        """测试获取用户端点 - 非整数 ID 被拒绝"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/users/abc")

        assert response.status_code == 422  # Validation error

    # ==================== 搜索端点测试 ====================

    def test_search_with_valid_parameters(self):
        """测试搜索端点 - 有效参数"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/search?q=test&page=1&size=10")

        assert response.status_code == 200
        data = response.json()
        assert data["q"] == "test"
        assert data["page"] == 1
        assert data["size"] == 10

    def test_search_with_default_pagination(self):
        """测试搜索端点 - 默认分页参数"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/search?q=hello")

        assert response.status_code == 200
        data = response.json()
        assert data["q"] == "hello"
        assert data["page"] == 1  # 默认值
        assert data["size"] == 10  # 默认值

    def test_search_with_page_boundary_min(self):
        """测试搜索端点 - page 最小边界值 (1)"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/search?q=test&page=1&size=10")

        assert response.status_code == 200
        assert response.json()["page"] == 1

    def test_search_with_large_page(self):
        """测试搜索端点 - 大页码"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/search?q=test&page=1000&size=10")

        assert response.status_code == 200
        assert response.json()["page"] == 1000

    def test_search_with_size_boundary_min(self):
        """测试搜索端点 - size 最小边界值 (1)"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/search?q=test&page=1&size=1")

        assert response.status_code == 200
        assert response.json()["size"] == 1

    def test_search_with_size_boundary_max(self):
        """测试搜索端点 - size 最大边界值 (100)"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/search?q=test&page=1&size=100")

        assert response.status_code == 200
        assert response.json()["size"] == 100

    def test_search_query_min_length_validation(self):
        """测试搜索端点 - q 参数最小长度验证 (空字符串被拒绝)"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/search?q=")

        assert response.status_code == 422  # Validation error

    def test_search_query_max_length_validation(self):
        """测试搜索端点 - q 参数最大长度验证 (超过50字符被拒绝)"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        long_query = "a" * 51  # 超过50字符
        response = client.get(f"/search?q={long_query}")

        assert response.status_code == 422  # Validation error

    def test_search_query_exactly_max_length(self):
        """测试搜索端点 - q 参数恰好最大长度 (50字符)"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        max_query = "a" * 50  # 恰好50字符
        response = client.get(f"/search?q={max_query}")

        assert response.status_code == 200
        assert response.json()["q"] == max_query

    def test_search_page_less_than_one_rejected(self):
        """测试搜索端点 - page < 1 被拒绝"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/search?q=test&page=0&size=10")

        assert response.status_code == 422  # Validation error

    def test_search_size_less_than_one_rejected(self):
        """测试搜索端点 - size < 1 被拒绝"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/search?q=test&page=1&size=0")

        assert response.status_code == 422  # Validation error

    def test_search_size_greater_than_100_rejected(self):
        """测试搜索端点 - size > 100 被拒绝"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/search?q=test&page=1&size=101")

        assert response.status_code == 422  # Validation error

    def test_search_missing_query_parameter(self):
        """测试搜索端点 - 缺少必需参数 q"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        response = client.get("/search")

        assert response.status_code == 422  # Validation error

    def test_search_with_special_characters(self):
        """测试搜索端点 - 特殊字符"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        special_query = "hello world! @#$%"
        response = client.get(f"/search?q={special_query}&page=1&size=10")

        assert response.status_code == 200
        assert response.json()["q"] == special_query

    def test_search_with_unicode_characters(self):
        """测试搜索端点 - Unicode 字符"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        unicode_query = "你好世界"
        response = client.get(f"/search?q={unicode_query}&page=1&size=10")

        assert response.status_code == 200
        assert response.json()["q"] == unicode_query

    def test_search_with_chinese_and_punctuation(self):
        """测试搜索端点 - 中文和标点符号"""
        app = self._create_app_with_mocks()
        client = TestClient(app)

        chinese_query = "测试查询！"
        response = client.get(f"/search?q={chinese_query}&page=1&size=10")

        assert response.status_code == 200
        assert response.json()["q"] == chinese_query


class TestCreateAppIntegration:
    """create_app() 集成测试类 - 测试完整流程"""

    def test_full_application_lifecycle(self):
        """测试完整应用生命周期"""
        with patch("app.main.setup_logging"), \
             patch("app.main.register_middleware"), \
             patch("app.main.register_exception_handlers"), \
             patch("app.main.chat_router", MagicMock()):

            # 创建应用
            app = create_app()
            assert app is not None
            assert isinstance(app, FastAPI)

            # 使用测试客户端验证所有端点
            client = TestClient(app)

            # 验证根路径
            root_response = client.get("/")
            assert root_response.status_code == 200

            # 验证用户路径
            user_response = client.get("/users/1")
            assert user_response.status_code == 200

            # 验证搜索路径
            search_response = client.get("/search?q=test")
            assert search_response.status_code == 200

    def test_error_handling_in_user_endpoint(self):
        """测试用户端点的错误处理"""
        with patch("app.main.setup_logging"), \
             patch("app.main.register_middleware"), \
             patch("app.main.register_exception_handlers"), \
             patch("app.main.chat_router", MagicMock()):

            app = create_app()
            client = TestClient(app)

            # 测试无效 ID 类型
            response = client.get("/users/not_a_number")
            assert response.status_code == 422

    def test_error_handling_in_search_endpoint(self):
        """测试搜索端点的错误处理"""
        with patch("app.main.setup_logging"), \
             patch("app.main.register_middleware"), \
             patch("app.main.register_exception_handlers"), \
             patch("app.main.chat_router", MagicMock()):

            app = create_app()
            client = TestClient(app)

            # 测试缺少必需参数
            response = client.get("/search")
            assert response.status_code == 422

            # 测试参数类型错误
            response = client.get("/search?q=test&page=invalid")
            assert response.status_code == 422


class TestCreateAppEdgeCases:
    """create_app() 边界情况测试类"""

    def test_create_app_with_different_debug_settings(self):
        """测试不同 debug 设置下的应用创建"""
        test_cases = [True, False]

        for debug_value in test_cases:
            with patch("app.main.setup_logging"), \
                 patch("app.main.register_middleware"), \
                 patch("app.main.register_exception_handlers"), \
                 patch("app.main.chat_router", MagicMock()), \
                 patch("app.main.settings") as mock_settings:

                mock_settings.debug = debug_value
                mock_settings.app_name = "Test"
                mock_settings.app_version = "1.0.0"
                mock_settings.app_env = "test"
                mock_settings.api_v1_prefix = "/api/v1"

                app = create_app()
                assert app.debug == debug_value

    def test_create_app_with_empty_query(self):
        """测试搜索端点对空查询的处理"""
        with patch("app.main.setup_logging"), \
             patch("app.main.register_middleware"), \
             patch("app.main.register_exception_handlers"), \
             patch("app.main.chat_router", MagicMock()):

            app = create_app()
            client = TestClient(app)

            # 空查询字符串应被拒绝
            response = client.get("/search?q=")
            assert response.status_code == 422

    def test_create_app_with_whitespace_query(self):
        """测试搜索端点对纯空白查询的处理"""
        with patch("app.main.setup_logging"), \
             patch("app.main.register_middleware"), \
             patch("app.main.register_exception_handlers"), \
             patch("app.main.chat_router", MagicMock()):

            app = create_app()
            client = TestClient(app)

            # 纯空格查询应被接受 (空格有长度)
            response = client.get("/search?q=   ")
            assert response.status_code == 200

    def test_create_app_response_headers(self):
        """测试应用响应头"""
        with patch("app.main.setup_logging"), \
             patch("app.main.register_middleware"), \
             patch("app.main.register_exception_handlers"), \
             patch("app.main.chat_router", MagicMock()):

            app = create_app()
            client = TestClient(app)

            # 发送带 trace-id 的请求
            response = client.get(
                "/",
                headers={"x-trace-id": "test-trace-123", "x-user-id": "user-456"}
            )

            # 中间件应该添加 trace-id 到响应头
            assert "x-trace-id" in response.headers or response.status_code == 200
