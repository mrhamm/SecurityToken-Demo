pragma solidity ^0.8.0;

interface CallerInterface { 
    function callback(uint256 customerId, bool isKYC, address customer, uint256 id) external; 
    function isAuthorized(address customer) external view returns (bool);
}