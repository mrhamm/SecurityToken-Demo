## Ethereum Security Token CrowdSale

### Prerequisites
This repository requires Node.js, the Ethereum-Brownie package and the Ganache Ethereum Client.  The demo requires a browser with an ethereum enabled wallet, we suggest MetaMask.  After installing the most recent version of Node.js:
<br/>
To install Eth-Brownie see:<link> https://eth-brownie.readthedocs.io/en/stable/install.html</link>
<br/>
To install Ganache-Cli: `npm install -g ganache-cli`
<br/>
Install the front-end dependencies (may replace yarn with npm):

```shell 
cd SecurityMarketplaceDemo
yarn install
```

## The Demo

Demo will launch a sample of a token crowdsale.  
### Initializing Demo Parameters
First, in a text-editor open the file: `SecurityTokenSale/scripts/FullDemoLaunch.py` <br/>
Replace the variable "MetaMaskAddress" with your respesctive metamask wallet address. <br/>
The values of "StartDelay" and "Duration" will denote how many seconds the initial crowdsale takes to start and then the final duration.  We have set the demo to start the sale 90 seconds after launch and then the sale is open for a duration of 2 minutes - change these values to your own flavor.

### Start the Ganache Client
Before launching the demo, open a terminal and run: `ganache-cli`
### Connect and Reset your MetaMask Wallet
Open your browser's metamask wallet.  Choose the connection options menu -> Add Custom RPC -> Set the URL to localhost:8545.  Choose localhost:8545 to connect to the ganache-cli instance.  Before starting the demo choose MetaMask->settings->Advanced->Reset Account.  This must be reset each time the demo is run to avoid nonce errors. 
### Launch the demo contracts and start the oracle
Open a new terminal and run the following from this directory
```shell
cd SecurityTokenSale/scripts
brownie run FullDemoLaunch.py
brownie run EventListener.py
```
This will inject ganache with the relevant contract codes, save the relevant ABIs to the front-end folder, and run the whitelist oracle
### Open the Client Web-app
Open a new terminal and rune the following from this directory (may replace yarn with npm)
```shell
cd SecurityMarketplaceDemo
yarn start
```
### Follow the demo script
Once the contracts are launched, the demo has a 90 second timer before purchase is allowed.  Follow these steps in the web-browswer app:
<br/>
1. Register your metamask with the oracle: Navigate to "Register" and connect to the page. Paste your metamask address into the box and submit.  The oracle will be contacted and eventually approve your account
<br/>
2. Purchasing tokens: Navigate to "CrowdSale."  Connect to the page.  The timer will indicate if the crowdsale has started or ended.  Once the sale has started, you may purchase with the purchase form.  Purchase at least the "Goal" value of tokens.
<br/>
3. Finalizing CrowdSale: The transfer/trade features will be disabled til the crowdsale ends.  Once the sale time is over, select the "Finalize" button to end the sale. 
<br/>
4. Trade Demo:  Navigate to "Minter" and connect to the page. We have initialized some metamask addresses for the page to track.  You can transfer to these addresses, but only if they are first approved by the oracle.  Approve an address by copying and pasting into the "resgister" form and submit.  The oracle will eventually approve the account.  Once approved, the account can accept incoming transfers with the "transfer" form.  The metamask address has operator permissions and can transfer tokens on the behalf of others, assuming both the sender and receiver are registered with the oracle.  
<br/>
5. Marketplace Demo: Navigate to "Marketplace" and connect to the page.  This is an example of a Uniswap pair.  Mint HAMM tokens for the pair by clicking the button on the left, soon you will be credited some tokens for testing.  Once credited, add liquidity to the swap pool by using the form.  Once liquidity is added the "swap" forms on the bottom left will be functional to submit trades.

## Closing Demo and Cleaning up
<br/>
1. Stop the front-end: In the terminal for the web app, run ctrl+c to stop the app.
<br/>
2. Stop Ganache-cli: In the ganache terminal run ctrl+c to stop the ganache blockchain
<br/>
3. Stop the oracle: The oracle should have automatically disconnected and stopped, but in case it didnt stop it with ctrl+c
<br/>
4. Reset metamask wallet: Since it needs reset every time you run the demo, go ahead and choose Metamask->settings->advanced->Reset Account

## Unit Tests
A non-comprehensive set of unit tests are available in the brownie project.  To run tests:
```shell
cd SecurityTokenSale/tests
brownie test
```
To run a single test `brownie test test_name`