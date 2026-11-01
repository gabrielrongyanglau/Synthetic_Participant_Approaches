"""Every element the page scripts look up by id exists in index.html, so a removed element cannot break a button."""
import re,pathlib
WEB=pathlib.Path(__file__).resolve().parent.parent/'web'

def test_script_ids_exist_in_page():
    ids=set(re.findall(r'id="([^"]+)"',(WEB/'index.html').read_text()))
    for name in ['app.js','research.js','console.js','study-charts.js','zip.js']:
        s=(WEB/name).read_text()
        used=set(re.findall(r"\$\('([A-Za-z0-9_-]+)'\)",s))|set(re.findall(r"getElementById\('([A-Za-z0-9_-]+)'\)",s))
        assert not used-ids,(name,sorted(used-ids))
