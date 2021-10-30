pragma solidity ^0.8.0;

import "../Token/PausableERC1400.sol";
import "OpenZeppelin/openzeppelin-contracts@4.3.0/contracts/utils/math/SafeMath.sol";
import "../Token/IERC1400.sol";

contract CrowdSale  {
    using SafeMath for uint256;

    

    // start and end timestamps where investments are allowed (both inclusive)
    uint256 public startTime;
    uint256 public endTime;
    IERC1400 public token;
  // address where funds are collected
    address payable public wallet;

  // how many token units a buyer gets per wei
    uint256 public rate;

  // amount of raised money in wei
    uint256 public weiRaised;


    event TokenPurchase(address indexed purchaser, address indexed beneficiary, uint256 value, uint256 amount);

    constructor(uint256 _startTime, uint256 _endTime, uint256 _rate, address _wallet, address tokenAddress) {
    require(_startTime >= block.timestamp,'Invalid Start');
    require(_endTime >= _startTime, 'Invalid end');
    require(_rate > 0, 'Invalid Rate');
    require(_wallet != address(0), 'Invalid wallet');

    token = createTokenContract(tokenAddress);
    startTime = _startTime;
    endTime = _endTime;
    rate = _rate;
    wallet = payable(_wallet);

  }

   // creates the token to be sold.
  // override this method to have crowdsale of a specific mintable token.
  function createTokenContract(address tokenAddress) internal returns (IERC1400) {
      token = IERC1400(tokenAddress);
    return token;
  }


  // fallback function can be used to buy tokens
  fallback () external payable {
    buyTokens(msg.sender);
  }
  receive () external payable {
      buyTokens(msg.sender);
  }

  // low level token purchase function
  function buyTokens(address beneficiary) public payable {
    require(beneficiary != address(0));
    require(validPurchase(),"Invalid Purchase");

    uint256 weiAmount = msg.value;

    // calculate token amount to be created
    uint256 tokens = weiAmount.mul(rate);

    // update state
    weiRaised = weiRaised.add(weiAmount);

    token.issue(beneficiary, tokens,'');
    emit TokenPurchase(msg.sender, beneficiary, weiAmount, tokens);

    forwardFunds();
  }

  // send ether to the fund collection wallet
  // override to create custom fund forwarding mechanisms
  function forwardFunds() internal {
    wallet.transfer(msg.value);
  }

  // @return true if the transaction can buy tokens
  function validPurchase() internal view returns (bool) {
    bool withinPeriod = block.timestamp >= startTime && block.timestamp <= endTime;
    bool nonZeroPurchase = msg.value != 0;
    return withinPeriod && nonZeroPurchase;
  }

  // @return true if crowdsale event has ended
  function hasEnded() public view returns (bool) {
    return block.timestamp > endTime;
  }



}