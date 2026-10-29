import io,json,shutil,subprocess,zipfile
from pathlib import Path
import pytest

@pytest.mark.skipif(not shutil.which('node'),reason='Optional Node.js check for the browser ZIP writer')
def test_browser_zip_crc_and_utf8_roundtrip():
    source=(Path(__file__).parents[1]/'web/zip.js').read_text()
    expected={'M1_R0001.csv':'participant_id,score\n1,6.1234\n','metadata.json':'{"note":"心理学 — fictional"}','large.txt':'0123456789'*50000}
    script=source+'\nmakeZip('+json.dumps(expected)+').arrayBuffer().then(b=>process.stdout.write(Buffer.from(b)));'
    result=subprocess.run(['node'],input=script.encode(),capture_output=True,check=True)
    with zipfile.ZipFile(io.BytesIO(result.stdout)) as z:
        assert z.testzip() is None
        assert set(z.namelist())==set(expected)
        for name,text in expected.items():assert z.read(name).decode()==text
