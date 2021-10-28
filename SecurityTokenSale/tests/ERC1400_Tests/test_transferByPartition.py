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
    ensemble['token'].setDefaultPartitions([])
    with brownie.reverts('ERC1400Pausable: token transfer while paused'): 
        ensemble['token'].transferByPartition(b'Holding',accounts[1],100,b'')
    
def test_unauthorizedSender(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].unpause()
    blacklist_account(ensemble,accounts[0])
    with brownie.reverts("Unauthorized Party."):
        ensemble['token'].transferByPartition(b'Holding',accounts[1],20,b'')

def test_unauthorizedReceiver(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].unpause()
    blacklist_account(ensemble,accounts[1])
    with brownie.reverts("Unauthorized Party."):
        ensemble['token'].transferByPartition(b'Holding',accounts[1],20,b'')

def test_insufficientBalance(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].unpause()
    with brownie.reverts("52"):
        ensemble['token'].transferByPartition(b'Holding',accounts[1],200,b'')

def test_nonExistentPartition(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].unpause()
    with brownie.reverts("52"):
        ensemble['token'].transferByPartition(b'Null',accounts[1],20,b'')

def test_incorrectGranularity(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].unpause()
    with brownie.reverts("50"):
        ensemble['token'].transferByPartition(b'Holding',accounts[1],22,b'')

def test_transferToZeroAddress(ensemble,accounts):
    zeroAddress = "0x0000000000000000000000000000000000000000"
    initialize_account(ensemble,[accounts[0],accounts[1],zeroAddress])
    with brownie.reverts("57"):
        ensemble['token'].transferByPartition(b'Holding',zeroAddress,20,b'')

def test_transferBalances(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].unpause()
    ensemble['token'].transferByPartition(b'Holding',accounts[1],50,b'')
    assert ensemble['token'].balanceOf(accounts[0])==50
    assert ensemble['token'].balanceOf(accounts[1]) == 150
    assert ensemble['token'].balanceOfByPartition(b'Holding',accounts[0]) == 50
    assert ensemble['token'].balanceOfByPartition(b'Holding',accounts[1]) == 150

def test_removePartitionFromAccount(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].unpause()
    ensemble['token'].transferByPartition(b'Holding',accounts[1],100,b'')
    partitions = ensemble['token'].partitionsOf(accounts[0])
    partitionString = '0x' + (64-len(b'Holding'.hex()))*"0" + b'Holding'.hex()
    assert  partitionString not in partitions 

def test_events(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    ensemble['token'].unpause()
    tx = ensemble['token'].transferByPartition(b'Holding',accounts[1],50,b'Data')
    Events.check_transferEvent(tx,0,accounts[0],accounts[1],50)
    Events.check_transferByPartitionEvent(tx,1,b'Holding'.hex(),accounts[0],accounts[0],accounts[1],50,b'Data'.hex(),b''.hex())