from swarmintelligence.modules.bash_console_tool import BashConsoleInterpreterToolClass

import unittest
class TestBashConsoleInterpreterToolClass(unittest.TestCase):
    def setUp(self):
        pass

    def test_bash_console_tool(self):
        import types, json, subprocess
        _subproc_original = subprocess.run
        def _fake_run(*args, **kwargs):
            return types.SimpleNamespace(returncode=0, stdout="Hello PowerShell\n", stderr="")
        subprocess.run = _fake_run
        tool = BashConsoleInterpreterToolClass(timeout_seconds=5)
        out_json = tool.run('Write-Output "Hello PowerShell"')
        print(json.loads(out_json))
        subprocess.run = _subproc_original

