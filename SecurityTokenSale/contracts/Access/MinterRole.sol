pragma solidity ^0.8.0;

import "./AccessControl.sol";

contract MinterRole is AccessControl {


    event MinterAdded(address indexed account);
    event MinterRemoved(address indexed account);
    bytes32 public constant MINTER_ROLE = keccak256('Minter'); 
    constructor () {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _addMinter(msg.sender);
        _setRoleAdmin(MINTER_ROLE, MINTER_ROLE);
    }

    modifier onlyMinter() {
        require(isMinter(msg.sender),'not minter');
        _;
    }

    function isMinter(address account) public view returns (bool) {
        return hasRole(MINTER_ROLE, account);
    }

    function addMinter(address account) public onlyMinter {
        _addMinter(account);
    }

    function removeMinter(address account) public onlyMinter {
        _removeMinter(account);
    }

    function renounceMinter() public {
        _removeMinter(msg.sender);
    }

    function _addMinter(address account) internal {
        _grantRole(MINTER_ROLE, account);
        emit MinterAdded(account);
    }

    function _removeMinter(address account) internal {
        revokeRole(MINTER_ROLE, account);
        emit MinterRemoved(account);
    }


}