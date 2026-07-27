from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[1]

def test_ecosystem_integrity_gate():
    result=subprocess.run([sys.executable,str(ROOT/'tools/check_repository_integrity.py'),'--check','ecosystem'],cwd=ROOT,text=True,capture_output=True)
    assert result.returncode==0, result.stdout+result.stderr

def test_support_matrix_is_truthful():
    text=(ROOT/'docs/ecosystem/SUPPORT_MATRIX.md').read_text(encoding='utf-8')
    assert 'Implemented' in text
    assert 'Foundation' in text
    assert 'Planned' in text
    assert 'BTDoor Security+' in text

def test_product_documents_have_contract_sections():
    required=('## Status','## Capability scope','## Home Assistant mapping principles','## Dependencies and acceptance','## Related documentation')
    for path in (ROOT/'docs/ecosystem').glob('*.md'):
        if path.name in {'README.md','SUPPORT_MATRIX.md','CAPABILITY_MODEL.md','ADAPTER_CONTRACT.md','DISCOVERY_AND_IDENTITY.md'}: continue
        text=path.read_text(encoding='utf-8')
        assert all(x in text for x in required), path.name
