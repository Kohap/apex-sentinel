import unittest
from apex_agent.engine import onchain_config, prompt_for


class OnchainConfigTest(unittest.TestCase):
    def test_off_by_default(self):
        self.assertIsNone(onchain_config())

    def test_accepts_loopback(self):
        cfg = onchain_config("http://127.0.0.1:8545", 4663, 93984992, ["0x" + "a" * 40])
        self.assertEqual(cfg["chain_id"], 4663)
        self.assertEqual(cfg["addresses"], ["0x" + "a" * 40])
        self.assertIsNotNone(onchain_config("http://localhost:8545"))
        self.assertIsNotNone(onchain_config("http://[::1]:8545"))

    def test_rejects_remote_rpc(self):
        for url in ("https://rpc.mainnet.chain.robinhood.com", "http://10.0.0.5:8545", "file:///tmp/x"):
            with self.assertRaises(ValueError):
                onchain_config(url)

    def test_rejects_bad_address_and_orphan_flags(self):
        with self.assertRaises(ValueError):
            onchain_config("http://127.0.0.1:8545", addresses=["0x123"])
        with self.assertRaises(ValueError):
            onchain_config(chain_id=1)

    def test_prompt_includes_onchain_only_when_enabled(self):
        base = {"focus": "x", "summary": "", "findings": [], "coverage": [], "blockers": [], "next_steps": []}
        self.assertNotIn("On-chain mode", prompt_for(dict(base), "explore"))
        on = dict(base, onchain=onchain_config("http://127.0.0.1:8545", 1, 5, []))
        text = prompt_for(on, "explore")
        self.assertIn("On-chain mode", text)
        self.assertIn("127.0.0.1:8545", text)


if __name__ == "__main__":
    unittest.main()
