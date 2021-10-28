import pytest
from brownie import PausableERC1400, accounts, RefundableCrowdSale
from brownie import KYCOracle, CallerContract
import time

duration = 1000
startDelay = 100

rate = 1
goal = 1000
granularity = 10

@pytest.fixture(scope="function",autouse=True)
def isolate(fn_isolation):
    pass

@pytest.fixture(scope="module")
def ensemble():
    start = int(time.time())+startDelay
    end = start + duration
    whitelist = CallerContract.deploy({'from':accounts[0]})
    oracle = KYCOracle.deploy({'from':accounts[0]})
    whitelistAddress = accounts[0].get_deployment_address(0)
    token = PausableERC1400.deploy('TestToken','TT',granularity,[accounts[0],accounts[-1]],[b'Holding'],whitelistAddress,{'from':accounts[0]})
    tokenAddress = accounts[0].get_deployment_address(2)
    crowdSale = RefundableCrowdSale.deploy(start,end,rate,accounts[0],tokenAddress,goal,{'from':accounts[0]})
    crowdSaleAddress = accounts[0].get_deployment_address(3)
    oracleAddress = accounts[0].get_deployment_address(1)
    ensemble = {}
    ensemble['whitelist']= whitelist
    ensemble['oracle'] = oracle
    ensemble['token'] = token
    ensemble['oracleAddress'] = oracleAddress
    ensemble['crowdSale'] = crowdSale
    ensemble['crowdSaleAddress']=crowdSaleAddress
    ensemble['granularity'] = granularity
    return ensemble


