import json
from pathlib import Path
import sys
import tempfile
import unittest

from apex_agent.runtime import CodexRuntime


class RuntimeAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / 'workspace'
        self.workspace.mkdir()
        self.binary = self.root / 'fixture-codex'

    def executable(self, body):
        self.binary.write_text(f'#!{sys.executable}\n' + body)
        self.binary.chmod(0o755)
        return CodexRuntime(str(self.binary))

    def test_process_adapter_reads_structured_result_and_captured_command(self):
        response = {'summary': 'Adapter fixture only', 'done': False, 'coverage': [],
                    'findings': [], 'blockers': [], 'next_steps': []}
        runtime = self.executable('''import json, sys
from pathlib import Path
args = sys.argv[1:]
assert args[args.index('--sandbox') + 1] == 'workspace-write'
assert 'sandbox_workspace_write.network_access=false' in args
assert sys.stdin.read() == 'adapter fixture prompt'
result = Path(args[args.index('--output-last-message') + 1])
result.write_text(''' + repr(json.dumps(response)) + ''')
print(json.dumps({'type': 'item.completed', 'item': {'id': 'fixture_1', 'type': 'command_execution',
    'command': 'python3 artifacts/check.py', 'aggregated_output': 'adapter fixture output', 'exit_code': 0}}))
print(json.dumps({'type': 'turn.completed', 'usage': {'input_tokens': 3}}))
''')
        result, commands, usage = runtime.run(self.workspace, self.root / 'round', 'adapter fixture prompt', 10)
        self.assertEqual(result, response)
        self.assertEqual(commands[0]['output'], 'adapter fixture output')
        self.assertEqual(usage, {'input_tokens': 3})

    def test_process_timeout_is_enforced(self):
        runtime = self.executable('import sys, time\nsys.stdin.read()\ntime.sleep(10)\n')
        with self.assertRaises(TimeoutError):
            runtime.run(self.workspace, self.root / 'round', 'prompt', .15)
        self.assertTrue((self.root / 'round/events.jsonl').exists())

    def test_timeout_also_covers_blocked_prompt_delivery(self):
        runtime = self.executable('import time\ntime.sleep(10)\n')
        with self.assertRaises(TimeoutError):
            runtime.run(self.workspace, self.root / 'round', 'x' * 1_000_000, .15)

    def test_invalid_structured_result_is_rejected(self):
        runtime = self.executable('''import sys
from pathlib import Path
sys.stdin.read()
Path(sys.argv[sys.argv.index('--output-last-message')+1]).write_text('{"done": true}')
''')
        with self.assertRaisesRegex(RuntimeError, 'Invalid agent response'):
            runtime.run(self.workspace, self.root / 'round', 'prompt', 10)

    def test_nonzero_process_exit_cannot_complete(self):
        runtime = self.executable('import sys\nsys.stdin.read()\nsys.exit(7)\n')
        with self.assertRaisesRegex(RuntimeError, 'exit 7'):
            runtime.run(self.workspace, self.root / 'round', 'prompt', 10)


if __name__ == '__main__':
    unittest.main()
