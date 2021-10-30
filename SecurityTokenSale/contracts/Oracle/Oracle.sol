pragma solidity ^0.8.0;

import "OpenZeppelin/openzeppelin-contracts@4.3.0/contracts/access/Ownable.sol";
import "./CallerInterface.sol";

contract KYCOracle is Ownable {
    uint private randNonce = 0;
    uint private modulus = 1000;
    mapping(uint256=>bool) pendingRequests;
    
    event GetKYCEvent(address callerAddress, uint id, address customer);
    event SetKYCEvent(bool isKYC, address callerAddress, address customer, uint256 customerId);

    function getKYC(address _customer) public returns (uint256) {
        randNonce++;
        uint id = uint(keccak256(abi.encodePacked(block.timestamp ,msg.sender,randNonce))) % modulus; 
        pendingRequests[id] = true;
        emit GetKYCEvent(msg.sender, id, _customer);
        return id;
    }

    function setKYC(bool _isKYC, uint256 _customerId, address _callerAddress, uint256 _id, address _customer) public onlyOwner {
        require(pendingRequests[_id]);
        delete pendingRequests[_id];
        CallerInterface callerInstance;
        callerInstance = CallerInterface(_callerAddress);
        callerInstance.callback(_customerId, _isKYC, _customer,  _id);
        emit SetKYCEvent(_isKYC, _callerAddress, _customer, _customerId);
    }
}