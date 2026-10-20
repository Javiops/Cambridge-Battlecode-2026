import struct

import pytest

from lab import replay


def fixture(inputs):
    mp=b'w62pam\0\0'+bytes(10)
    return b'a62per\0\0'+struct.pack('<I',1)+bytes([0,3])+mp+struct.pack('<I',len(inputs))+b''.join(inputs),mp


def test_decodes_native_serializer_fixtures():
    blob,mp=fixture([b'\x04\x01'+struct.pack('<i',5)+b'\xff',b'\x03\x00',
        b'\x00\x01'+struct.pack('<ii',2,3),b'\x00\x02\x02'+struct.pack('<II',9,65535),
        b'\x00\x03'+struct.pack('<I',1)+b'\x01'+struct.pack('<Iii',7,-1,-1),
        b'\x00\x06'+struct.pack('<II',0,1),b'\x00\x07',b'\x00\x0b'+struct.pack('<I',2)])
    actions=replay.decode(blob,mp)
    assert actions[0]['pick']==5
    assert actions[2]=={'kind':'move','x':2,'y':3}
    assert actions[3]=={'kind':'attack','target':{'kind':2,'id':9}}
    assert actions[4]=={'kind':'cast','slot':1,'target':{'kind':1,'id':7}}
    assert actions[-2]=={'kind':'cancel'}


def test_replay_rejects_truncation_unknown_inputs_and_wrong_map():
    b,mp=fixture([b'\x00\x01'+struct.pack('<ii',1,2)])
    with pytest.raises(ValueError,match='Truncated'):replay.decode(b[:-1],mp)
    with pytest.raises(ValueError,match='map'):replay.decode(b,b'other')
    b,mp=fixture([b'\x02\x00'])
    with pytest.raises(ValueError,match='Unsupported'):replay.decode(b,mp)


def test_extra_bytes_are_not_silently_ignored():
    b,mp=fixture([b'\x03\x01'])
    assert replay.decode(b,mp)[0]=={'kind':'wait','reason':1}
    with pytest.raises(ValueError,match='Trailing'):replay.decode(b+b'junk',mp)
