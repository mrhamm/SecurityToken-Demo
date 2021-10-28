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
      
def test_lockup(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].setDefaultPartitions([])  
    with brownie.reverts("55"):
        ensemble['token'].transferFromWithData(accounts[1],accounts[0],100,b'')

def test_unauthorizedReceiver(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    with brownie.reverts('Unauthorized Party.'):
        ensemble['token'].transferFromWithData(accounts[1],accounts[2],100,b'')

def test_unauthorizedFrom(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    blacklist_account(ensemble,accounts[1])
    with brownie.reverts('Unauthorized Party.'):
        ensemble['token'].transferFromWithData(accounts[1],accounts[0],100,b'')

def test_unauthorizedOperator(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    blacklist_account(ensemble,accounts[0])
    with brownie.reverts("Unauthorized Party."):
        ensemble['token'].transferFromWithData(accounts[1],accounts[2],100,b'')
    
def test_operatorTransferBalance(ensemble,accounts):
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].transferFromWithData(accounts[1],accounts[0],100,b'')
    assert ensemble['token'].balanceOf(accounts[1]) == 0
    assert ensemble['token'].balanceOf(accounts[0]) == 200

def test_operatorInsufficientBalance(ensemble,accounts):
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],accounts[1]])
    with brownie.reverts("52"):
        ensemble['token'].transferFromWithData(accounts[1],accounts[0],200,b'')

def test_operatorIncorrectGranularity(ensemble,accounts):
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],accounts[1]])
    with brownie.reverts("50"):
        ensemble['token'].transferFromWithData(accounts[1],accounts[0],22,b'')
    
def test_operatorToZeroAddress(ensemble,accounts):
    zeroAddress = "0x0000000000000000000000000000000000000000"
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],zeroAddress, accounts[1]])
    with brownie.reverts("57"):
        ensemble['token'].transferFromWithData(accounts[1],zeroAddress,100,b'')

def test_notOperator(ensemble,accounts):
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],accounts[1]])
    with brownie.reverts("53"):
        ensemble['token'].transferFromWithData(accounts[0],accounts[1],100,b'',{'from':accounts[1]})

def test_allowance(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    tx = ensemble['token'].approve(accounts[2],50,{'from':accounts[1]})
    assert ensemble['token'].allowance(accounts[1],accounts[2]) == 50
    Events.check_approvalEvent(tx,0,accounts[1],accounts[2],50)

def test_allowZeroAddress(ensemble,accounts):
    zeroAddress = "0x0000000000000000000000000000000000000000"
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],zeroAddress, accounts[1]])
    with brownie.reverts("56"):
        ensemble['token'].approve(zeroAddress,100,{'from':accounts[1]})

def test_changeAllowance(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].approve(accounts[2],50,{'from':accounts[1]})
    assert ensemble['token'].allowance(accounts[1],accounts[2]) == 50
    ensemble['token'].approve(accounts[2],100,{'from':accounts[1]})
    assert ensemble['token'].allowance(accounts[1],accounts[2]) == 100

def test_operatorTwoPartitions(ensemble,accounts):
    ensemble['token'].unpause({'from':accounts[0]})
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].issueByPartition(b"Partition2",accounts[1],100,'')
    ensemble['token'].setDefaultPartitions([b'Holding',b'Partition2'])
    ensemble['token'].transferFromWithData(accounts[1],accounts[0],200,b'',{'from':accounts[0]})
    assert ensemble['token'].balanceOf(accounts[1])==0
    assert ensemble['token'].balanceOf(accounts[0])==300

def test_allowedTransferBalance(ensemble,accounts):
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].approve(accounts[2],50,{'from':accounts[1]})
    ensemble['token'].transferFromWithData(accounts[1],accounts[0],50,b'',{'from':accounts[2]})
    assert ensemble['token'].balanceOf(accounts[1]) == 50
    assert ensemble['token'].balanceOf(accounts[0])== 150
    assert ensemble['token'].allowance(accounts[1],accounts[2]) == 0

def test_insufficientAllowance(ensemble,accounts):
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].approve(accounts[2],50,{'from':accounts[1]})
    with brownie.reverts("53"):
        ensemble['token'].transferFromWithData(accounts[1],accounts[0],100,b'',{'from':accounts[2]})

def test_allowedInsufficientBalance(ensemble,accounts):
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].approve(accounts[2],150,{'from':accounts[1]})
    with brownie.reverts('52'):
        ensemble['token'].transferFromWithData(accounts[1],accounts[0],150,b'',{'from':accounts[2]})

def test_allowedToZeroAddress(ensemble,accounts):
    zeroAddress = "0x0000000000000000000000000000000000000000"
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2],zeroAddress])
    ensemble['token'].approve(accounts[2],150,{'from':accounts[1]})
    with brownie.reverts("57"):
        ensemble['token'].transferFromWithData(accounts[1],zeroAddress,100,b'',{'from':accounts[2]})

def test_allowedIncorrectGranularity(ensemble,accounts):
    ensemble['token'].unpause()
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].approve(accounts[2],100,{'from':accounts[1]})
    with brownie.reverts("50"):
        ensemble['token'].transferFromWithData(accounts[1],accounts[0],22,b'',{'from':accounts[2]})

def test_allowedTwoPartitions(ensemble,accounts):
    ensemble['token'].unpause({'from':accounts[0]})
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].issueByPartition(b"Partition2",accounts[1],100,'')
    ensemble['token'].setDefaultPartitions([b'Holding',b'Partition2'])
    ensemble['token'].approve(accounts[2],200,{'from':accounts[1]})
    ensemble['token'].transferFromWithData(accounts[1],accounts[0],200,b'',{'from':accounts[2]})
    assert ensemble['token'].balanceOf(accounts[1])==0
    assert ensemble['token'].balanceOf(accounts[0])==300

def test_operatorEvents(ensemble,accounts):
    ensemble['token'].unpause({'from':accounts[0]})
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].issueByPartition(b"Partition2",accounts[1],100,'')
    ensemble['token'].setDefaultPartitions([b'Holding',b'Partition2'])
    tx = ensemble['token'].transferFromWithData(accounts[1],accounts[0],200,b'Data',{'from':accounts[0]})
    Events.check_transferEvent(tx,0,accounts[1],accounts[0],100)
    Events.check_transferByPartitionEvent(tx,1,b'Holding'.hex(),accounts[0],accounts[1],accounts[0],100,b'Data'.hex(),b''.hex())
    Events.check_transferEvent(tx,2,accounts[1],accounts[0],100)
    Events.check_transferByPartitionEvent(tx,3,b'Partition2'.hex(),accounts[0],accounts[1],accounts[0],100,b'Data'.hex(),b''.hex())

def test_allowedEvents(ensemble,accounts):
    ensemble['token'].unpause({'from':accounts[0]})
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].issueByPartition(b"Partition2",accounts[1],100,'')
    ensemble['token'].setDefaultPartitions([b'Holding',b'Partition2'])
    tx1 = ensemble['token'].approve(accounts[2],200,{'from':accounts[1]})
    Events.check_approvalEvent(tx1,0,accounts[1],accounts[2],200)
    tx2 = ensemble['token'].transferFromWithData(accounts[1],accounts[0],200,b'Data',{'from':accounts[2]})
    Events.check_transferEvent(tx2,0,accounts[1],accounts[0],100)
    Events.check_transferByPartitionEvent(tx2,1,b'Holding'.hex(),accounts[2],accounts[1],accounts[0],100,b'Data'.hex(),b''.hex())
    Events.check_transferEvent(tx2,2,accounts[1],accounts[0],100)
    Events.check_transferByPartitionEvent(tx2,3,b'Partition2'.hex(),accounts[2],accounts[1],accounts[0],100,b'Data'.hex(),b''.hex())

