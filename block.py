"""
http://bit.ly/pytest-feb-15-2018

Coin - chain of signatures
Chain - seq of hash(block, prev_hash)
Proof of Work - (POW) - Hash that starts with zero's
Block - header (hash, nonce), data

>>> node = Node('matt')
>>> gb, hash = node.process_txns([])
>>> # Pay Fred .1
>>> txn = Transaction([Amount(1, 'matt')],
...     [Amount(.9, 'matt'), Amount(.1, 'fred')])
>>> b2, h2 = node.process_txns([txn])
>>> b2 # doctest: +ELLIPSIS
<__main__.Block object at 0x...>
   
>>> h2[0]
'0'

"""

import hashlib
import json

MINING_COST = 1


class Amount:
    """
    >>> a = Amount(5, 'matt')
    >>> a.todict()
    {'uuid': 'matt', 'amount': 5}
    """
    def __init__(self, amount, uuid):
        self.amount = amount
        self.uuid = uuid

    def __eq__(self, other):
        return self.uuid == other.uuid and \
               self.amount == other.amount

    def todict(self):
        return {
            'uuid': self.uuid,
            'amount': self.amount
        }

    @classmethod
    def fromdict(cls, d):
        return cls(**d)


class Transaction:
    """
    A transaction consists of list of inputs (Amounts)
    and outputs (Amounts)
    
    >>> t = Transaction([Amount(.4, 'matt'),
    ...     Amount(.6, 'matt')],
    ...     [Amount(.7, 'fred'), Amount('.3', 'matt')])
    >>> t.todict()
    {'inputs': [{'uuid': 'matt', 'amount': 0.4}, {'uuid': 'matt', 'amount': 0.6}], 'outputs': [{'uuid': 'fred', 'amount': 0.7}, {'uuid': 'matt', 'amount': '.3'}]}
    """
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

    def __eq__(self, other):
        return self.inputs == other.inputs and \
               self.outputs == other.outputs

    def todict(self):
        return {
            'inputs':
            [i.todict() for i in self.inputs],
            'outputs':
            [o.todict() for o in self.outputs]
        }

    @classmethod
    def fromdict(cls, d):
        inputs = [Amount.fromdict(a) for a in d['inputs']]
        outputs = [Amount.fromdict(a) for a in d['outputs']]
        txn = cls(inputs, outputs)
        return txn


class Block:
    """
    >>> b = Block([], '', 1)
    >>> h = b.get_hash(53)
    >>> h.startswith('0')
    True
    """
    def __init__(self, txns, prev_hash,
                 difficulty):
        self.txns = txns
        self.prev_hash = prev_hash
        self.nonce = None
        self.difficulty = difficulty

    def __eq__(self, other):
        return self.prev_hash == other.prev_hash and \
               self.txns == other.txns

    @classmethod
    def fromdict(cls, d):
        prev_hash = d['header']['prev_hash']
        difficulty = d['header']['difficulty']
        txns = [Transaction.fromdict(x) for x in d['body']['txns']]
        b = cls(txns, prev_hash, difficulty)
        return b

    def dumps(self):
        data = self.todict(self.nonce)
        return json.dumps(data, sort_keys=True)

    def todict(self, nonce):
        body = {
            'txns':
            [t.todict() for t in self.txns]
        }
        header = {
            'prev_hash': self.prev_hash,
            'body_hash': get_hash(body),
            'difficulty': self.difficulty,
            'nonce': nonce
        }
        return {'header': header, 'body': body}

    def get_hash(self, nonce):
        return get_hash(self.todict(nonce))

def to_db(db_con, blocks):
    cur = db_con.cursor()
    for b in blocks:
        data = b.dumps()
        cur.execute(f"INSERT INTO Blocks VALUES(0, '{data}')")

def from_db(db_con):
    blocks = []
    cur = db_con.cursor()
    rows = cur.execute('SELECT * FROM Blocks').fetchall()
    for row in rows:
        blocks.append(Block.fromdict(json.loads(row[1])))
    return blocks

def get_hash(data_dict):
    """
    >>> get_hash({'foo': 3})   
    '01b1fc25f60c0debc2446b2653ef8cfbf872e958bff11551a3d135a2b461c849'
    """
    sha = hashlib.sha256()
    sha.update(str(data_dict).encode('utf8'))
    return sha.hexdigest()


class Node:
    def __init__(self, uuid):
        self.uuid = uuid
        self.blocks = []  # BLOCKCHAIN!!!

    def process_txns(self, txns, difficulty=1):
        # payment to ourself
        txns.insert(
            0,
            Transaction(
                [],
                [Amount(MINING_COST, self.uuid)]))
        # prev hash
        if self.blocks:
            prev_hash = self.blocks[-1].prev_hash
        else:  # genesis block
            prev_hash = ''
        block = Block(txns, prev_hash, difficulty)
        nonce = 0
        while True:
            hash = block.get_hash(nonce)
            if hash.startswith('0' * difficulty):
                block.nonce = nonce
                self.blocks.append(block)
                return block, hash
            nonce += 1


if __name__ == '__main__':
    import doctest
    doctest.testmod()
