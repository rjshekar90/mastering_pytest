import os
import sqlite3

import block

import pytest


@pytest.mark.addfunc
@pytest.mark.subfunc
def test_add():
    res = 2 + 3
    assert res == 5

@pytest.mark.addfunc
@pytest.mark.subfunc
def test_sub():
    res = 2 - 3
    assert res == -1


@pytest.fixture
def genesis_block(node):
    gb, hash = node.process_txns([])
    return gb

@pytest.fixture
def block2(node):
    txn = block.Transaction([block.Amount(5, 'matt')],
            [block.Amount(4, 'fred'), block.Amount(1, 'matt')])
    b2, h2 = node.process_txns([txn])
    return b2

def test_difficulty(node):
    gb, hash = node.process_txns([], difficulty=2)
    assert hash[:2] == '00'

    
def test_bad_difficulty(node):
    with pytest.raises(TypeError):
        gb, hash = node.process_txns([], difficulty='2')


def test_genesis_block(genesis_block):
    hash = genesis_block.get_hash(genesis_block.nonce)
    assert hash[0] == '0'

def test_txn(block2):
    b2 = block2
    h2 = b2.get_hash(b2.nonce)
    assert h2[0] == '0'

# create a block2 fixture

@pytest.mark.parametrize('d, h',
    [({}, '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a'),
     ({'name': 'matt'}, '9ea24fe0487df4c29f0f45a4b2ab359aa7127631eda08bcb4ce1be48e0ab0fd2')])
def test_get_hash(d, h):
    res = block.get_hash(d)
    assert res == h

@pytest.fixture
def sqlite_con():    
    try:
        con = sqlite3.connect('test_db')
        cur = con.cursor()
        cur.execute('CREATE TABLE Blocks(id INTEGER PRIMARY KEY, data TEXT)')
        con.commit()
        yield con
    finally:
        os.remove('test_db')

def test_db(sqlite_con, node, genesis_block):
    block.to_db(sqlite_con, [genesis_block])
    blocks = block.from_db(sqlite_con)
    assert blocks[0] == genesis_block
    assert os.path.exists('test_db')
        
def bar(x, y):
    return x + y

def test_mp(monkeypatch):
    block.foo = 1
    monkeypatch.setattr(block, 'foo', bar)
    res = block.foo(4, 5)
    assert res == 9

def test_wo_mp():
    with pytest.raises(TypeError):
        block.foo(4, 5)


