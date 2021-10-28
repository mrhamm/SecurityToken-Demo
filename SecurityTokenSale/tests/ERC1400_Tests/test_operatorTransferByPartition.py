import brownie 
import Events as Events

def initialize_account(ensemble,accounts):
    ensemble['whitelist'].setOracleInstanceAddress(ensemble['oracleAddress'])
    for account in accounts:
        tx = ensemble['whitelist'].updateKYC(account)
        id = tx.events['ReceivedNewRequestIdEvent'][0]['id']
        callerAddress = tx.events['GetKYCEvent'][0]['callerAddress']
        ensemble['oracle'].setKYC(True,1,callerAddress,id,account)
        if account!= "0x0000000000000000000000000000000000000000":
         ensemble['token'].issueByPartition(b'Holding',account,100,b'')
         ensemble['token'].setDefaultPartitions([b'Holding'])

def blacklist_account(ensemble,account):
     ensemble['whitelist'].setOracleInstanceAddress(ensemble['oracleAddress'])
     tx = ensemble['whitelist'].updateKYC(account)
     id = tx.events['ReceivedNewRequestIdEvent'][0]['id']
     callerAddress = tx.events['GetKYCEvent'][0]['callerAddress']
     ensemble['oracle'].setKYC(False,1,callerAddress,id,account)
      

def test_pause(ensemble,accounts): #this function should be considered more carefully.  currently, partitions can be transfered during the "lockup" period but not during a pause
    initialize_account(ensemble,[accounts[0],accounts[1]])
    with brownie.reverts('ERC1400Pausable: token transfer while paused'): 
        ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[0],100,b'',b'')
    

def test_unauthorizedReceiver(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    with brownie.reverts('Unauthorized Party.'):
        ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[2],100,b'',b'')

def test_unauthorizedFrom(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    blacklist_account(ensemble,accounts[1])
    with brownie.reverts('Unauthorized Party.'):
        ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[0],100,b'',b'')

def test_unauthorizedOperator(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    blacklist_account(ensemble,accounts[0])
    with brownie.reverts("Unauthorized Party."):
        ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[2],100,b'',b'')

def test_operatorTransferBalance(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].unpause()
    ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[2],50,b'',b'')
    assert ensemble['token'].balanceOfByPartition(b'Holding',accounts[1]) == 50
    assert ensemble['token'].balanceOfByPartition(b'Holding',accounts[2]) == 150

def test_operatorInsufficientBalance(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].unpause()
    with brownie.reverts("52"):
        ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[0],150,b'',b'')

def test_operatorIncorrectGranularity(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].unpause()
    with brownie.reverts("50"):
        ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[0],22,b'',b'')

def test_operatorToZeroAddress(ensemble,accounts):
    zeroAddress = "0x0000000000000000000000000000000000000000"
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],zeroAddress, accounts[1]])
    with brownie.reverts("57"):
        ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],zeroAddress,50,b'',b'')

def test_notOperator(ensemble,accounts):
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],accounts[1]])
    with brownie.reverts("53"): #this error code is not quite consistent due to an or statement in the contract
        ensemble['token'].operatorTransferByPartition(b'Holding',accounts[0],accounts[1],50,b'',b'',{'from':accounts[1]})

def test_partitionAllowance(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    tx = ensemble['token'].approveByPartition(b'Holding',accounts[1],50,{'from':accounts[0]})
    assert ensemble['token'].allowanceByPartition(b'Holding',accounts[0],accounts[1]) == 50
    assert ensemble['token'].allowanceByPartition(b'Null',accounts[0],accounts[1]) == 0 
    Events.check_approvalByPartitionEvent(tx,0,b'Holding'.hex(),accounts[0],accounts[1],50)

def test_changePartitionAllowance(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].approveByPartition(b'Holding',accounts[1],50,{'from':accounts[0]})
    assert ensemble['token'].allowanceByPartition(b'Holding',accounts[0],accounts[1]) == 50
    ensemble['token'].approveByPartition(b'Holding',accounts[1],100,{'from':accounts[0]})
    assert ensemble['token'].allowanceByPartition(b'Holding',accounts[0],accounts[1]) == 100

def test_allowZeroAddres(ensemble,accounts):
    zeroAddress = "0x0000000000000000000000000000000000000000"
    initialize_account(ensemble,[accounts[0],zeroAddress, accounts[1]])
    with brownie.reverts("56"):
        ensemble['token'].approveByPartition(b'Holding',zeroAddress,50)

def test_allowedTransferBalance(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].unpause()
    ensemble['token'].approveByPartition(b'Holding',accounts[2],100,{'from':accounts[1]})
    ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[0],100,b'',b'',{'from':accounts[2]})
    assert ensemble['token'].balanceOfByPartition(b'Holding',accounts[1])==0
    assert ensemble['token'].balanceOfByPartition(b'Holding',accounts[0]) ==200

def test_insufficientAllowance(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].unpause()
    ensemble['token'].approveByPartition(b'Holding',accounts[2],50,{'from':accounts[1]})
    with brownie.reverts("53"):
        ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[0],100,b'',b'',{'from':accounts[2]})

def test_allowedInsufficientBalance(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].unpause()
    ensemble['token'].approveByPartition(b'Holding',accounts[2],150,{'from':accounts[1]})
    with brownie.reverts("52"):
        ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[0],150,b'',b'',{'from':accounts[2]})

def test_allowedIncorrectGranularity(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].unpause()
    ensemble['token'].approveByPartition(b'Holding',accounts[2],50,{'from':accounts[1]})
    with brownie.reverts("50"):
        ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[0],22,b'',b'',{'from':accounts[2]})

def test_allowedToZeroAddress(ensemble,accounts):
    zeroAddress = "0x0000000000000000000000000000000000000000"
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],zeroAddress, accounts[1],accounts[2]])
    ensemble['token'].approveByPartition(b'Holding',accounts[2],50,{'from':accounts[1]})
    with brownie.reverts("57"):
        ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],zeroAddress,50,b'',b'',{'from':accounts[2]})
    
def test_operatorEvents(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].unpause()
    tx = ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[2],50,b'Data',b'OperatorData')
    Events.check_transferEvent(tx,0,accounts[1],accounts[2],50)
    Events.check_transferByPartitionEvent(tx,1,b'Holding'.hex(),accounts[0],accounts[1],accounts[2],50,b'Data'.hex(),b'OperatorData'.hex())

def test_allowedEvents(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].unpause()
    tx = ensemble['token'].approveByPartition(b'Holding',accounts[2],100,{'from':accounts[1]})
    Events.check_approvalByPartitionEvent(tx,0,b'Holding'.hex(),accounts[1],accounts[2],100)
    tx2 = ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[0],100,b'Data',b'OperatorData',{'from':accounts[2]})
    Events.check_transferEvent(tx2,0,accounts[1],accounts[0],100)
    Events.check_transferByPartitionEvent(tx2,1,b'Holding'.hex(),accounts[2],accounts[1],accounts[0],100,b'Data'.hex(),b'OperatorData'.hex())

def test_operatorTransferChangePartitions(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].unpause()
    flag = 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
    newPartition = b'NewPartition'
    newPartition = (32-len(newPartition))*b'0' + newPartition
    data = bytes.fromhex(flag) 
    data = data + newPartition
    tx = ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[2],50,data,b'OperatorData')
    assert len(tx.events)==3
    assert ensemble['token'].balanceOfByPartition(newPartition,accounts[2])==50
    Events.check_transferEvent(tx,0,accounts[1],accounts[2],50)
    Events.check_transferByPartitionEvent(tx,1,b'Holding'.hex(),accounts[0],accounts[1],accounts[2],50,data.hex(),b'OperatorData'.hex())
    Events.check_changedPartitionEvent(tx,2,b'Holding'.hex(),newPartition.hex(),50)

def test_allowedTransferChangePartitions(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].unpause()
    ensemble['token'].approveByPartition(b'Holding',accounts[2],100,{'from':accounts[1]})
    flag = 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
    newPartition = b'NewPartition'
    newPartition = (32-len(newPartition))*b'0' + newPartition
    data = bytes.fromhex(flag) 
    data = data + newPartition
    tx = ensemble['token'].operatorTransferByPartition(b'Holding',accounts[1],accounts[0],50,data,b'OperatorData',{'from':accounts[2]})
    assert len(tx.events)==3
    assert ensemble['token'].balanceOfByPartition(newPartition,accounts[0])==50
    Events.check_transferEvent(tx,0,accounts[1],accounts[0],50)
    Events.check_transferByPartitionEvent(tx,1,b'Holding'.hex(),accounts[2],accounts[1],accounts[0],50,data.hex(),b'OperatorData'.hex())
    Events.check_changedPartitionEvent(tx,2,b'Holding'.hex(),newPartition.hex(),50)