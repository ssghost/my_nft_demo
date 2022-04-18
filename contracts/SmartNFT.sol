// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract SmartNFT is ERC721 {
    uint256 public tokenCounter;
    
    constructor () public ERC721 ("SmartNFT", "SNFT"){
        tokenCounter = 0;
    }

    function createCollectible(string memory tokenURI) public returns (uint256){
        uint256 newTokenId = tokenCounter;
        _safeMint(msg.sender, newTokenId);
        _setTokenURI(newTokenId, tokenURI);
        tokenCounter += 1;
        return newTokenId;
    }
}
