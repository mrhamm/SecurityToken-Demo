/*
 * This code has not been reviewed.
 * Do not use or deploy this code before reviewing it personally first.
 */
pragma solidity ^0.8.0;

/**
 * @title IERC1400 security token standard
 * @dev See https://github.com/SecurityTokenStandard/EIP-Spec/blob/master/eip/eip-1400.md
 */
interface IPausable { // Interfaces can currently not inherit interfaces, but IERC1400 shall include IERC20
  function unpause() external;
  // ****************** Document Management *******************
}