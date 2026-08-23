from hr_recruitment_ai_assistant_core.orchestrator import Orchestrator

def test_hr_recruitment_ai_assistant_orchestrator():
    orch = Orchestrator()
    res = orch.run('test task')
    assert res['status'] == 'completed'
