pragma solidity ^0.8.0;

import "OpenZeppelin/openzeppelin-contracts@4.3.0/contracts/access/Ownable.sol";
import "./OracleInterface.sol";

contract CallerContract is Ownable {

    bool private isKYC = false;
    OracleInterface private oracleInstance;
    address private oracleAddress;
    mapping(uint256=>bool) myRequests;

    struct customer {
        uint256 customerId;
        uint32 expireyDate;
        bool isAuthorized;
    }

    mapping (address => customer) customerRegistry;


    event newOracleAddressEvent(address oracleAddress);
    event ReceivedNewRequestIdEvent(uint256 id, address customer);
    event KYCUpdatedEvent(bool isKYC, uint256 id);

    function setOracleInstanceAddress(address _oracleInstanceAddress) public onlyOwner {
        oracleAddress = _oracleInstanceAddress;
        oracleInstance = OracleInterface(oracleAddress);
        emit newOracleAddressEvent(oracleAddress);
    }

    function updateKYC(address _customer) public {
        uint256 id = oracleInstance.getKYC(_customer);
        myRequests[id] = true; 
        emit ReceivedNewRequestIdEvent(id, _customer);
    }

    function callback(uint256 _customerId, bool _isKYC, address _customer, uint256 _id) public onlyOracle {
        require(myRequests[_id]);
        isKYC = _isKYC;
        customerRegistry[_customer].customerId= _customerId;
        customerRegistry[_customer].isAuthorized = _isKYC;
        customerRegistry[_customer].expireyDate = uint32(block.timestamp + 52 weeks);
        delete myRequests[_id];
        emit KYCUpdatedEvent(_isKYC, _id);
    }

    modifier onlyOracle() {
        require(msg.sender == oracleAddress);
        _;
    }
    function _isAuthorized(address _customer) internal view returns (bool) {
        return customerRegistry[_customer].isAuthorized;
    }

    function isAuthorized(address _customer) public view returns(bool) {
        return _isAuthorized(_customer);
    }

    function getOracleAddress() public view returns (address) {
        return oracleAddress;
    }

    function getCustomerId(address _customer) public view returns (uint256) {
        return customerRegistry[_customer].customerId;
    }
    function getCustomerDate(address _customer) public view returns (uint32) {
        return customerRegistry[_customer].expireyDate;
    }
    function getCustomerAuthorization(address _customer) public view returns (bool) {
        return customerRegistry[_customer].isAuthorized;
    }
}