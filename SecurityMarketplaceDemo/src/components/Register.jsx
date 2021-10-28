import '../App.css';
import Web3 from 'web3';
import React, { Component } from 'react';
import ERC1400 from './ABI_Files/ERC1400.json'
import CALLER from './ABI_Files/CallerContract.json'
import Data from './Deployment_Data.json'
require('dotenv').config();

class Register extends Component {

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
          window.alert('Non-Etherem browser detected.  You must not have a cryptocurrency wallet connected to the browser, you should consider trying MetaMask!')}
      }
    
    
      loadPage = async() => {
        await this.loadWeb3()
        if (this.state.connected){
    
        window.web3 = new Web3(window.ethereum)
        await window.ethereum.enable()
        const web3 = window.web3
        const Abi = ERC1400.abi
        
        const address =  Data.Tokens[0].token1 /* ropsten **/
        const token = new web3.eth.Contract(Abi,address)
        this.setState({contract:token})
        
        const callerAddress = Data.Whitelist[0].address
        const callerAbi = CALLER.abi
    
        const caller = new web3.eth.Contract(callerAbi,callerAddress)
        this.setState({caller:caller})
    
    
        let balance = await token.methods.balanceOf(this.state.account).call()
        
        this.setState({balance: balance})
       
        let authorization = await caller.methods.isAuthorized(this.state.account).call()
        this.setState({authorization:authorization})
      
          
       
      
      
      }}
      
      mintToken = async(event) =>{
        event.preventDefault()
        if(this.state.contract){
            const token = this.state.contract
            const to = event.target.to.value
            const amount = event.target.quantity.value
            await token.methods.issue(to,amount,"0x00").send({from:this.state.account})
            window.alert("Your token has been minted!")
            this.loadPage()
        }else{window.alert("You need to connect to do that!")}
    }
      transferToken = async(event) =>{
        event.preventDefault()
        if(this.state.contract){
          const token = this.state.contract
          const to = event.target.to.value
          const amount = event.target.quantity.value
          await token.methods.transfer(to,amount).send({from:this.state.account})
          window.alert("Your transfer is complete!")
          this.loadPage()
    
        }else{window.alert("You need to connect to do that!")}
      }
    
      operatorTransfer = async(event) => {
        event.preventDefault()
        if(this.state.contract){
          const token = this.state.contract
          const to = event.target.to.value
          const amount = event.target.quantity.value
          const from = event.target.from.value 
          await token.methods.transferFrom(from,to,amount).send({from:this.state.account})
          window.alert("You have transfered your client's funds!")
          this.loadPage()
        }else{window.alert("You need to connect to do that!")}
      }
      
      checkKYC = async(event) =>{
        event.preventDefault()
        if(this.state.caller){
          const caller = this.state.caller
          await caller.methods.updateKYC(this.state.account).send({from:this.state.account})
          window.alert("Oracle has been contacted")
          this.loadPage()
        }
      }
    
      componentDidMount() {
          this.interval = setInterval(()=>{ 
            this.loadPage()
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
          account2: Data.accounts[0].address,
          account3: Data.accounts[1].address,
          contract: null,
          caller: null,
          networkId: 0,
          connected: false,
          items: false,
          balance: 0,
          balance2: 0,
          balance3: 0,
          score: 0,
          grindReset: undefined,
          authorization: false,
          auth2: false,
          auth3: false,
          operator: false,
          
    
         
       }  
      }
    render() {
        let connectionMessage = <text className="text-danger">Not Connected</text>
        if (this.state.connected){
            connectionMessage = <text className="text-success">Connected</text>
        }
        let authorization = <text className="text-danger">Not Authorized</text>
        if (this.state.authorization){
          authorization = <text className="text-success">Authorized</text>
        }

        return(


        <main>
      
            <div className="row" style={{padding:"10px 10px 10px 10px"}}>
          
                <button  onClick={this.loadPage}>Connect Wallet</button>
                <button  onClick={this.loadPage}>Refresh</button>
                <div> 
                    <b><u>Current Account:  </u></b><br/>
            
                    {this.state.account}<br /> 
          
                    <br />
                    {connectionMessage}
                    <br />
                    Authorized: {authorization}
                    <br/>
                    
               <    b><u>Register Account</u></b>
                    <form onSubmit ={this.checkKYC}>
                        <label>Account</label><br/>
                        <input type="text" name="account" placeholder="Address"></input><br/>
                        <button type="submit">Register</button>
                    </form>

                </div>
            </div>
          </main>
        );
    }

}
export default Register;