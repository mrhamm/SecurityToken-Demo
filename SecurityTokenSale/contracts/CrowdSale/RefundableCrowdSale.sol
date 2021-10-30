pragma solidity ^0.8.0;

import "./FinalizableCrowdSale.sol";
import "OpenZeppelin/openzeppelin-contracts@4.3.0/contracts/utils/escrow/RefundEscrow.sol";
import "OpenZeppelin/openzeppelin-contracts@4.3.0/contracts/utils/math/SafeMath.sol";
contract RefundableCrowdSale is FinalizableCrowdSale{
using SafeMath for uint256;

constructor(uint256 _startTime, uint256 _endTime, uint256 _rate, address _wallet, address tokenAddress, uint256 _goal) 
    FinalizableCrowdSale(_startTime, _endTime, _rate, _wallet, tokenAddress) {
    require(_goal > 0);
    vault = new RefundEscrow(payable(_wallet));
    goal = _goal;
}
 using SafeMath for uint256;

  // minimum amount of funds to be raised in weis
  uint256 public goal;

  // refund vault used to hold funds while crowdsale is running
  RefundEscrow public vault;


  /**
   * @dev Investors can claim refunds here if crowdsale is unsuccessful
   */
  function claimRefund() public {
    require(isFinalized);
    require(!goalReached());

    vault.withdraw(payable(msg.sender));
  }

  /**
   * @dev Checks whether funding goal was reached.
   * @return Whether funding goal was reached
   */
  function goalReached() public view returns (bool) {
    return weiRaised >= goal;
  }

  /**
   * @dev vault finalization task, called when owner calls finalize()
   */
  function finalization() internal override {
    if (goalReached()) {
      vault.close();
    } else {
      vault.enableRefunds();
    }

    super.finalization();
  }

  /**
   * @dev Overrides Crowdsale fund forwarding, sending funds to vault.
   */
  function _forwardFunds() internal {
    vault.deposit(msg.sender);
  }

  function getTotal() external view returns (uint256) {
      return vault.depositsOf(msg.sender); 
  }
  
}
