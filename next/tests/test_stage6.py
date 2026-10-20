import struct
import pytest
from lab import stage6


def record(probe=0):
    return b'S6D!'+struct.pack('<14I',1,0,0,0,0xffffffff,0,0,0,0,100,200,300,probe,200000).hex().encode()+b'\n'


def test_trace_rejects_missing_duplicate_and_truncated_records():
    with pytest.raises(ValueError):stage6.parse_log(record(1))
    with pytest.raises(ValueError):stage6.parse_log(record()+record())
    with pytest.raises(ValueError):stage6.parse_log(record()+b'incomplete')


def test_fuel_gate_requires_complete_turns_and_headroom():
    d,f=stage6.parse_log(record()+b'S6F!'+struct.pack('<5I',1,0,200000,400,1).hex().encode()+b'\n')
    assert stage6.fuel_summary(d,f,90000,180000)['first_turn_max']==400
    with pytest.raises(ValueError):stage6.fuel_summary(d,{},90000,180000)
    f['1/0']['used']=180001
    with pytest.raises(ValueError):stage6.fuel_summary(d,f,90000,180000)


def test_seed_uses_geometry_and_lcg_wraps():
    terrain=dict(width=4,height=3,walls=[[1,2]],holes=[],altars=[[2,1]])
    assert stage6.map_seed(terrain)==stage6.map_seed(terrain)
    assert stage6.map_seed(terrain)!=stage6.map_seed(terrain|{'holes':[[0,0]]})
    assert stage6.next_random(0xffffffff)==1012239698


def test_hex_trace_survives_timeline_separators():
    d,f=stage6.parse_log(b'\0\0'+record().replace(b'ff',b'f\0f')+b'\0')
    assert d['1/0/0']['pick']==-1


def test_official_fuel_includes_logging_and_end_turn():
    header=b'a62leuf\0\0\0\1'+bytes([0,0])+struct.pack('<4Q',1000000,100000,200000,100000)*2
    footer={'1/0':dict(budget=200000,used=80000,count=1)}
    assert stage6.official_fuel(header+struct.pack('<4Q',100,100,100,81000),footer,90000,180000)['initial_max']==81000
    with pytest.raises(ValueError):stage6.official_fuel(header+struct.pack('<4Q',100,100,100,180001),footer,90000,180000)
