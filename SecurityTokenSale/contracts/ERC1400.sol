pragma solidity ^0.8.0;

import "OpenZeppelin/openzeppelin-contracts@4.3.0/contracts/token/ERC20/IERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@4.3.0/contracts/utils/math/SafeMath.sol";
import "OpenZeppelin/openzeppelin-contracts@4.3.0/contracts/access/Ownable.sol";
import "./MinterRole.sol";
import "./IERC1400.sol";
import "./CallerInterface.sol";

contract ERC1400 is IERC20, IERC1400, Ownable, MinterRole {
  using SafeMath for uint256;


  // Token
  string constant internal ERC1400_INTERFACE_NAME = "ERC1400Token";
  string constant internal ERC20_INTERFACE_NAME = "ERC20Token";



  /************************************* Token description ****************************************/
  string internal _name;
  string internal _symbol;
  uint256 internal _granularity;
  uint256 internal _totalSupply;
  bool internal _migrated;
  address internal whitelist;
  /************************************************************************************************/


  /**************************************** Token behaviours **************************************/
  // Indicate whether the token can still be controlled by operators or not anymore.
  bool internal _isControllable;

  // Indicate whether the token can still be issued by the issuer or not anymore.
  bool internal _isIssuable;
  /************************************************************************************************/


  /********************************** ERC20 Token mappings ****************************************/
  // Mapping from tokenHolder to balance.
  mapping(address => uint256) internal _balances;

  // Mapping from (tokenHolder, spender) to allowed value.
  mapping (address => mapping (address => uint256)) internal _allowed;
  /************************************************************************************************/


  /**************************************** Documents *********************************************/
  struct Doc {
    string docURI;
    bytes32 docHash;
  }
  // Mapping for token URIs.
  mapping(bytes32 => Doc) internal _documents;
  /************************************************************************************************/


  /*********************************** Partitions  mappings ***************************************/
  // List of partitions.
  bytes32[] internal _totalPartitions;

  // Mapping from partition to their index.
  mapping (bytes32 => uint256) internal _indexOfTotalPartitions;

  // Mapping from partition to global balance of corresponding partition.
  mapping (bytes32 => uint256) internal _totalSupplyByPartition;

  // Mapping from tokenHolder to their partitions.
  mapping (address => bytes32[]) internal _partitionsOf;

  // Mapping from (tokenHolder, partition) to their index.
  mapping (address => mapping (bytes32 => uint256)) internal _indexOfPartitionsOf;

  // Mapping from (tokenHolder, partition) to balance of corresponding partition.
  mapping (address => mapping (bytes32 => uint256)) internal _balanceOfByPartition;

  // List of token default partitions (for ERC20 compatibility).
  bytes32[] internal _defaultPartitions;
  /************************************************************************************************/


  /********************************* Global operators mappings ************************************/
  // Mapping from (operator, tokenHolder) to authorized status. [TOKEN-HOLDER-SPECIFIC]
  mapping(address => mapping(address => bool)) internal _authorizedOperator;

  // Array of controllers. [GLOBAL - NOT TOKEN-HOLDER-SPECIFIC]
  address[] internal _controllers;

  // Mapping from operator to controller status. [GLOBAL - NOT TOKEN-HOLDER-SPECIFIC]
  mapping(address => bool) internal _isController;
  /************************************************************************************************/


  /******************************** Partition operators mappings **********************************/
  // Mapping from (partition, tokenHolder, spender) to allowed value. [TOKEN-HOLDER-SPECIFIC]
  mapping(bytes32 => mapping (address => mapping (address => uint256))) internal _allowedByPartition;

  // Mapping from (tokenHolder, partition, operator) to 'approved for partition' status. [TOKEN-HOLDER-SPECIFIC]
  mapping (address => mapping (bytes32 => mapping (address => bool))) internal _authorizedOperatorByPartition;

  // Mapping from partition to controllers for the partition. [NOT TOKEN-HOLDER-SPECIFIC]
  mapping (bytes32 => address[]) internal _controllersByPartition;

  // Mapping from (partition, operator) to PartitionController status. [NOT TOKEN-HOLDER-SPECIFIC]
  mapping (bytes32 => mapping (address => bool)) internal _isControllerByPartition;
  /************************************************************************************************/

  

  /***************************************** Modifiers ********************************************/
  /**
   * @dev Modifier to verify if token is issuable.
   */
  modifier isIssuableToken() {
    require(_isIssuable, "55"); // 0x55	funds locked (lockup period)
    _;
  }
  /**
   * @dev Modifier to make a function callable only when the contract is not migrated.
   */
  modifier isNotMigratedToken() {
      require(!_migrated, "54"); // 0x54	transfers halted (contract paused)
      _;
  }
  
  function _isAuthorized(address _customer) internal view returns(bool) {
    CallerInterface callerInstance;
    callerInstance = CallerInterface(whitelist);
    return callerInstance.isAuthorized(_customer);
  }
  function changeWhitelist(address _whitelist) external onlyOwner {
      whitelist = _whitelist;
      emit WhitelistChanged(whitelist);
  }
  event WhitelistChanged(address _whitelist);
  /************************************************************************************************/


  /**************************** Events (additional - not mandatory) *******************************/
  event ApprovalByPartition(bytes32 indexed partition, address indexed owner, address indexed spender, uint256 value);
  /************************************************************************************************/


  /**
   * @dev Initialize ERC1400 + register the contract implementation in ERC1820Registry.
   * @param name_ Name of the token.
   * @param symbol_ Symbol of the token.
   * @param granularity Granularity of the token.
   * @param controllers Array of initial controllers.
   * @param defaultPartitions Partitions chosen by default, when partition is
   * not specified, like the case ERC20 tranfers.
   */
  constructor(
    string memory name_,
    string memory symbol_,
    uint256 granularity,
    address[] memory controllers,
    bytes32[] memory defaultPartitions,
    address _whitelist
  
  )
  {
    _name = name_;
    _symbol = symbol_;
    _totalSupply = 0;
    require(granularity >= 1); // Constructor Blocked - Token granularity can not be lower than 1
    _granularity = granularity;

    _setControllers(controllers);

    _defaultPartitions = defaultPartitions;

    _isControllable = true;
    _isIssuable = true;
    whitelist = _whitelist;
    emit WhitelistChanged(whitelist);
    // Register contract in ERC1820 registry


    // Indicate token verifies ERC1400 and ERC20 interfaces
   
  }

  
  /************************************************************************************************/
  /****************************** EXTERNAL FUNCTIONS (ERC20 INTERFACE) ****************************/
  /************************************************************************************************/


  /**
   * @dev Get the total number of issued tokens.
   * @return Total supply of tokens currently in circulation.
   */
  function totalSupply() external override view returns (uint256) {
    return _totalSupply;
  }
  /**
   * @dev Get the balance of the account with address 'tokenHolder'.
   * @param tokenHolder Address for which the balance is returned.
   * @return Amount of token held by 'tokenHolder' in the token contract.
   */
  function balanceOf(address tokenHolder) external override view returns (uint256) {
    return _balances[tokenHolder];
  }
  /**
   * @dev Transfer token for a specified address.
   * @param to The address to transfer to.
   * @param value The value to be transferred.
   * @return A boolean that indicates if the operation was successful.
   */
  function transfer(address to, uint256 value) external override returns (bool) {
    
    _transferByDefaultPartitions(msg.sender, msg.sender, to, value, "");
    return true;
  }
  /**
   * @dev Check the value of tokens that an owner allowed to a spender.
   * @param owner address The address which owns the funds.
   * @param spender address The address which will spend the funds.
   * @return A uint256 specifying the value of tokens still available for the spender.
   */
  function allowance(address owner, address spender) external override view returns (uint256) {
    return _allowed[owner][spender];
  }
  /**
   * @dev Approve the passed address to spend the specified amount of tokens on behalf of 'msg.sender'.
   * @param spender The address which will spend the funds.
   * @param value The amount of tokens to be spent.
   * @return A boolean that indicates if the operation was successful.
   */
  function approve(address spender, uint256 value) external override returns (bool) {
    require(spender != address(0), "56"); // 0x56	invalid sender
    _allowed[msg.sender][spender] = value;
    emit Approval(msg.sender, spender, value);
    return true;
  }
  /**
   * @dev Transfer tokens from one address to another.
   * @param from The address which you want to transfer tokens from.
   * @param to The address which you want to transfer to.
   * @param value The amount of tokens to be transferred.
   * @return A boolean that indicates if the operation was successful.
   */
  function transferFrom(address from, address to, uint256 value) external override returns (bool) {
    
    require( _isOperator(msg.sender, from)
      || (value <= _allowed[from][msg.sender]), "53"); // 0x53	insufficient allowance

    if(_allowed[from][msg.sender] >= value) {
      _allowed[from][msg.sender] = _allowed[from][msg.sender].sub(value);
    } else {
      _allowed[from][msg.sender] = 0;
    }

    _transferByDefaultPartitions(msg.sender, from, to, value, "");
    return true;
  }


  /************************************************************************************************/
  /****************************** EXTERNAL FUNCTIONS (ERC1400 INTERFACE) **************************/
  /************************************************************************************************/

  function name() external view returns (string memory) {
    return _name;
  }

  function symbol() external view returns (string memory) {
    return _symbol;
  }

  /************************************* Document Management **************************************/
  /**
   * @dev Access a document associated with the token.
   * @param name Short name (represented as a bytes32) associated to the document.
   * @return Requested document + document hash.
   */
  function getDocument(bytes32 name) external override view returns (string memory, bytes32) {
    require(bytes(_documents[name].docURI).length != 0); // Action Blocked - Empty document
    return (
      _documents[name].docURI,
      _documents[name].docHash
    );
  }
  /**
   * @dev Associate a document with the token.
   * @param name Short name (represented as a bytes32) associated to the document.
   * @param uri Document content.
   * @param documentHash Hash of the document [optional parameter].
   */
  function setDocument(bytes32 name, string calldata uri, bytes32 documentHash) external override {
    require(_isController[msg.sender]);
    _documents[name] = Doc({
      docURI: uri,
      docHash: documentHash
    });
    emit Document(name, uri, documentHash);
  }
  /************************************************************************************************/


  /************************************** Token Information ***************************************/
  /**
   * @dev Get balance of a tokenholder for a specific partition.
   * @param partition Name of the partition.
   * @param tokenHolder Address for which the balance is returned.
   * @return Amount of token of partition 'partition' held by 'tokenHolder' in the token contract.
   */
  function balanceOfByPartition(bytes32 partition, address tokenHolder) external override view returns (uint256) {
    return _balanceOfByPartition[tokenHolder][partition];
  }
  /**
   * @dev Get partitions index of a tokenholder.
   * @param tokenHolder Address for which the partitions index are returned.
   * @return Array of partitions index of 'tokenHolder'.
   */
  function partitionsOf(address tokenHolder) external override view returns (bytes32[] memory) {
    return _partitionsOf[tokenHolder];
  }
  /************************************************************************************************/
/****************************************** Transfers *******************************************/
  /**
   * @dev Transfer the amount of tokens from the address 'msg.sender' to the address 'to'.
   * @param to Token recipient.
   * @param value Number of tokens to transfer.
   * @param data Information attached to the transfer, by the token holder.
   */
  function transferWithData(address to, uint256 value, bytes calldata data) external override {
    
    _transferByDefaultPartitions(msg.sender, msg.sender, to, value, data);
  }
  /**
   * @dev Transfer the amount of tokens on behalf of the address 'from' to the address 'to'.
   * @param from Token holder (or 'address(0)' to set from to 'msg.sender').
   * @param to Token recipient.
   * @param value Number of tokens to transfer.
   * @param data Information attached to the transfer, and intended for the token holder ('from').
   */
  function transferFromWithData(address from, address to, uint256 value, bytes calldata data) external override {
    
    require( _isOperator(msg.sender, from)
      || (value <= _allowed[from][msg.sender]), "53");// 0x58	invalid operator (transfer agent)

    if(_allowed[from][msg.sender] >= value) {
      _allowed[from][msg.sender] = _allowed[from][msg.sender].sub(value);
    } else {
      _allowed[from][msg.sender] = 0;
    }

    _transferByDefaultPartitions(msg.sender, from, to, value, data);
  }
  /************************************************************************************************/


  /********************************** Partition Token Transfers ***********************************/
  /**
   * @dev Transfer tokens from a specific partition.
   * @param partition Name of the partition.
   * @param to Token recipient.
   * @param value Number of tokens to transfer.
   * @param data Information attached to the transfer, by the token holder.
   * @return Destination partition.
   */
  function transferByPartition(
    bytes32 partition,
    address to,
    uint256 value,
    bytes calldata data
  )
    external override
    returns (bytes32)
  {
  
    return _transferByPartition(partition, msg.sender, msg.sender, to, value, data, "");
  }
  /**
   * @dev Transfer tokens from a specific partition through an operator.
   * @param partition Name of the partition.
   * @param from Token holder.
   * @param to Token recipient.
   * @param value Number of tokens to transfer.
   * @param data Information attached to the transfer. [CAN CONTAIN THE DESTINATION PARTITION]
   * @param operatorData Information attached to the transfer, by the operator.
   * @return Destination partition.
   */
  function operatorTransferByPartition(
    bytes32 partition,
    address from,
    address to,
    uint256 value,
    bytes calldata data,
    bytes calldata operatorData
  )
    external override
    returns (bytes32)
  {
    
    require(_isOperatorForPartition(partition, msg.sender, from)
      || (value <= _allowedByPartition[partition][from][msg.sender]), "53"); // 0x53	insufficient allowance

    if(_allowedByPartition[partition][from][msg.sender] >= value) {
      _allowedByPartition[partition][from][msg.sender] = _allowedByPartition[partition][from][msg.sender].sub(value);
    } else {
      _allowedByPartition[partition][from][msg.sender] = 0;
    }

    return _transferByPartition(partition, msg.sender, from, to, value, data, operatorData);
  }
  /************************************************************************************************/
   /******************************** Partition Token Allowances ************************************/
  /**
   * @dev Check the value of tokens that an owner allowed to a spender.
   * @param partition Name of the partition.
   * @param owner address The address which owns the funds.
   * @param spender address The address which will spend the funds.
   * @return A uint256 specifying the value of tokens still available for the spender.
   */
  function allowanceByPartition(bytes32 partition, address owner, address spender) external view returns (uint256) {
    return _allowedByPartition[partition][owner][spender];
  }
  /**
   * @dev Approve the passed address to spend the specified amount of tokens on behalf of 'msg.sender'.
   * @param partition Name of the partition.
   * @param spender The address which will spend the funds.
   * @param value The amount of tokens to be spent.
   * @return A boolean that indicates if the operation was successful.
   */
  function approveByPartition(bytes32 partition, address spender, uint256 value) external returns (bool) {
    require(spender != address(0), "56"); // 0x56	invalid sender
    _allowedByPartition[partition][msg.sender][spender] = value;
    emit ApprovalByPartition(partition, msg.sender, spender, value);
    return true;
  }
/**************************************** Token Issuance ****************************************/
  /**
   * @dev Know if new tokens can be issued in the future.
   * @return bool 'true' if tokens can still be issued by the issuer, 'false' if they can't anymore.
   */
  function isIssuable() external override view returns (bool) {
    return _isIssuable;
  }
  /**
   * @dev Issue tokens from default partition.
   * @param tokenHolder Address for which we want to issue tokens.
   * @param value Number of tokens issued.
   * @param data Information attached to the issuance, by the issuer.
   */
  function issue(address tokenHolder, uint256 value, bytes calldata data)
    external override
    onlyMinter
    isIssuableToken
  {
    
    require(_defaultPartitions.length != 0, "55"); // 0x55	funds locked (lockup period)
    require(_isAuthorized(tokenHolder),"Unauthorized Party.");
    _issueByPartition(_defaultPartitions[0], msg.sender, tokenHolder, value, data);
  }
  /**
   * @dev Issue tokens from a specific partition.
   * @param partition Name of the partition.
   * @param tokenHolder Address for which we want to issue tokens.
   * @param value Number of tokens issued.
   * @param data Information attached to the issuance, by the issuer.
   */
  function issueByPartition(bytes32 partition, address tokenHolder, uint256 value, bytes calldata data)
    external override
    onlyMinter
    isIssuableToken
  {
    
    _issueByPartition(partition, msg.sender, tokenHolder, value, data);
  }
  /************************************************************************************************/
  

  /*************************************** Token Redemption ***************************************/
  /**
   * @dev Redeem the amount of tokens from the address 'msg.sender'.
   * @param value Number of tokens to redeem.
   * @param data Information attached to the redemption, by the token holder.
   */
  function redeem(uint256 value, bytes calldata data)
    external override
  {
   
    _redeemByDefaultPartitions(msg.sender, msg.sender, value, data);
  }
  /**
   * @dev Redeem the amount of tokens on behalf of the address from.
   * @param from Token holder whose tokens will be redeemed (or address(0) to set from to msg.sender).
   * @param value Number of tokens to redeem.
   * @param data Information attached to the redemption.
   */
  function redeemFrom(address from, uint256 value, bytes calldata data)
    external override
  {
    
    require(_isOperator(msg.sender, from), "58"); // 0x58	invalid operator (transfer agent)

    _redeemByDefaultPartitions(msg.sender, from, value, data);
  }
  /**
   * @dev Redeem tokens of a specific partition.
   * @param partition Name of the partition.
   * @param value Number of tokens redeemed.
   * @param data Information attached to the redemption, by the redeemer.
   */
  function redeemByPartition(bytes32 partition, uint256 value, bytes calldata data)
    external override
  {
   
    _redeemByPartition(partition, msg.sender, msg.sender, value, data, "");
  }
  /**
   * @dev Redeem tokens of a specific partition.
   * @param partition Name of the partition.
   * @param tokenHolder Address for which we want to redeem tokens.
   * @param value Number of tokens redeemed
   * @param operatorData Information attached to the redemption, by the operator.
   */
  function operatorRedeemByPartition(bytes32 partition, address tokenHolder, uint256 value, bytes calldata operatorData)
    external override
  {
    
    require(_isOperatorForPartition(partition, msg.sender, tokenHolder), "58"); // 0x58	invalid operator (transfer agent)

    _redeemByPartition(partition, msg.sender, tokenHolder, value, "", operatorData);
  }
  /************************************************************************************************/


 /**************************************** Token Transfers ***************************************/
  /**
   * @dev Perform the transfer of tokens.
   * @param from Token holder.
   * @param to Token recipient.
   * @param value Number of tokens to transfer.
   */
  function _transferWithData(
    address from,
    address to,
    uint256 value
  )
    internal
    isNotMigratedToken
  {
    
    require(_isMultiple(value), "50"); // 0x50	transfer failure
    require(to != address(0), "57"); // 0x57	invalid receiver
    require(_balances[from] >= value, "52"); // 0x52	insufficient balance

    _balances[from] = _balances[from].sub(value);
    _balances[to] = _balances[to].add(value);

    emit Transfer(from, to, value); // ERC20 retrocompatibility 
  }
  /**
   * @dev Transfer tokens from a specific partition.
   * @param fromPartition Partition of the tokens to transfer.
   * @param operator The address performing the transfer.
   * @param from Token holder.
   * @param to Token recipient.
   * @param value Number of tokens to transfer.
   * @param data Information attached to the transfer. [CAN CONTAIN THE DESTINATION PARTITION]
   * @param operatorData Information attached to the transfer, by the operator (if any).
   * @return Destination partition.
   */
  function _transferByPartition(
    bytes32 fromPartition,
    address operator,
    address from,
    address to,
    uint256 value,
    bytes memory data,
    bytes memory operatorData
  )
    internal virtual
    returns (bytes32)
  {
   
    require(_balanceOfByPartition[from][fromPartition] >= value, "52"); // 0x52	insufficient balance
    require(_isAuthorized(operator) && _isAuthorized(from) && _isAuthorized(to),"Unauthorized Party.");
    bytes32 toPartition = fromPartition;

    if(operatorData.length != 0 && data.length >= 64) {
      toPartition = _getDestinationPartition(fromPartition, data);
    }

    //_callSenderExtension(fromPartition, operator, from, to, value, data, operatorData);
    //_callTokenExtension(fromPartition, operator, from, to, value, data, operatorData);

    _removeTokenFromPartition(from, fromPartition, value);
    _transferWithData(from, to, value);
    _addTokenToPartition(to, toPartition, value);

    //_callRecipientExtension(toPartition, operator, from, to, value, data, operatorData);

    emit TransferByPartition(fromPartition, operator, from, to, value, data, operatorData);

    if(toPartition != fromPartition) {
      emit ChangedPartition(fromPartition, toPartition, value);
    }

    return toPartition;
  }
  /**
   * @dev Transfer tokens from default partitions.
   * Function used for ERC20 retrocompatibility.
   * @param operator The address performing the transfer.
   * @param from Token holder.
   * @param to Token recipient.
   * @param value Number of tokens to transfer.
   * @param data Information attached to the transfer, and intended for the token holder ('from') [CAN CONTAIN THE DESTINATION PARTITION].
   */
  function _transferByDefaultPartitions(
    address operator,
    address from,
    address to,
    uint256 value,
    bytes memory data
  )
    internal
  {
    
    require(_defaultPartitions.length != 0, "55"); // // 0x55	funds locked (lockup period)
    uint256 _remainingValue = value;
    uint256 _localBalance;

    for (uint i = 0; i < _defaultPartitions.length; i++) {
      _localBalance = _balanceOfByPartition[from][_defaultPartitions[i]];
      if(_remainingValue <= _localBalance) {
        _transferByPartition(_defaultPartitions[i], operator, from, to, _remainingValue, data, "");
        _remainingValue = 0;
        break;
      } else if (_localBalance != 0) {
        _transferByPartition(_defaultPartitions[i], operator, from, to, _localBalance, data, "");
        _remainingValue = _remainingValue - _localBalance;
      }
    }

    require(_remainingValue == 0, "52"); // 0x52	insufficient balance
  }
  /**
   * @dev Retrieve the destination partition from the 'data' field.
   * By convention, a partition change is requested ONLY when 'data' starts
   * with the flag: 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
   * When the flag is detected, the destination tranche is extracted from the
   * 32 bytes following the flag.
   * @param fromPartition Partition of the tokens to transfer.
   * @param data Information attached to the transfer. [CAN CONTAIN THE DESTINATION PARTITION]
   * @return toPartition  Destination partition.
   */
  function _getDestinationPartition(bytes32 fromPartition, bytes memory data) internal pure returns(bytes32 toPartition) {
    bytes32 changePartitionFlag = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff;
    bytes32 flag;
    assembly {
      flag := mload(add(data, 32))
    }
    if(flag == changePartitionFlag) {
      assembly {
        toPartition := mload(add(data, 64))
      }
    } else {
      toPartition = fromPartition;
    }
  }
  /**
   * @dev Remove a token from a specific partition.
   * @param from Token holder.
   * @param partition Name of the partition.
   * @param value Number of tokens to transfer.
   */
  function _removeTokenFromPartition(address from, bytes32 partition, uint256 value) internal {
    _balanceOfByPartition[from][partition] = _balanceOfByPartition[from][partition].sub(value);
    _totalSupplyByPartition[partition] = _totalSupplyByPartition[partition].sub(value);

    // If the total supply is zero, finds and deletes the partition.
    if(_totalSupplyByPartition[partition] == 0) {
      uint256 index1 = _indexOfTotalPartitions[partition];
      require(index1 > 0, "50"); // 0x50	transfer failure

      // move the last item into the index being vacated
      bytes32 lastValue = _totalPartitions[_totalPartitions.length - 1];
      _totalPartitions[index1 - 1] = lastValue; // adjust for 1-based indexing
      delete _totalPartitions[_totalPartitions.length -1];
      _indexOfTotalPartitions[lastValue] = index1;

      //_totalPartitions.length -= 1;
      _indexOfTotalPartitions[partition] = 0;
    }

    // If the balance of the TokenHolder's partition is zero, finds and deletes the partition.
    if(_balanceOfByPartition[from][partition] == 0) {
      uint256 index2 = _indexOfPartitionsOf[from][partition];
      require(index2 > 0, "50"); // 0x50	transfer failure

      // move the last item into the index being vacated
      bytes32 lastValue = _partitionsOf[from][_partitionsOf[from].length - 1];
      _partitionsOf[from][index2 - 1] = lastValue;  // adjust for 1-based indexing
      delete _partitionsOf[from][_partitionsOf[from].length -1];
      _indexOfPartitionsOf[from][lastValue] = index2;

      //_partitionsOf[from].length -= 1;
      _indexOfPartitionsOf[from][partition] = 0;
    }
  }
  /**
   * @dev Add a token to a specific partition.
   * @param to Token recipient.
   * @param partition Name of the partition.
   * @param value Number of tokens to transfer.
   */
  function _addTokenToPartition(address to, bytes32 partition, uint256 value) internal {
    if(value != 0) {
      if (_indexOfPartitionsOf[to][partition] == 0) {
        _partitionsOf[to].push(partition);
        _indexOfPartitionsOf[to][partition] = _partitionsOf[to].length;
      }
      _balanceOfByPartition[to][partition] = _balanceOfByPartition[to][partition].add(value);

      if (_indexOfTotalPartitions[partition] == 0) {
        _totalPartitions.push(partition);
        _indexOfTotalPartitions[partition] = _totalPartitions.length;
      }
      _totalSupplyByPartition[partition] = _totalSupplyByPartition[partition].add(value);
    }
  }
  /**
   * @dev Check if 'value' is multiple of the granularity.
   * @param value The quantity that want's to be checked.
   * @return 'true' if 'value' is a multiple of the granularity.
   */
  function _isMultiple(uint256 value) internal view returns(bool) {
    return(value.div(_granularity).mul(_granularity) == value);
  }


/************************************ Token controllers *****************************************/
  /**
   * @dev Get the list of controllers as defined by the token contract.
   * @return List of addresses of all the controllers.
   */
  function controllers() external view returns (address[] memory) {
    return _controllers;
  }
  /**
   * @dev Get controllers for a given partition.
   * @param partition Name of the partition.
   * @return Array of controllers for partition.
   */
  function controllersByPartition(bytes32 partition) external view returns (address[] memory) {
    return _controllersByPartition[partition];
  }
  /**
   * @dev Set list of token controllers.
   * @param operators Controller addresses.
   */
  function setControllers(address[] calldata operators) external onlyOwner {
    _setControllers(operators);
  }
  /**
   * @dev Set list of token partition controllers.
   * @param partition Name of the partition.
   * @param operators Controller addresses.
   */
   function setPartitionControllers(bytes32 partition, address[] calldata operators) external onlyOwner {
     _setPartitionControllers(partition, operators);
   }
  /************************************ Token controllers *****************************************/
  /**
   * @dev Set list of token controllers.
   * @param operators Controller addresses.
   */
  function _setControllers(address[] memory operators) internal {
    for (uint i = 0; i<_controllers.length; i++){
      _isController[_controllers[i]] = false;
    }
    for (uint j = 0; j<operators.length; j++){
      _isController[operators[j]] = true;
    }
    _controllers = operators;
  }
  /**
   * @dev Set list of token partition controllers.
   * @param partition Name of the partition.
   * @param operators Controller addresses.
   */
   function _setPartitionControllers(bytes32 partition, address[] memory operators) internal {
     for (uint i = 0; i<_controllersByPartition[partition].length; i++){
       _isControllerByPartition[partition][_controllersByPartition[partition][i]] = false;
     }
     for (uint j = 0; j<operators.length; j++){
       _isControllerByPartition[partition][operators[j]] = true;
     }
     _controllersByPartition[partition] = operators;
   }
  /************************************************************************************************/


  /**************************************** Token behaviours **************************************/
  /**
   * @dev Definitely renounce the possibility to control tokens on behalf of tokenHolders.
   * Once set to false, '_isControllable' can never be set to 'true' again.
   */
  function renounceControl() external onlyOwner {
    _isControllable = false;
  }
  /**
   * @dev Definitely renounce the possibility to issue new tokens.
   * Once set to false, '_isIssuable' can never be set to 'true' again.
   */
  function renounceIssuance() external onlyOwner {
    _isIssuable = false;
  }
  /************************************* Operator Information *************************************/
  /**
   * @dev Indicate whether the operator address is an operator of the tokenHolder address.
   * @param operator Address which may be an operator of 'tokenHolder'.
   * @param tokenHolder Address of a token holder which may have the 'operator' address as an operator.
   * @return 'true' if 'operator' is an operator of 'tokenHolder' and 'false' otherwise.
   */
  function _isOperator(address operator, address tokenHolder) internal view returns (bool) {
    return (operator == tokenHolder
      || _authorizedOperator[operator][tokenHolder]
      || (_isControllable && _isController[operator])
    );
  }
  /**
   * @dev Indicate whether the operator address is an operator of the tokenHolder
   * address for the given partition.
   * @param partition Name of the partition.
   * @param operator Address which may be an operator of tokenHolder for the given partition.
   * @param tokenHolder Address of a token holder which may have the operator address as an operator for the given partition.
   * @return 'true' if 'operator' is an operator of 'tokenHolder' for partition 'partition' and 'false' otherwise.
   */
   function _isOperatorForPartition(bytes32 partition, address operator, address tokenHolder) internal view returns (bool) {
     return (_isOperator(operator, tokenHolder)
       || _authorizedOperatorByPartition[tokenHolder][partition][operator]
       || (_isControllable && _isControllerByPartition[partition][operator])
     );
   }


  /************************************* Controller Operation *************************************/
  /**
   * @dev Know if the token can be controlled by operators.
   * If a token returns 'false' for 'isControllable()'' then it MUST always return 'false' in the future.
   * @return bool 'true' if the token can still be controlled by operators, 'false' if it can't anymore.
   */
  function isControllable() external override view returns (bool) {
    return _isControllable;
  }
  /************************************************************************************************/


  /************************************* Operator Management **************************************/
  /**
   * @dev Set a third party operator address as an operator of 'msg.sender' to transfer
   * and redeem tokens on its behalf.
   * @param operator Address to set as an operator for 'msg.sender'.
   */
  function authorizeOperator(address operator) external override {
    require(operator != msg.sender);
    _authorizedOperator[operator][msg.sender] = true;
    emit AuthorizedOperator(operator, msg.sender);
  }
  /**
   * @dev Remove the right of the operator address to be an operator for 'msg.sender'
   * and to transfer and redeem tokens on its behalf.
   * @param operator Address to rescind as an operator for 'msg.sender'.
   */
  function revokeOperator(address operator) external override {
    require(operator != msg.sender);
    _authorizedOperator[operator][msg.sender] = false;
    emit RevokedOperator(operator, msg.sender);
  }
  /**
   * @dev Set 'operator' as an operator for 'msg.sender' for a given partition.
   * @param partition Name of the partition.
   * @param operator Address to set as an operator for 'msg.sender'.
   */
  function authorizeOperatorByPartition(bytes32 partition, address operator) external override {
    _authorizedOperatorByPartition[msg.sender][partition][operator] = true;
    emit AuthorizedOperatorByPartition(partition, operator, msg.sender);
  }
  /**
   * @dev Remove the right of the operator address to be an operator on a given
   * partition for 'msg.sender' and to transfer and redeem tokens on its behalf.
   * @param partition Name of the partition.
   * @param operator Address to rescind as an operator on given partition for 'msg.sender'.
   */
  function revokeOperatorByPartition(bytes32 partition, address operator) external override {
    _authorizedOperatorByPartition[msg.sender][partition][operator] = false;
    emit RevokedOperatorByPartition(partition, operator, msg.sender);
  }
  /************************************************************************************************/


  /************************************* Operator Information *************************************/
  /**
   * @dev Indicate whether the operator address is an operator of the tokenHolder address.
   * @param operator Address which may be an operator of tokenHolder.
   * @param tokenHolder Address of a token holder which may have the operator address as an operator.
   * @return 'true' if operator is an operator of 'tokenHolder' and 'false' otherwise.
   */
  function isOperator(address operator, address tokenHolder) external override view returns (bool) {
    return _isOperator(operator, tokenHolder);
  }
  /**
   * @dev Indicate whether the operator address is an operator of the tokenHolder
   * address for the given partition.
   * @param partition Name of the partition.
   * @param operator Address which may be an operator of tokenHolder for the given partition.
   * @param tokenHolder Address of a token holder which may have the operator address as an operator for the given partition.
   * @return 'true' if 'operator' is an operator of 'tokenHolder' for partition 'partition' and 'false' otherwise.
   */
  function isOperatorForPartition(bytes32 partition, address operator, address tokenHolder) external override view returns (bool) {
    return _isOperatorForPartition(partition, operator, tokenHolder);
  }
  /************************************************************************************************/


  

     /**************************************** Token Issuance ****************************************/
  /**
   * @dev Perform the issuance of tokens.
   * @param operator Address which triggered the issuance.
   * @param to Token recipient.
   * @param value Number of tokens issued.
   * @param data Information attached to the issuance, and intended for the recipient (to).
   */
  function _issue(address operator, address to, uint256 value, bytes memory data)
    internal
    isNotMigratedToken  
  {
    require(_isAuthorized(operator) && _isAuthorized(to),"Unauthorized Party.");
    require(_isMultiple(value), "50"); // 0x50	transfer failure
    require(to != address(0), "57"); // 0x57	invalid receiver

    _totalSupply = _totalSupply.add(value);
    _balances[to] = _balances[to].add(value);

    emit Issued(operator, to, value, data);
    emit Transfer(address(0), to, value); // ERC20 retrocompatibility
  }
  /**
   * @dev Issue tokens from a specific partition.
   * @param toPartition Name of the partition.
   * @param operator The address performing the issuance.
   * @param to Token recipient.
   * @param value Number of tokens to issue.
   * @param data Information attached to the issuance.
   */
  function _issueByPartition(
    bytes32 toPartition,
    address operator,
    address to,
    uint256 value,
    bytes memory data
  )
    internal
  {
    require(_isAuthorized(operator) && _isAuthorized(to),"Unauthorized Party.");
    //_callTokenExtension(toPartition, operator, address(0), to, value, data, "");

    _issue(operator, to, value, data);
    _addTokenToPartition(to, toPartition, value);

    //_callRecipientExtension(toPartition, operator, address(0), to, value, data, "");

    emit IssuedByPartition(toPartition, operator, to, value, data, "");
  }
  /************************************************************************************************/


  /*************************************** Token Redemption ***************************************/
  /**
   * @dev Perform the token redemption.
   * @param operator The address performing the redemption.
   * @param from Token holder whose tokens will be redeemed.
   * @param value Number of tokens to redeem.
   * @param data Information attached to the redemption.
   */
  function _redeem(address operator, address from, uint256 value, bytes memory data)
    internal
    isNotMigratedToken
  {
    require(_isAuthorized(operator) && _isAuthorized(from),"Unauthorized Party.");
    require(_isMultiple(value), "50"); // 0x50	transfer failure
    require(from != address(0), "56"); // 0x56	invalid sender
    require(_balances[from] >= value, "52"); // 0x52	insufficient balance

    _balances[from] = _balances[from].sub(value);
    _totalSupply = _totalSupply.sub(value);

    emit Redeemed(operator, from, value, data);
    emit Transfer(from, address(0), value);  // ERC20 retrocompatibility
  }
  /**
   * @dev Redeem tokens of a specific partition.
   * @param fromPartition Name of the partition.
   * @param operator The address performing the redemption.
   * @param from Token holder whose tokens will be redeemed.
   * @param value Number of tokens to redeem.
   * @param data Information attached to the redemption.
   * @param operatorData Information attached to the redemption, by the operator (if any).
   */
  function _redeemByPartition(
    bytes32 fromPartition,
    address operator,
    address from,
    uint256 value,
    bytes memory data,
    bytes memory operatorData
  )
    internal
  {
    require(_isAuthorized(operator) && _isAuthorized(from),"Unauthorized Party.");
    require(_balanceOfByPartition[from][fromPartition] >= value, "52"); // 0x52	insufficient balance

    //_callSenderExtension(fromPartition, operator, from, address(0), value, data, operatorData);
    //_callTokenExtension(fromPartition, operator, from, address(0), value, data, operatorData);

    _removeTokenFromPartition(from, fromPartition, value);
    _redeem(operator, from, value, data);

    emit RedeemedByPartition(fromPartition, operator, from, value, operatorData);
  }
  /**
   * @dev Redeem tokens from a default partitions.
   * @param operator The address performing the redeem.
   * @param from Token holder.
   * @param value Number of tokens to redeem.
   * @param data Information attached to the redemption.
   */
  function _redeemByDefaultPartitions(
    address operator,
    address from,
    uint256 value,
    bytes memory data
  )
    internal
  {
    require(_isAuthorized(operator) && _isAuthorized(from),"Unauthorized Party.");
    require(_defaultPartitions.length != 0, "55"); // 0x55	funds locked (lockup period)

    uint256 _remainingValue = value;
    uint256 _localBalance;

    for (uint i = 0; i < _defaultPartitions.length; i++) {
      _localBalance = _balanceOfByPartition[from][_defaultPartitions[i]];
      if(_remainingValue <= _localBalance) {
        _redeemByPartition(_defaultPartitions[i], operator, from, _remainingValue, data, "");
        _remainingValue = 0;
        break;
      } else {
        _redeemByPartition(_defaultPartitions[i], operator, from, _localBalance, data, "");
        _remainingValue = _remainingValue - _localBalance;
      }
    }

    require(_remainingValue == 0, "52"); // 0x52	insufficient balance
  }
  /************************************************************************************************/

      /********************************* Token default partitions *************************************/
  /**
   * @dev Get default partitions to transfer from.
   * Function used for ERC20 retrocompatibility.
   * For example, a security token may return the bytes32("unrestricted").
   * @return Array of default partitions.
   */
  function getDefaultPartitions() external view returns (bytes32[] memory) {
    return _defaultPartitions;
  }
  /**
   * @dev Set default partitions to transfer from.
   * Function used for ERC20 retrocompatibility.
   * @param partitions partitions to use by default when not specified.
   */
  function setDefaultPartitions(bytes32[] calldata partitions) external onlyOwner {
    _defaultPartitions = partitions;
  }

}
