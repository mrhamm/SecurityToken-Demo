pragma solidity ^0.8.0;

import "./ERC1400.sol";
import "OpenZeppelin/openzeppelin-contracts@4.3.0/contracts/security/Pausable.sol";
import "./SellerRole.sol";

contract PausableERC1400 is ERC1400, Pausable, SellerRole {
    
    constructor(
    string memory name,
    string memory symbol,
    uint256 granularity,
    address[] memory controllers,
    bytes32[] memory defaultPartitions,
    address _whitelist
  ) ERC1400(name, symbol, granularity, controllers, defaultPartitions, _whitelist) {  
    _pause();
  }

    function _transferByPartition(
    bytes32 fromPartition,
    address operator,
    address from,
    address to,
    uint256 value,
    bytes memory data,
    bytes memory operatorData
  ) internal virtual override returns (bytes32) {
      super._transferByPartition(fromPartition,operator,from,to,value,data,operatorData);
    require(!paused(), "ERC1400Pausable: token transfer while paused");
  }

  function unpause() external onlySeller {
    _unpause();
  }
}