import copy
import json
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from data import DATA, ROOT, ReviewConfig, DataError, load_scenario, review_candidates, statistics_baseline
from agent import Report, validate_report, dispatch, report_markdown
from tests.test_agent import example_report, FakeClient


def inputs():
    folder = DATA/'scenarios/00_practice'
    return pd.read_csv(folder/'stats.csv', dtype=str, keep_default_na=False), (folder/'feedback.csv').read_bytes()


def test_whole_current_character_missing_is_reported_without_inventing_rates():
    stats, feedback = inputs()
    stats = stats[~((stats.character=='Brannoc') & (stats['update']=='3.2'))]
    e = load_scenario(stats_bytes=stats.to_csv(index=False).encode(), feedback_bytes=feedback)
    assert any('Brannoc' in w for w in e.warnings)
    assert all(r['win_rate'] is None for r in e.get_performance('Brannoc')['rows'] if r['update']=='3.2')
    assert any(c['character']=='Brannoc' and c['action']=='Collect data' for c in review_candidates(e))


def test_scope_distinguishes_unobserved_test_queue_from_missing_standard_roster():
    e = load_scenario('01_strong_performance')
    assert not e.warnings
    assert next(r for r in e.coverage if r['Character']=='Quill')['Scope']=='Outside scope'
    full = load_scenario('01_strong_performance',config=ReviewConfig(scope='Entire roster'))
    assert any('Quill' in w for w in full.warnings)
    standard = load_scenario(config=ReviewConfig(scope='Standard only'))
    assert 'Quill' not in set(standard.stats.character)


def test_configuration_changes_metrics_tools_baseline_and_report_rules_together():
    config = ReviewConfig(win_rate_min=.40,win_rate_max=.60,min_appearances=2500,pick_rate_min=.20,pick_rate_max=.40)
    e = load_scenario(config=config)
    assert not any(c['action']=='Investigate' for c in review_candidates(e))
    assert e.metric_index()['stats:3.2:Brannoc:High']['balance_flag']=='Collect data'
    assert e.get_review_rules()['thresholds']['win_rate_max']==.60
    assert '46% to 54%' not in e.guide
    assert e.get_review_rules()['configuration']==config.snapshot()


@pytest.mark.parametrize('settings',[{'win_rate_min':.6,'win_rate_max':.4},{'min_appearances':0},{'pick_rate_max':1.5},{'ranking':'unknown'}])
def test_invalid_configuration_rejected(settings):
    with pytest.raises(DataError): ReviewConfig(**settings)


def test_policy_changes_order_when_reach_and_deviation_disagree():
    stats, feedback = inputs()
    for group in ['Low','Mid','High']:
        mask=(stats.character=='Vex')&(stats['update']=='3.2')&(stats.skill_group==group)
        stats.loc[mask,'wins']=str(round(int(stats.loc[mask,'appearances'].iloc[0])*.55))
    mask=(stats.character=='Brannoc')&(stats['update']=='3.2')&(stats.skill_group=='High')
    stats.loc[mask,'wins']=str(round(int(stats.loc[mask,'appearances'].iloc[0])*.80))
    kwargs={'stats_bytes':stats.to_csv(index=False).encode(),'feedback_bytes':feedback}
    reach=load_scenario(**kwargs)
    deviation=load_scenario(**kwargs,config=ReviewConfig(ranking='Largest deviation first'))
    assert statistics_baseline(reach)[0]['character']!='Brannoc'
    assert statistics_baseline(deviation)[0]['character']=='Brannoc'


def test_low_sample_request_cannot_displace_supported_investigation():
    e=load_scenario()
    body=example_report()
    body['priorities'][0].update(character='Quill',action='Collect data',metric_refs=[f'stats:3.2:Quill:{g}' for g in ['Low','Mid','High']],comment_ids=[],context_refs=[])
    body['not_selected']=[{'character':c,'reason':'Deferred.'} for c in ['Vex','Lyra','Brannoc']]
    errors=validate_report(Report.model_validate(body),e,[])
    assert any('displace' in error for error in errors)


def test_report_stays_tied_to_its_original_rules_after_ui_changes(monkeypatch,tmp_path):
    import agent, dotenv
    monkeypatch.setattr(dotenv,'dotenv_values',lambda *a,**kw:{})
    monkeypatch.setenv('GEMINI_API_KEY','fake-local-test')
    original=agent.review
    save=agent.save_run
    monkeypatch.setattr(agent,'review',lambda e,key,model,**kw:original(e,key,model,client=FakeClient(),**kw))
    monkeypatch.setattr(agent,'save_run',lambda run:save(run,tmp_path))
    app=AppTest.from_file(ROOT/'app.py',default_timeout=30).run()
    app.button(key='run_review').click().run()
    assert not app.exception
    original_rules=app.session_state['last_run']['configuration']
    app.number_input(key='rule_sample').set_value(1000).run()
    assert not app.exception
    assert any('previous review' in w.value for w in app.warning)
    assert app.session_state['last_run']['configuration']==original_rules
    assert original_rules['min_appearances']==500
    exported = report_markdown(app.session_state['last_run'], app.session_state['run_evidence'])
    assert '| Minimum appearances per group | 500 |' in exported
    assert '| Skill group | Patch | Win rate |' in exported
    app.button(key='reset_rules').click().run()
    assert app.number_input(key='rule_sample').value==500


def test_rank_validation_and_custom_eligibility_are_enforced():
    e=load_scenario()
    body=example_report()
    body['not_selected']=[]
    priorities=[]
    for candidate in review_candidates(e):
        if candidate['action']!='Investigate':continue
        p=copy.deepcopy(body['priorities'][0])
        p.update(character=candidate['character'],affected_skill_groups=candidate['affected_skill_groups'],metric_refs=candidate['metric_refs'],comment_ids=[],context_refs=[])
        priorities.append(p)
    body['priorities']=priorities
    calls=[{'name':name,'arguments':{},'result':dispatch(e,name,{})} for name in ['get_review_rules','get_performance','get_character_context','get_feedback']]
    assert not validate_report(Report.model_validate(body),e,calls)
    body['priorities']=list(reversed(priorities))
    assert any('order' in error for error in validate_report(Report.model_validate(body),e,calls))
    custom=load_scenario(config=ReviewConfig(win_rate_min=.40,win_rate_max=.60))
    assert any('ordinary' in error for error in validate_report(Report.model_validate(body),custom,calls))


def test_settings_are_isolated_between_user_sessions(monkeypatch):
    import dotenv
    monkeypatch.setattr(dotenv,'dotenv_values',lambda *a,**kw:{})
    first=AppTest.from_file(ROOT/'app.py',default_timeout=30).run()
    first.number_input(key='rule_sample').set_value(1000).run()
    second=AppTest.from_file(ROOT/'app.py',default_timeout=30).run()
    assert first.number_input(key='rule_sample').value==1000
    assert second.number_input(key='rule_sample').value==500


def test_unreceived_rows_are_explicitly_identified():
    e=load_scenario('01_strong_performance',config=ReviewConfig(scope='Entire roster'))
    rows=[r for r in e.get_performance('Quill')['rows'] if r['update']=='3.2']
    assert all(r['record_missing'] and r['win_rate'] is None for r in rows)
