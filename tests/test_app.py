from streamlit.testing.v1 import AppTest
from data import ROOT, scenarios
import pytest


@pytest.fixture(autouse=True)
def isolate_private_local_setup(monkeypatch):
    # UI tests must not read an owner's actual saved key/model.
    import dotenv
    monkeypatch.setattr(dotenv, "dotenv_values", lambda *args, **kwargs: {})
    for name in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_MODEL"]:
        monkeypatch.delenv(name, raising=False)


def test_app_loads_without_credentials_and_baseline_is_available(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "BalanceCheck"
    assert app.button(key="run_review").disabled
    assert any("Data is ready" in item.value for item in app.info)
    app.selectbox(key="scenario").set_value("01_strong_performance").run()
    assert not app.exception
    assert app.button(key="run_review").disabled
    app.radio[0].set_value("Upload CSVs").run()
    assert not app.exception
    assert any("Upload both" in item.value for item in app.info)


def test_app_model_connection_with_test_double(monkeypatch, tmp_path):
    import agent
    original = agent.review
    save = agent.save_run
    from tests.test_agent import FakeClient
    monkeypatch.setattr(agent, "review", lambda e, key, model, **kw: original(e, key, model, client=FakeClient(), **kw))
    monkeypatch.setattr(agent, "save_run", lambda run: save(run, tmp_path))
    monkeypatch.setenv("GEMINI_API_KEY", "test-only-placeholder")
    app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
    assert not app.text_input
    app.button(key="run_review").click().run()
    assert not app.exception
    assert any("Review priorities" == s.value for s in app.subheader)


def test_local_setup_checks_saves_then_hides_owner_controls(monkeypatch, tmp_path):
    import agent
    monkeypatch.setenv("BALANCECHECK_LOCAL_SETUP", "1")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setattr(agent, "check_connection", lambda key, model: {
        "ok": True, "available_models": [agent.DEFAULT_MODEL], "selected_model_listed": True})
    (tmp_path / ".gitignore").write_text(".env.*\n")
    save = agent.save_local_configuration

    def save_setup(key, model):
        save(key, model, root=tmp_path)
        monkeypatch.setenv("GEMINI_API_KEY", key)
        monkeypatch.setenv("GEMINI_MODEL", model)

    monkeypatch.setattr(agent, "save_local_configuration", save_setup)
    app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
    app.text_input(key="api_key_input").set_value("test-only-placeholder").run()
    assert app.button(key="run_review").disabled
    app.button(key="check_connection").click().run()
    assert not app.exception
    app.button(key="save_setup").click().run()
    assert not app.exception
    assert not app.text_input
    assert not app.button(key="run_review").disabled
    assert (tmp_path / ".env.local").exists()


def test_hosted_secrets_enable_reviews_without_user_setup(monkeypatch):
    monkeypatch.delenv("BALANCECHECK_LOCAL_SETUP", raising=False)
    app = AppTest.from_file(ROOT / "app.py", default_timeout=30)
    app.secrets["GEMINI_API_KEY"] = "cloud-test-placeholder"
    app.secrets["GEMINI_MODEL"] = "gemini-3.5-flash-lite"
    app.run()
    assert not app.exception
    assert not app.text_input
    assert not app.button(key="run_review").disabled
    assert not any("Model for this app" == box.label for box in app.selectbox)
    for scenario in scenarios():
        app.selectbox(key="scenario").set_value(scenario).run()
        assert not app.exception
        assert not app.button(key="run_review").disabled
        assert not any("freeze" in item.value.lower() or "held-out" in item.value.lower() for item in app.warning)
