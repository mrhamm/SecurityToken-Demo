import pytest
import brownie 
import hashlib


def test_setDocURI(ensemble,accounts):
    testDoc = b'This is a sample test document.'
    docHash = hashlib.sha256(testDoc).digest()
    ensemble['token'].setDocument(b'Test Document','Https://MrHamm.net',docHash,{'from':accounts[0]})
    document = ensemble['token'].getDocument(b'Test Document')
    assert document[0]== 'Https://MrHamm.net', 'Did not retrieve the correct documnent URI.'
    
def test_setDocHash(ensemble,accounts):
    testDoc = b'This is a sample test document.'
    docHash = hashlib.sha256(testDoc).hexdigest()
    ensemble['token'].setDocument(b'Test Document','Https://MrHamm.net',docHash,{'from':accounts[0]})
    document = ensemble['token'].getDocument(b'Test Document')
    hash = brownie.convert.datatypes.HexString(document[1],"bytes32")
    assert str(hash) == '0x' + docHash

def test_permissionlessSetDoc(ensemble,accounts):
    testDoc = b'This is a sample test document.'
    docHash = hashlib.sha256(testDoc).digest()
    with brownie.reverts(''):
        ensemble['token'].setDocument(b'Test Document','Https://MrHamm.net',docHash,{'from':accounts[1]})
    