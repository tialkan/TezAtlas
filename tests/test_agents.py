"""
test_agents.py — Agents module tests.

Tests:
1. Config loading (agents.yaml)
2. Provider factory (no real API calls — uses mocks)
3. Agent instantiation
4. CLI --list-providers and --test-providers (mocked)
"""
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent
AGENTS_SCRIPT = REPO_ROOT / "agents" / "run.py"


class TestConfigLoading:
    def test_agents_yaml_exists(self):
        assert (REPO_ROOT / "agents.yaml").exists()

    def test_env_example_exists(self):
        assert (REPO_ROOT / ".env.example").exists()

    def test_config_loads_without_error(self, tmp_path, monkeypatch):
        """AgentConfig loads agents.yaml without raising."""
        monkeypatch.chdir(REPO_ROOT)
        # Set fake env vars so providers don't fail on missing keys
        monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "fake-test-key")
        from agents.config import AgentConfig
        cfg = AgentConfig()
        assert len(cfg.list_providers()) > 0
        assert len(cfg.list_agents()) > 0

    def test_list_providers_returns_known_providers(self, monkeypatch):
        monkeypatch.chdir(REPO_ROOT)
        monkeypatch.setenv("GEMINI_API_KEY", "fake")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "fake")
        from agents.config import AgentConfig
        cfg = AgentConfig()
        provider_names = [p["name"] for p in cfg.list_providers()]
        assert "gemini" in provider_names

    def test_list_agents_returns_known_agents(self, monkeypatch):
        monkeypatch.chdir(REPO_ROOT)
        monkeypatch.setenv("GEMINI_API_KEY", "fake")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "fake")
        from agents.config import AgentConfig
        cfg = AgentConfig()
        agent_names = [a["name"] for a in cfg.list_agents()]
        assert "source_hunter" in agent_names
        assert "methodology_checker" in agent_names
        assert "citation_verifier" in agent_names


class TestProviders:
    def test_openai_compat_provider_instantiates(self, monkeypatch):
        monkeypatch.chdir(REPO_ROOT)
        from agents.providers.openai_compat import OpenAICompatProvider
        provider = OpenAICompatProvider(
            name="test",
            base_url="https://api.example.com/v1",
            api_key="fake-key",
            default_model="test-model",
        )
        assert provider.name == "test"
        assert provider.default_model == "test-model"
        assert provider.resolve_model(None) == "test-model"
        assert provider.resolve_model("override-model") == "override-model"

    def test_anthropic_provider_instantiates(self, monkeypatch):
        monkeypatch.chdir(REPO_ROOT)
        from agents.providers.anthropic import AnthropicProvider
        provider = AnthropicProvider(
            name="anthropic",
            api_key="fake-key",
            default_model="claude-test",
        )
        assert provider.name == "anthropic"
        assert provider.resolve_model(None) == "claude-test"


class TestAgentInstantiation:
    def test_source_hunter_instantiates(self, monkeypatch):
        monkeypatch.chdir(REPO_ROOT)
        from agents.providers.openai_compat import OpenAICompatProvider
        from agents.core.source_hunter import SourceHunterAgent
        mock_provider = OpenAICompatProvider("mock", "https://api.example.com/v1", "fake", "test")
        agent = SourceHunterAgent(provider=mock_provider, model=None)
        assert agent is not None

    def test_methodology_checker_instantiates(self, monkeypatch):
        monkeypatch.chdir(REPO_ROOT)
        from agents.providers.openai_compat import OpenAICompatProvider
        from agents.core.methodology_checker import MethodologyCheckerAgent
        mock_provider = OpenAICompatProvider("mock", "https://api.example.com/v1", "fake", "test")
        agent = MethodologyCheckerAgent(provider=mock_provider, model=None)
        assert agent is not None

    def test_citation_verifier_instantiates(self, monkeypatch):
        monkeypatch.chdir(REPO_ROOT)
        from agents.providers.openai_compat import OpenAICompatProvider
        from agents.core.citation_verifier import CitationVerifierAgent
        mock_provider = OpenAICompatProvider("mock", "https://api.example.com/v1", "fake", "test")
        agent = CitationVerifierAgent(provider=mock_provider, model=None)
        assert agent is not None


class TestPromptFiles:
    """System prompt files must exist and be non-empty."""

    def test_source_hunter_prompt_exists(self):
        p = REPO_ROOT / "agents" / "prompts" / "source_hunter.md"
        assert p.exists()
        assert len(p.read_text()) > 100

    def test_methodology_checker_prompt_exists(self):
        p = REPO_ROOT / "agents" / "prompts" / "methodology_checker.md"
        assert p.exists()
        assert len(p.read_text()) > 100

    def test_citation_verifier_prompt_exists(self):
        p = REPO_ROOT / "agents" / "prompts" / "citation_verifier.md"
        assert p.exists()
        assert len(p.read_text()) > 100


class TestCLI:
    def test_list_providers_cli(self, monkeypatch):
        """--list-providers exits 0 and prints provider table."""
        env = {"GEMINI_API_KEY": "fake", "DEEPSEEK_API_KEY": "fake", "PATH": "/usr/bin:/bin"}
        result = subprocess.run(
            [sys.executable, str(AGENTS_SCRIPT), "--list-providers"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(REPO_ROOT),
            env=env,
        )
        assert result.returncode == 0
        assert "gemini" in result.stdout.lower()
