import brownie 

def check_approvalByPartitionEvent(tx,n,_partition,_owner,_spender,_value):
    assert tx.events[n].name == "ApprovalByPartition" 
    assert tx.events[n].keys() == ['partition','owner','spender','value'] 
    assert brownie.convert.datatypes.HexString(tx.events[n]['partition'],"bytes32") == '0x'+ (len(_partition))%32 *"0" +  _partition
    assert tx.events[n]['owner'] == _owner
    assert tx.events[n]['spender'] == _spender
    assert tx.events[n]['value'] == _value

def check_documentEvent(tx,n,_name,_uri,_documentHash):
    assert tx.events[n].name == "Document" 
    assert tx.events[n].keys()==['name','uri','documentHash'] 
    assert tx.events[n]['name'] == _name 
    assert tx.events[n]['uri'] == _uri 
    assert tx.events[n]['documentHash'] == _documentHash

def check_transferByPartitionEvent(tx,n,_fromPartition,_operator,_from,_to,_value,_data,_operatorData):
    assert tx.events[n].name == "TransferByPartition" 
    assert tx.events[n].keys() == ['fromPartition','operator','from','to','value','data','operatorData'] 
    assert brownie.convert.datatypes.HexString(tx.events[n]['fromPartition'],"bytes32") == '0x' + (len(_fromPartition))%32*"0"+_fromPartition
    assert tx.events[n]['operator'] == _operator
    assert tx.events[n]['from'] == _from
    assert tx.events[n]['to'] == _to
    assert tx.events[n]['value'] == _value
    if len(_data)<=32:
        datatype = 'bytes32'
    else:
        datatype = "bytes"
    assert brownie.convert.datatypes.HexString(tx.events[n]['data'],datatype) == '0x' + (len(_data)%32)*"0" + _data
    assert brownie.convert.datatypes.HexString(tx.events[n]['operatorData'],'bytes32') == '0x'+(len(_operatorData)%32)*"0" + _operatorData

def check_changedPartitionEvent(tx,n,_fromPartition,_toPartition,_value):
    assert tx.events[n].name == "ChangedPartition" 
    assert tx.events[n].keys() == ['fromPartition','toPartition','value']
    assert brownie.convert.datatypes.HexString(tx.events[n]['fromPartition'],'bytes32') =='0x'+(len(_fromPartition)%32)*'0'+ _fromPartition
    assert brownie.convert.datatypes.HexString(tx.events[n]['toPartition'],'bytes32') == '0x' + (len(_toPartition)%32)*'0' + _toPartition
    assert tx.events[n]['value'] == _value


def check_authorizedOperatorEvent(tx,n,_operator,_tokenHolder):
    assert tx.events[n].name == "AuthorizedOperator" 
    assert tx.events[n].keys() == ['operator','tokenHolder']
    assert tx.events[n]['operator'] == _operator
    assert tx.events[n]['tokenHolder'] == _tokenHolder

def check_revokedOperatorEvent(tx,n,_operator,_tokenHolder):
    assert tx.events[n].name == "RevokedOperator" 
    assert tx.events[n].keys() == ['operator','tokenHolder']
    assert tx.events[n]['operator'] == _operator
    assert tx.events[n]['tokenHolder'] == _tokenHolder

def check_authorizedOperatorByPartitionEvent(tx,n,_partition,_operator,_tokenHolder):
    assert tx.events[n].name == "AuthorizedOperatorByPartition" 
    assert tx.events[n].keys() == ['partition','operator','tokenHolder']
    assert tx.events[n]['partition'] == _partition
    assert tx.events[n]['operator'] == _operator
    assert tx.events[n]['tokenHolder'] == _tokenHolder

def check_revokedOperatorByPartitionEvent(tx,n, _partition,_operator,_tokenHolder):
    assert tx.events[n].name == "RevokedOperatorByPartition" 
    assert tx.events[n].keys() == ['partition','operator','tokenHolder']
    assert tx.events[n]['partition']==_partition
    assert tx.events[n]['operator'] == _operator
    assert tx.events[n]['tokenHolder'] == _tokenHolder

def check_issuedEvent(tx,n,_operator,_from,_value,_data):
    assert tx.events[n].name == "Issued" 
    assert tx.events[n].keys() == ['operator','from','value','data']
    assert tx.events[n]['operator'] == _operator
    assert tx.events[n]['from'] == _from
    assert tx.events[n]['value'] == _value
    assert tx.events[n]['data'] == _data

def check_redeemedEvent(tx,n,_operator,_from,_value,_data):
    assert tx.events[n].name == "Redeemed" 
    assert tx.events[n].keys() == ['operator','from','value','data']
    assert tx.events[n]['operator'] == _operator
    assert tx.events[n]['from']== _from
    assert tx.events[n]['value'] == _value
    assert tx.events[n]['data'] == _data

def check_issuedByPartitionEvent(tx,n,_partition,_operator,_to,_value,_data,_operatorData):
    assert tx.events[n].name == "IssuedByPartition" 
    assert tx.events[n].keys() == ['partition','operator','to','value','data','operatorData']
    assert tx.events[n]['partition'] == _partition
    assert tx.events[n]['operator'] == _operator
    assert tx.events[n]['to'] == _to
    assert tx.events[n]['value'] == _value
    assert tx.events[n]['data'] == _data
    assert tx.events[n]['operatorData'] == _operatorData

def check_redeemedByPartitionEvent(tx,n,_partition,_operator,_from,_value,_operatorData):
    assert tx.events[n].name == "RedeemedByPartition" 
    assert tx.events[n].keys() == ['partition','operator','from','value','operatorData']
    assert tx.events[n]['partition'] == _partition
    assert tx.events[n]['operator'] == _operator
    assert tx.events[n]['from'] == _from
    assert tx.events[n]['value'] == _value
    assert tx.events[n]['operatorData'] == _operatorData

def check_transferEvent(tx,n,_from,_to,_value):
    assert tx.events[n].name == "Transfer"
    assert tx.events[n].keys() == ['from','to','value']
    assert tx.events[n]['from'] == _from
    assert tx.events[n]['to'] == _to
    assert tx.events[n]['value'] == _value

def check_approvalEvent(tx,n,_owner, _spender, _value):
    assert tx.events[n].name == "Approval"
    assert tx.events[n].keys() ==  ['owner','spender','value']
    assert tx.events[n]['owner'] == _owner
    assert tx.events[n]['spender'] == _spender
    assert tx.events[n]['value'] == _value 