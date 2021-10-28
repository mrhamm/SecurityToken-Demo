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
        ensemble['token'].transferWithData(accounts[0],20,b'')

def test_unauthorizedReceiver(ensemble,accounts):
    initialize_account(ensemble,[accounts[0]])
    with brownie.reverts("Unauthorized Party."):
        ensemble['token'].transferWithData(accounts[2],20,b'',{'from':accounts[0]})

def test_unauthorizedSender(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    blacklist_account(ensemble,accounts[0])
    with brownie.reverts("Unauthorized Party."):
        ensemble['token'].transferWithData(accounts[1],20,b'',{'from':accounts[0]})

def test_insufficientBalance(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    with brownie.reverts("52"):
        ensemble['token'].unpause()
        ensemble['token'].transferWithData(accounts[1],200,b'')

def test_incorrectGranularity(ensemble,accounts):
    initialize_account(ensemble,[accounts[0],accounts[1]])
    with brownie.reverts("50"):
        ensemble['token'].unpause()
        ensemble['token'].transferWithData(accounts[1],22,b'')

def test_transferWithDataToZeroAddress(ensemble,accounts):
    zeroAddress = "0x0000000000000000000000000000000000000000"
    initialize_account(ensemble,[accounts[0],accounts[1],zeroAddress])
    with brownie.reverts("57"):
        ensemble['token'].transferWithData(zeroAddress,20,b'')

def test_transferWithDataBalance(ensemble,accounts):
    ensemble['token'].unpause({'from':accounts[0]})
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].transferWithData(accounts[2],10,b'',{'from':accounts[1]})
    assert ensemble['token'].balanceOf(accounts[1])==90, 'Did not transfer out.'
    assert ensemble['token'].balanceOf(accounts[2])==110, 'Did not transfer in.'

def test_twoPartitions(ensemble,accounts):
    ensemble['token'].unpause({'from':accounts[0]})
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].issueByPartition(b"Partition2",accounts[0],100,'')
    ensemble['token'].setDefaultPartitions([b'Holding',b'Partition2'])
    ensemble['token'].transferWithData(accounts[1],200,b'',{'from':accounts[0]})
    assert ensemble['token'].balanceOf(accounts[0])==0
    assert ensemble['token'].balanceOf(accounts[1])==300

def test_events(ensemble,accounts):
    ensemble['token'].unpause({'from':accounts[0]})
    initialize_account(ensemble,[accounts[0],accounts[1],accounts[2]])
    ensemble['token'].issueByPartition(b"Partition2",accounts[0],100,b'')
    ensemble['token'].setDefaultPartitions([b'Holding',b'Partition2'])
    tx = ensemble['token'].transferWithData(accounts[1],140,b'Data',{'from':accounts[0]})
    Events.check_transferEvent(tx,0,accounts[0],accounts[1],100)
    Events.check_transferByPartitionEvent(tx,1,b'Holding'.hex(),accounts[0],accounts[0],accounts[1],100,b'Data'.hex(),b''.hex())
    Events.check_transferEvent(tx,2,accounts[0],accounts[1],40)
    Events.check_transferByPartitionEvent(tx,3,b'Partition2'.hex(),accounts[0],accounts[0],accounts[1],40,b'Data'.hex(),b''.hex())
