from streamlit.testing.v1 import AppTest
from data import ROOT


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
    assert any("held-out" in item.value for item in app.warning)
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
    app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
    app.text_input(key="api_key_input").set_value("test-only-placeholder").run()
    app.button(key="run_review").click().run()
    assert not app.exception
    assert any("Review report" == s.value for s in app.subheader)
