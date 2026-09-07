from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib,json
ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'godaddy'
target=ROOT/'DEDAK-GoDaddy.zip'
with ZipFile(target,'w',ZIP_DEFLATED) as z:
    for p in sorted(source.rglob('*')):
        if p.is_file():z.write(p,p.relative_to(source).as_posix())
with ZipFile(target) as z:
    assert z.testzip() is None
    assert 'index.html' in z.namelist() and '.htaccess' in z.namelist()
    for name in z.namelist():assert z.read(name)==(source/name).read_bytes()
    count=len(z.namelist())
print(json.dumps({'archive':str(target),'files':count,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},indent=2))
