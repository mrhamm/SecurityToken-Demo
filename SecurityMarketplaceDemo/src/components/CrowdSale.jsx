import '../App.css';
import Web3 from 'web3';
import React, { Component } from 'react';
import RefundableCrowdSale from './ABI_Files/RefundableCrowdSale.json'
import Data from './Deployment_Data.json'
import PausableERC1400 from './ABI_Files/PausableERC1400.json'
require('dotenv').config();

class CrowdSale extends Component {
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
          window.alert('Non-Etherem browser detected.  You must not have a cryptocurrency wallet connected to the browser, you should consider trying MetaMask!')
        }
    }



    loadPage = async() => {
        await this.loadWeb3()
        if (this.state.connected){

        window.web3 = new Web3(window.ethereum)
        await window.ethereum.enable()
        const web3 = window.web3
        const saleAbi = RefundableCrowdSale.abi
        const saleAddress =  Data.Sale[0].address /* ropsten **/
        this.setState({address:saleAddress})
        const sale = new web3.eth.Contract(saleAbi,saleAddress)
        const start = await sale.methods.startTime().call()
        const end = await sale.methods.endTime().call()
        const goal = await sale.methods.goal().call()
        const weiRaised = await sale.methods.weiRaised().call()
        this.setState({goal:goal})
        this.setState({sales:weiRaised})
        this.setState({sale:sale})
        this.setState({startTime:start})
        this.setState({endTime:end})
       
    
        const tokenABI = PausableERC1400.abi
        const tokenAddress = Data.Tokens[0].token1
        const token = new web3.eth.Contract(tokenABI,tokenAddress)
        this.setState({Token_Contract:token})

        let balance = await token.methods.balanceOf(this.state.account).call()
        this.setState({balance: balance})
  }}

    buyToken = async(event) => {
        event.preventDefault()
        let amount = event.target.quantity.value
        amount = amount.toString()
        const web3 = window.web3
        web3.eth.handleRevert = true
        let tx = await web3.eth.sendTransaction({from: this.state.account, to: this.state.address, value: amount})
        window.alert("Tokens Purchased!")

    }
    finalize = async() => {
        const sale = this.state.sale
        await sale.methods.finalize().send({from:this.state.account})
        window.alert("You have finalized the sale!")
    }

    claimRefund = async(event) =>{
        event.preventDefault()
        const sale = this.state.sale
        await sale.methods.claimRefund().send({from: this.state.account})
        window.alert("Refund Claimed!")
    }

    updateTimers = async() => {
        const startDate = new Date(1000*this.state.startTime)
        const endDate = new Date(1000*this.state.endTime)
        let startTime = this.state.startTimer
        let endTime = this.state.endTimer
        let timeToStart = (startDate.getTime() - Date.now())/1000
        let timeToEnd = (endDate.getTime() - Date.now())/1000

        startTime.seconds = Math.floor(timeToStart%60)
        startTime.minutes = Math.floor((timeToStart%3600)/60)
        startTime.hours = Math.floor((timeToStart%86400)/3600)
        startTime.days = Math.floor((timeToStart%(86400*30))/86400)
        if(startTime.seconds <0){
            startTime.seconds =0
            startTime.minutes = 0
            startTime.hours = 0
            startTime.days = 0
        } 
        this.setState({endTimer:endTime})
        endTime.seconds = Math.floor(timeToEnd%60)
        endTime.minutes = Math.floor((timeToEnd%3600)/60)
        endTime.hours = Math.floor((timeToEnd%86400)/3600)
        endTime.days = Math.floor((timeToEnd%(86400*30))/86400)
        if(endTime.seconds <0){
            endTime.seconds =0
            endTime.minutes = 0
            endTime.hours = 0
            endTime.days = 0
        }
        this.setState({startTimer:startTime})
    }

    componentDidMount() {
        this.interval = setInterval(()=>{ 
        this.updateTimers()
       
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
        address: null,
        account: '0x                                     ',
        token: null,
        sale: null,
        balance: 0,
        networkID: null,
        connected: false,
        startTime: null,
        endTime: null,
        startTimer: {
            days: 0,
            hours: 0,
            minutes: 0,
            seconds: 0,
        },
        endTimer: {
            days: 0,
            hours: 0,
            minutes: 0,
            seconds: 0,
        },
        sales: 0,
        goal: 0,
        }  
    }
    render() { 
        let connectionMessage = <text className="text-danger">Not Connected</text>
        if (this.state.connected){
            connectionMessage = <text className="text-success">Connected</text>
        }
    return (
    
        <div className="row" style={{padding:"10px 10px 10px 10px"}}>
      
            <button className='column' onClick={this.loadPage}>Connect Wallet</button>
            <button className='column' onClick={this.loadPage}>Refresh</button>
            <div className='column'>
                <b>Time til' Crowd Sale Open:</b>                
                <br/>
                {this.state.startTimer.days}days{this.state.startTimer.hours}hours{this.state.startTimer.minutes}minutes{this.state.startTimer.seconds}seconds
            </div>
            <div className='column'>
                <b>Time til' Crowd Sale Close:</b>
                <br/>
                {this.state.endTimer.days}days{this.state.endTimer.hours}hours{this.state.endTimer.minutes}minutes{this.state.endTimer.seconds}seconds
                <br/>
                Tokens Sold: {this.state.sales}
                <br/>
                Goal: {this.state.goal}
                <br/>
                <br/>
                <button onClick={this.finalize}>Finalize</button>
            </div>

            <div style={{textAlign:'left'}}> 
                <b><u>Current Account:  </u></b><br/>
          
                {this.state.account}<br /> 
        
                <br />
                {connectionMessage}
                <br/>
                Token Balance: {this.state.balance}
                <br/>
                <br/>
                <b><u>Buy Tokens</u></b>
               <form onSubmit={this.buyToken}>
                    <label>Quantity</label><br/>
                    <input type="number" name="quantity" placeholder="Quantity"></input><br/><br/>
                    <button type = "submit">Buy</button>
               </form>
               <br/>
               <br/>
               
               
            </div>
        </div>
        
        );

    }
}

export default CrowdSale;