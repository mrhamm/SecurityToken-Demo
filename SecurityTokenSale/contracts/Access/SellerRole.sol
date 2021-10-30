pragma solidity ^0.8.0;

import "./AccessControl.sol";

contract SellerRole is AccessControl {


    event SellerAdded(address indexed account);
    event SellerRemoved(address indexed account);
    bytes32 public constant SELLER_ROLE = keccak256('Seller'); 
    constructor () {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _addSeller(msg.sender);
        _setRoleAdmin(SELLER_ROLE, SELLER_ROLE);
    }

    modifier onlySeller() {
        require(isSeller(msg.sender),'not seller');
        _;
    }

    function isSeller(address account) public view returns (bool) {
        return hasRole(SELLER_ROLE, account);
    }

    function addSeller(address account) public onlySeller {
        _addSeller(account);
    }

    function removeSeller(address account) public onlySeller {
        _removeSeller(account);
    }

    function renounceSeller() public {
        _removeSeller(msg.sender);
    }

    function _addSeller(address account) internal {
        _grantRole(SELLER_ROLE, account);
        emit SellerAdded(account);
    }

    function _removeSeller(address account) internal {
        revokeRole(SELLER_ROLE, account);
        emit SellerRemoved(account);
    }


}