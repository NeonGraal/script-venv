from script_venv.venv import VEnv


def test_venv_str():
    venv = VEnv('test')
    assert "test" in str(venv)
