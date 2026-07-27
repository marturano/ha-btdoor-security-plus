from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]

def load_checker():
    spec=importlib.util.spec_from_file_location('integrity',ROOT/'tools/check_repository_integrity.py')
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def test_all_repository_integrity_gates_pass():
    mod=load_checker()
    failures=[]
    for name,fn in mod.CHECKS.items():
        res=fn()
        if res['status']!='PASS': failures.append((name,res['errors']))
    assert not failures

def test_roadmap_documentation_platform_is_4_4():
    text=(ROOT/'docs/roadmap/ROADMAP_4X.md').read_text(encoding='utf-8')
    assert '## 4.4 — Documentation Platform' in text
    assert text.count('## 4.3 —') == 1
