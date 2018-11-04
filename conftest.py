import block

import pytest

@pytest.fixture(scope='session')
def node():
    node = block.Node('matt')
    return node
