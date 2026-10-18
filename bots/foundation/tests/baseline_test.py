import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('foundation_baseline', Path(__file__).parents[1] / 'baseline.py')
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)


class BaselineTests(unittest.TestCase):
    def test_detects_content_names_additions_and_missing_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            src = root / 'bots' / 'legacy' / 'src'
            src.mkdir(parents=True)
            main = src / 'main.cpp'
            main.write_bytes(b'int main() {}\n')
            manifest = {'schema': 1, 'protected_bots': {'legacy': baseline.source_identity(src)}}
            baseline.verify(root, manifest)
            for content in (b'int main(){return 1;}\n', b''):
                main.write_bytes(content)
                with self.assertRaises(ValueError): baseline.verify(root, manifest)
            main.write_bytes(b'int main() {}\n')
            extra = src / 'params.h'
            extra.write_bytes(b'#define X 1\n')
            with self.assertRaises(ValueError): baseline.verify(root, manifest)
            extra.unlink()
            main.rename(src / 'renamed.cpp')
            with self.assertRaises(ValueError): baseline.verify(root, manifest)
            (src / 'renamed.cpp').unlink()
            with self.assertRaises(ValueError): baseline.verify(root, manifest)
            bad = copy.deepcopy(manifest)
            bad['protected_bots'] = {'../escape': {}}
            with self.assertRaises(ValueError): baseline.verify(root, bad)


if __name__ == '__main__': unittest.main()
