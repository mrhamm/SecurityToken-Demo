pragma solidity ^0.8.0;

import "./CrowdSale.sol";
import "OpenZeppelin/openzeppelin-contracts@4.3.0/contracts/access/Ownable.sol";
import "./PauseInterface.sol";
contract FinalizableCrowdSale is CrowdSale, Ownable {
    IPausable pauser; 
    constructor(uint256 _startTime, uint256 _endTime, uint256 _rate, address _wallet, address tokenAddress) 
    CrowdSale(_startTime, _endTime, _rate, _wallet, tokenAddress) {
        pauser = IPausable(tokenAddress);
    }

    bool public isFinalized = false;

    event Finalized();

  /**
   * @dev Must be called after crowdsale ends, to do some extra finalization
   * work. Calls the contract's finalization function.
   */
    function finalize() onlyOwner public {
        require(!isFinalized);
        require(hasEnded());

        finalization();
        emit Finalized();

        isFinalized = true;
    }

  /**
   * @dev Can be overridden to add finalization logic. The overriding function
   * should call super.finalization() to ensure the chain of finalization is
   * executed entirely.
   */
  function finalization() internal virtual {
      pauser.unpause();
  }
}