import pytest
import brownie
from brownie.network.state import Chain

def initialize_sale(ensemble,accounts):
    ensemble['token'].addSeller(ensemble['crowdSaleAddress'],{'from':accounts[0]})
    
def approve_account(ensemble,accounts):
    ensemble['whitelist'].setOracleInstanceAddress(ensemble['oracleAddress'])
    for account in accounts:
        tx = ensemble['whitelist'].updateKYC(account)
        id = tx.events['ReceivedNewRequestIdEvent'][0]['id']
        callerAddress = tx.events['GetKYCEvent'][0]['callerAddress']
        ensemble['oracle'].setKYC(True,1,callerAddress,id,account)

def test_tokenSale(ensemble,accounts):
    approve_account(ensemble,[accounts[0],accounts[1],ensemble['crowdSaleAddress']])
    ensemble['token'].addMinter(ensemble['crowdSaleAddress'],{"from":accounts[0]})
    chain = Chain()
    chain.sleep(200)
    accounts[0].transfer(ensemble['crowdSaleAddress'],"10 wei")
    assert ensemble['token'].balanceOf(accounts[0],{'from':accounts[0]}) == 10

def test_saleTime(ensemble,accounts):
    approve_account(ensemble,[accounts[0],accounts[1],ensemble['crowdSaleAddress']])
    ensemble['token'].addMinter(ensemble['crowdSaleAddress'],{"from":accounts[0]})
    chain = Chain()
    with brownie.reverts("Invalid Purchase"):
        accounts[0].transfer(ensemble['crowdSaleAddress'],"1 ether")
    chain.sleep(2000)
    with brownie.reverts("Invalid Purchase"):
        accounts[0].transfer(ensemble['crowdSaleAddress'],"1 ether")

def test_zeroEther(ensemble,accounts):
    approve_account(ensemble,[accounts[0],accounts[1],ensemble['crowdSaleAddress']])
    ensemble['token'].addMinter(ensemble['crowdSaleAddress'],{"from":accounts[0]})
    chain = Chain()
    chain.sleep(200)
    with brownie.reverts("Invalid Purchase"):
        accounts[0].transfer(ensemble['crowdSaleAddress'],"0 ether")

def test_unPause(ensemble,accounts):
    initialize_sale(ensemble,accounts)
    approve_account(ensemble,[accounts[0],accounts[1],ensemble['crowdSaleAddress']])
    ensemble['token'].addMinter(ensemble['crowdSaleAddress'],{"from":accounts[0]})
    chain = Chain()
    chain.sleep(200)
    accounts[0].transfer(ensemble['crowdSaleAddress'],"10 wei")
    with brownie.reverts("ERC1400Pausable: token transfer while paused"):
        ensemble['token'].transfer(accounts[1],10)
    chain.sleep(2000)
    ensemble['crowdSale'].finalize({'from':accounts[0]})
    ensemble['token'].transfer(accounts[1],10)
    assert ensemble['token'].balanceOf(accounts[1])==10 
    assert ensemble['token'].balanceOf(accounts[0])==0

def test_refund(ensemble,accounts):
    initialize_sale(ensemble,accounts)
    approve_account(ensemble,[accounts[0],accounts[1],ensemble['crowdSaleAddress']])
    ensemble['token'].addMinter(ensemble['crowdSaleAddress'],{"from":accounts[0]})
    chain = Chain()
    chain.sleep(200)
    accounts[0].transfer(ensemble['crowdSaleAddress'],"10 wei")
    chain.sleep(5000)
    ensemble['crowdSale'].finalize({'from':accounts[0]})
    ensemble['crowdSale'].claimRefund({'from':accounts[0]})
    assert ensemble['crowdSale'].getTotal({'from':accounts[0]}) ==0
