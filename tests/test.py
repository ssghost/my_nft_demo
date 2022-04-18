from scripts.deploy import get_account, get_contract, deploy_and_create 
from brownie import network
import pytest

def test_deploy_and_create():
    if network.show_active() not in ["hardhat", "development", "ganache", "mainnet-fork"]:
        pytest.skip()
    smart_nft = deploy_and_create()
    assert smart_nft.ownerOf(0) == get_account()

def test_create_advanced():
    if network.show_active() not in ["hardhat", "development", "ganache", "mainnet-fork"]:
        pytest.skip("Only for local testing")
    advanced_collectible, creation_transaction = deploy_and_create()
    requestId = creation_transaction.events["requestedCollectible"]["requestId"]
    random_number = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, random_number, advanced_collectible.address, {"from": get_account()}
    )
    assert advanced_collectible.tokenCounter() == 1
    assert advanced_collectible.tokenIdToBreed(0) == random_number % 3

def main():
    test_deploy_and_create()
    test_create_advanced() 