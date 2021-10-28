from brownie import accounts, CallerContract, KYCOracle, PausableERC1400, RefundableCrowdSale, UniswapV2Factory, ERC1400
import brownie
import time 
import json 
import shutil
metaMaskAddress = '0x7C8aA676A58ed46B4Fbc2F1E2d3cFa3577d45D4E' #REPLACE THIS WITH YOUR BROWSER'S METAMASK WALLET ADDRESS!!!
start = time.time() + 60
end = start + 60
rate = 1
goal = 1000000

def approve_account(caller,oracle,accounts):
    for account in accounts:
        tx = caller.updateKYC(account)
        id = tx.events['ReceivedNewRequestIdEvent'][0]['id']
        callerAddress = tx.events['GetKYCEvent'][0]['callerAddress']
        oracle.setKYC(True,1,callerAddress,id,account)
        
def main():
    caller = CallerContract.deploy({'from':accounts[0]})
    callerAddress = accounts[0].get_deployment_address(0)

    token1 = PausableERC1400.deploy('Company Token','Co.',1,[metaMaskAddress],[b'default',b'partition2',b'partition3'],callerAddress,{'from':accounts[0]})
    token1Address = accounts[0].get_deployment_address(1)
    token2 = ERC1400.deploy('Hamm Token','HAMM',1,[metaMaskAddress],[b'default',b'partition2',b'partition3'],callerAddress,{'from':accounts[0]})
    token2Address = accounts[0].get_deployment_address(2)

    crowdSale = RefundableCrowdSale.deploy(start,end,rate,accounts[0],token1Address,goal,{'from':accounts[0]})
    crowdSaleAddress = accounts[0].get_deployment_address(3)

    oracle = KYCOracle.deploy({"from":accounts[0]})
    oracleAddress = accounts[0].get_deployment_address(4)

    factory = UniswapV2Factory.deploy(accounts[0],{'from':accounts[0]})
    factoryAddress = accounts[0].get_deployment_address(5)

    tx = factory.createPair(token1,token2,{'from':accounts[0]})
    pairAddress = tx.events['PairCreated'][0]['pair']

    crowdSale.transferOwnership(metaMaskAddress,{'from':accounts[0]})
    token1.addMinter(metaMaskAddress,{'from':accounts[0]})
    factory.setFeeTo(accounts[0],{'from':accounts[0]})
    token1.addMinter(crowdSaleAddress,{'from':accounts[0]})
    token1.addSeller(crowdSaleAddress,{'from':accounts[0]})
    token2.addMinter(metaMaskAddress,{'from':accounts[0]})
    accounts[0].transfer(metaMaskAddress,"1 ether")
    caller.setOracleInstanceAddress(oracleAddress,{'from':accounts[0]})
    approve_account(caller,oracle,[crowdSaleAddress,pairAddress])
    ABI_Files = ['../build/contracts/CallerContract.json', '../build/contracts/KYCOracle.json','../build/contracts/PausableERC1400.json',
    '../build/contracts/RefundableCrowdSale.json','../build/contracts/UniswapV2Factory.json','../build/contracts/UniswapV2Pair.json','../build/contracts/ERC1400.json']

    for f in ABI_Files:
        shutil.copy(f,'../../SecurityMarketplaceDemo/src/components/ABI_Files')

    data = {}
    data['Whitelist'] = []
    data['Whitelist'].append({'address': callerAddress})

    data['Oracle'] = []
    data['Oracle'].append({'address':oracleAddress})

    data['Factory'] = []
    data['Factory'].append({'address':factoryAddress})

    data['Tokens'] = []
    data['Tokens'].append({'token1': token1Address, 'token2':token2Address})

    data['accounts'] = []
    for account in accounts:
        data['accounts'].append({'address': str(account)})

    data['Pair'] = []
    data['Pair'].append({'address':pairAddress})

    data['Sale'] = [{'address':crowdSaleAddress}]

    with open('Deployment_Data.json', 'w') as outfile:
        json.dump(data, outfile)
    with open('../../SecurityMarketplaceDemo/src/components/Deployment_Data.json','w') as outfile:
        json.dump(data,outfile)
    
    
    