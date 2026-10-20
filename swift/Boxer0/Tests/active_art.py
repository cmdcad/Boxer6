"""Resolve the active production art while retaining legacy-source fallback."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
def frame(name):
    if name.endswith('.png'): name = name[:-4]
    catalog = ROOT / f'Boxer0/Assets.xcassets/{name}.imageset/{name}.png'
    report = ROOT / 'ArtV2/UploadedSheet/integration_results.json'
    if report.exists():
        rows = json.loads(report.read_text())['assets']
        row = next((r for r in rows if r['catalog'] == name), None)
        if row:
            return ROOT / 'ArtV2/UploadedSheet' / row['source']
    return ROOT / f'IdleAnimation/frames/{name}.png'
