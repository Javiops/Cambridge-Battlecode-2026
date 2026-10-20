"""Fail-closed decoder for inputs serialized by the pinned official engine.

Field layouts are checked against native Game_SaveReplay fixtures and a native
timeline replay. The embedded map must match the supplied immutable map bytes.
No observations or labels are inferred from visual positions or final winners.
"""
import struct


def decode(data: bytes, map_bytes: bytes) -> list[dict]:
    if data[:8]!=b'a62per\0\0' or data[8:12]!=struct.pack('<I',1) or data[12:14]!=b'\0\3' or data[14:14+len(map_bytes)]!=map_bytes:
        raise ValueError('Unsupported replay header or embedded map mismatch')
    pos=14+len(map_bytes)
    def take(fmt):
        nonlocal pos
        n=struct.calcsize(fmt)
        if pos+n>len(data):raise ValueError('Truncated replay input')
        v=struct.unpack_from(fmt,data,pos);pos+=n
        return v[0] if len(v)==1 else v
    def target():
        kind,index=take('<B'),take('<I')
        return {'kind':kind,'id':index} if kind else None
    count=take('<I')
    if count>2_000_000:raise ValueError('Unsupported replay input count')
    actions=[]
    for _ in range(count):
        category=take('<B')
        if category==3:
            action={'kind':'wait','reason':take('<B')}
        elif category==4:
            variant=take('<B')
            if variant!=1:raise ValueError('Unsupported draft input variant')
            action={'kind':'draft','pick':take('<i'),'reason':take('<B')}
        elif category==0:
            kind=take('<B')
            if kind==0:action={'kind':'priority','priority':take('<i')}
            elif kind in (1,5,10):
                action={'kind':{1:'move',5:'submit',10:'ward'}[kind],'x':take('<i'),'y':take('<i')}
            elif kind==2:
                action={'kind':'attack','target':target()}
                take('<I')  # Serialized attack metadata; SDK action accepts only the typed target.
            elif kind==3:
                action={'kind':'cast','slot':take('<I')};t=target();x,y=take('<ii')
                if t:action['target']=t
                if x!=-1 or y!=-1:action.update(x=x,y=y)
            elif kind in (4,7):action={'kind':{4:'recall',7:'cancel'}[kind]}
            elif kind in (6,8):action={'kind':{6:'buy',8:'buy_consumable'}[kind],'item':take('<I'),'count':take('<I')}
            elif kind==9:action={'kind':'use_consumable','item':take('<B'),'x':take('<i'),'y':take('<i')}
            elif kind==11:action={'kind':'sell','item':take('<I')}
            else:raise ValueError(f'Unsupported action tag {kind} at byte {pos-1}')
        else:raise ValueError(f'Unsupported input category {category} at byte {pos-1}')
        actions.append(action)
    if pos!=len(data):raise ValueError(f'Trailing replay bytes ({len(data)-pos}); unsupported format')
    return actions
