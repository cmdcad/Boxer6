"""Approved palette-only variants of established guard/recoil poses."""
import json
import generate_bidirectional as palette

def main():
    variants=[]
    for clip in ['guard','block_jab','block_cross']:
        for i in range(3):
            source=f'{clip}_b_{i}';target=f'{clip}_a_{i}'
            palette.variant(source,target,(231,119,40),(40,118,210))
            variants.append({'source':source,'target':target})
    (palette.ROOT/'player_guard_manifest.json').write_text(json.dumps({'canvas':[512,512],'root':[256,448],'variants':variants},indent=2)+'\n')
    print('Generated nine approved palette variants; all poses unchanged.')
if __name__=='__main__':main()
