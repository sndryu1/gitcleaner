import os, subprocess, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import gitcleaner as g


def sh(d, *a):
    subprocess.run(a, cwd=d, check=True, capture_output=True)


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name
        self.old = os.getcwd()
        os.chdir(self.d)
        sh(self.d, "git", "init", "-q", "-b", "main")
        sh(self.d, "git", "config", "user.email", "a@b.c")
        sh(self.d, "git", "config", "user.name", "A")
        sh(self.d, "git", "commit", "-q", "--allow-empty", "-m", "init")
        sh(self.d, "git", "branch", "merged-one")
        sh(self.d, "git", "checkout", "-q", "-b", "wip")
        sh(self.d, "git", "commit", "-q", "--allow-empty", "-m", "wip")
        sh(self.d, "git", "checkout", "-q", "main")

    def tearDown(self):
        os.chdir(self.old)
        self.tmp.cleanup()

    def test_classify(self):
        res = {b["name"]: g.classify(b, 0) for b in g.branches()}
        self.assertEqual(res, {"main": None, "merged-one": "merged", "wip": None})

    def test_stale(self):
        bs = g.branches(now=10**10)
        self.assertTrue(g.classify(next(b for b in bs if b["name"] == "wip"), 30).startswith("stale"))

    def test_delete_skips_unmerged_without_force(self):
        g.main(["--delete", "--yes"])
        names = {b["name"] for b in g.branches()}
        self.assertEqual(names, {"main", "wip"})

    def test_current_branch_protected(self):
        sh(self.d, "git", "checkout", "-q", "merged-one")
        self.assertIsNone(g.classify(next(b for b in g.branches() if b["name"] == "merged-one"), 0))


if __name__ == "__main__":
    unittest.main()
