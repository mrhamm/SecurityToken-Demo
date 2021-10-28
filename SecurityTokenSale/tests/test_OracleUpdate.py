
import pytest 
from brownie import *

def test_oracleAddress(accounts, ensemble):
    
    assert KYCOracle.at(ensemble['oracleAddress'])==ensemble['oracle']

def test_oracleCallback(accounts,ensemble):
    ensemble['whitelist'].setOracleInstanceAddress(ensemble['oracleAddress'])
    assert ensemble['whitelist'].getCustomerAuthorization(accounts[0])== False
    tx = ensemble['whitelist'].updateKYC(accounts[0])
    id = tx.events['ReceivedNewRequestIdEvent'][0]['id']
    assert id == tx.events['GetKYCEvent'][0]['id']
    callerAddress = tx.events['GetKYCEvent'][0]['callerAddress']
    ensemble['oracle'].setKYC(True,1,callerAddress,id,accounts[0])
    assert ensemble['whitelist'].getCustomerId(accounts[0]) == 1
    assert ensemble['whitelist'].getCustomerAuthorization(accounts[0])== True

