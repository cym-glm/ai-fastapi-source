from enum import Enum


class AppEnv(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ApiTag:
    HEALTH = "Health"
    CHAT = "Chat"
    CONVERSATIONS = "Conversations"
    RAG = "RAG"
    MODELS = "Models"
    AGENTS = "Agents"