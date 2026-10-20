"""Install prepared V2 catalogs, backing up every affected catalog first."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile
from PIL import Image

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
CATALOG = ROOT/'Boxer0/Assets.xcassets'

def main():
    manifest=json.loads((BASE/'StageF/manifest.json').read_text())
    entries=[]
    for row in manifest['frames']:
        orange=BASE/'StageF'/row['output']
        blue=BASE/row['source']
        orange_name=orange.stem
        blue_name=orange_name.replace('_b_', '_a_')
        entries.extend([(blue,blue_name,row['source_sha256']),(orange,orange_name,row['output_sha256'])])
    assert len(entries)==148 and len({name for _,name,_ in entries})==148
    for source,name,digest in entries:
        assert hashlib.sha256(source.read_bytes()).hexdigest()==digest, source
        im=Image.open(source)
        assert im.mode=='RGBA' and im.size==(512,512),source
    backup=BASE/'pre_v2_live_assets.zip'
    # Immutable first-install snapshot: reruns cannot overwrite the rollback point.
    if not backup.exists():
        with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
            for _,name,_ in entries:
                folder=CATALOG/(name+'.imageset')
                if folder.exists():
                    for file in folder.rglob('*'):
                        if file.is_file(): z.write(file,file.relative_to(CATALOG))
    results=[]
    for source,name,digest in entries:
        folder=CATALOG/(name+'.imageset'); folder.mkdir(exist_ok=True)
        target=folder/(name+'.png')
        shutil.copyfile(source,target)
        contents={'images':[{'filename':target.name,'idiom':'universal','scale':'1x'}], 'info':{'author':'xcode','version':1}}
        (folder/'Contents.json').write_text(json.dumps(contents,indent=2)+'\n')
        assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
        results.append({'catalog':name,'source':str(source.relative_to(BASE)).replace('\\','/'),'sha256':digest})
    (BASE/'integration_results.json').write_text(json.dumps({'passed':True,'installed_frames':148,'canvas':[512,512],'root':[256,448],'rollback_archive':backup.name,'apple_build':'not run; Windows host','assets':results},indent=2))
    print('PASS: installed and hash-verified 148 V2 frames; original catalogs backed up.')

if __name__=='__main__': main()
