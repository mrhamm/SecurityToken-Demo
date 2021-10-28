# import the following dependencies
import json
from web3 import Web3
import asyncio
from brownie import accounts, Contract






# add your blockchain connection information
infura_url = 'http://127.0.0.1:8545'
web3 = Web3(Web3.HTTPProvider(infura_url))

# uniswap address and abi
with open('Deployment_Data.json') as json_file:
    data = json.load(json_file)
callerFile = open('../build/contracts/CallerContract.json')
callerBuild = json.load(callerFile)
callerABI = callerBuild["abi"]
oracleFile = open('../build/contracts/KYCOracle.json')
oracleBuild = json.load(oracleFile)
oracleABI = oracleBuild["abi"]
callerAddress = data['Whitelist'][0]['address']
oracleAddress = data['Oracle'][0]['address']
    #token = Contract.from_abi("ERC1400",tokenAddress,tokenABI)
    #oracle = Contract.from_abi("KYCOracle",oracleAddress,oracleABI)

caller = web3.eth.contract(address=callerAddress, abi=callerABI)
oracle = Contract.from_abi("KYCOracle",oracleAddress,oracleABI)
registry = {}
registry['0x7C8aA676A58ed46B4Fbc2F1E2d3cFa3577d45D4E'] = True
registry[data['accounts'][0]['address']] = True
registry[data['accounts'][1]['address']] = True
# define function to handle events and print to the console
def handle_event(event):
    print(event["args"]["id"])
    # and whatever
    print(event["args"]["customer"])
    print(event["address"])
    oracle.setKYC(registry[event["args"]["customer"]],  1, event["address"],  event["args"]["id"], event["args"]["customer"],{"from":accounts[0]})

    print("EVENT!!")


# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for Event in event_filter.get_new_entries():
            handle_event(Event)
        await asyncio.sleep(poll_interval)


# when main is called
# create a filter for the latest block and look for the "PairCreated" event for the uniswap factory contract
# run an async loop
# try to run the log_loop function above every 2 seconds
def main():
    event_filter = caller.events.ReceivedNewRequestIdEvent.createFilter(fromBlock='latest')
    #block_filter = web3.eth.filter('latest')
    # tx_filter = web3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter, 2)))
                # log_loop(block_filter, 2),
                # log_loop(tx_filter, 2)))
    finally:
        # close loop to free up system resources
        loop.close()


if __name__ == "__main__":
    main()