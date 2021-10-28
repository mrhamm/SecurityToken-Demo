
import '../App.css';
import Web3 from 'web3';
import React, { Component } from 'react';
import ERC1400 from './ABI_Files/ERC1400.json'
import Pair from './ABI_Files/UniswapV2Pair.json'
import Data from './Deployment_Data.json'
require('dotenv').config();


class Exchange extends Component {
    loadWeb3 = async() => {
        if (window.ethereum) {
          window.web3 = new Web3(window.ethereum)
          await window.ethereum.enable()
          const web3 = window.web3
          const accounts = await web3.eth.getAccounts()
          this.setState({account: accounts[0]})
          const networkId = await web3.eth.net.getId()
          this.setState({networkId: networkId})
          this.setState({connected:true})
          
          
        }
        else if (window.web3) {
          window.web3 = new Web3(window.web3.currentProvider)
          const web3 = window.web3
          const accounts = await web3.eth.getAccounts()
          this.setState({account: accounts[0]})
          const networkId = await web3.eth.net.getId()
          this.setState({networkId: networkId})
          this.setState({connected:true})
          
         
        }
        else {
          window.alert('Non-Ethereum browser detected.  You must not have a cryptocurrency wallet connected to the browser, you should consider trying MetaMask!')}
      }
    
    
    
      loadPage = async() => {
        await this.loadWeb3()
        if (this.state.connected){
    
        window.web3 = new Web3(window.ethereum)
        await window.ethereum.enable()
        const web3 = window.web3
        const Abi = ERC1400.abi
        
        const address1 =  Data.Tokens[0].token1 /* ropsten **/
        const token1 = new web3.eth.Contract(Abi,address1)
        this.setState({address1:address1})
        this.setState({token1:token1})
        
        const address2 = Data.Tokens[0].token2
        const token2 = new web3.eth.Contract(Abi,address2)
        this.setState({token2:token2})
        
        let balance1 = await token1.methods.balanceOf(this.state.account).call()
        let balance2 = await token2.methods.balanceOf(this.state.account).call()
        this.setState({balance1: balance1})
        this.setState({balance2: balance2})  

        let pairAddress = Data.Pair[0].address
        let pairABI = Pair.abi
        let pair = new web3.eth.Contract(pairABI,pairAddress)
        let token0 = await pair.methods.token0().call()
        this.setState({token0:token0})
        this.setState({PairContract: pair})
        this.setState({Pair: pairAddress})
        let tx = await pair.methods.getReserves().call()
  
        let pairB1 = tx[0]
        let pairB2 = tx[1]
        if(this.state.token0 === address2){
          pairB1 = tx[1]
          pairB2 = tx[0]
        }
        this.setState({poolBalance1:pairB1})
        this.setState({poolBalance2:pairB2})
      }}

      getTokens = async(event) => {
          event.preventDefault() 
          const token = this.state.token2
          await token.methods.issue(this.state.account,10000000,"0x00").send({from:this.state.account})
          window.alert("You now have HAMM Tokens!")
      }

      addLiquidity = async(event) => {
          event.preventDefault()
          let amt1 = event.target.amount1.value
          let amt2 = event.target.amount2.value 
          let token1 = this.state.token1
          let token2 = this.state.token2
          let pairAddress = this.state.Pair
          let pair = this.state.PairContract
          await token1.methods.transfer(pairAddress,amt1).send({from:this.state.account})
          await token2.methods.transfer(pairAddress,amt2).send({from:this.state.account})
          await pair.methods.mint(this.state.account).send({from:this.state.account})
          window.alert("Liquidity Added")
          this.loadPage()
      }
      
      buyBSIS = async(event) => {
          event.preventDefault()
          const BSIamt = event.target.BSIamount.value
          let pair = this.state.PairContract
          const token2 = this.state.token2
          
          const inputHAMM = 1 +  Math.floor(BSIamt*this.state.poolBalance2*1000/((this.state.poolBalance1-BSIamt)*997))
          await token2.methods.transfer(this.state.Pair,inputHAMM).send({from:this.state.account})
          if (this.state.token0===this.state.address1){
            await pair.methods.swap(BSIamt,0,this.state.account,"0x00").send({from: this.state.account})
          }else {
            await pair.methods.swap(0,BSIamt,this.state.account,"0x00").send({from: this.state.account})

          }
          
          window.alert("Swapped for BSIS Token")
      }
      
    

      buyHAMM = async(event) => {
        event.preventDefault()
        const HAMMamt = event.target.HAMMamount.value
        let pair = this.state.PairContract
        const token1 = this.state.token1
        
        const inputBSI = 1 + Math.floor(HAMMamt*this.state.poolBalance1*1000/((this.state.poolBalance2-HAMMamt)*997))
        await token1.methods.transfer(this.state.Pair,inputBSI).send({from:this.state.account})
        if (this.state.token0===this.state.address1){
          await pair.methods.swap(0,HAMMamt,this.state.account,"0x00").send({from:this.state.account})
        } else {
          await pair.methods.swap(HAMMamt,0,this.state.account,"0x00").send({from:this.state.account})
        }

        
        
        window.alert("Swapped for HAMM Token")
    }
    
      componentDidMount() {
          this.interval = setInterval(()=>{ 
            
          //****Insert Repeated Action Here */
            
          },1000);
        }
      
        componentWillUnmount() {
          if (this.interval) {
              clearInterval(this.interval);
          }
      }
    
      constructor(props) {
        super(props)
        this.state = {
    
          account: '0x                                     ',
          address1: null,
          token0: null,
          token1: null,
          token2: null,
          networkId: 0,
          connected: false,
          balance1: 0,
          balance2: 0,
          poolBalance1: 0,
          poolBalance2: 0,
          pair: null,
          PairContract:null,

        }  
      }
      
    
      render() {
      
      let connectionMessage = <text className="text-danger">Not Connected</text>
      if (this.state.connected){
          connectionMessage = <text className="text-success">Connected</text>
      }
     
      return (
        
             <main>
          
            <div className="row" style={{padding:"10px 10px 10px 10px"}}>
          
                <button className="column" onClick={this.loadPage}>Connect Wallet</button>
                <button  className="column" onClick={this.loadPage}>Refresh</button>
                <div className="column">
                    <b><u>Exchange Pair Info</u></b>
                    <br/>
                    BSIS Tokens: {this.state.poolBalance1}
                    <br/>
                    HAMM Tokens: {this.state.poolBalance2}
                    <br/>
                    BSIS-HAMM Price: {this.state.poolBalance2/this.state.poolBalance1}
        
                </div>
                <div className="column">
                <b><u>Add Liquidity to Exchange</u></b>
                <form onSubmit={this.addLiquidity}>
                    <label>Token 1</label><br/>
                    <input type="number" name= "amount1" placeholder ="Amount"></input><br/>
                    <label>Token 2</label><br/>
                    <input type="number" name="amount2" placeholder="Amount"></input><br/>
                    <button type = "submit">Send</button>
               </form>
               <br/>
               
               <br/>

                </div>
                <div style={{textAlign: 'left'}}> 
                  <b><u>Current Account:  </u></b><br/>
            
                  {this.state.account}<br /> 
          
                 <br />
                  {connectionMessage}
                  <br/>
                  BSIS Token Balance: {this.state.balance1}
                  <br/>
                  HAMM Token Balance: {this.state.balance2}
                  <br/>
                  <button onClick={this.getTokens}>Get HAMM Tokens</button>
                </div>
                <br/>
                
                <div style={{textAlign:'left'}}>
                <br/>
                <br/> 
                <b><u>Swap BSIS-HAMM (Buy BSIS)</u></b>
               <br/>
               <form onSubmit={this.buyBSIS} id="buyBSI">
                    <label>Amount</label><br/>
                    <input type="number" name= "BSIamount" placeholder ="Amount"></input><br/>
                    <button type = "submit" form = "buyBSI">Send</button>
                </form>
                <br/>
                <b><u>Swap HAMM-BSIS (Buy HAMM)</u></b>
                <br/>
               <form onSubmit={this.buyHAMM} id = "buyHamm">
                    <label>Amount</label><br/>
                    <input type="number" name= "HAMMamount" placeholder ="Amount"></input><br/>
                    <button type = "submit" form = "buyHamm">Send</button>
                </form>
                </div>
            </div>
    
          
          
              
          
         
    
         
        
          
          
    
          </main>
      
        
      );
    }
}

export default Exchange;