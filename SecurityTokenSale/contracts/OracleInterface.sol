pragma solidity ^0.8.0;

interface OracleInterface { 
    function getKYC(address customer) external returns (uint256); 
}