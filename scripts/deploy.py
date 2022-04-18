from brownie import accounts, network, config, SmartNFT, AdvancedCollectible, LinkToken, VRFCoordinatorMock, Contract
from web3 import Web3
from metadata.metadata_template import metadata_template
from pathlib import Path

sample_token_uri = "https://ipfs.io/ipfs/XXXX.json"
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"


def deploy_snft():
    account = get_account()
    smart_nft = SmartNFT.deploy({"from": account})
    tx = smart_nft.createCollectible(sample_token_uri, {"from": account})
    tx.wait(1)
    print(
        f"Awesome, you can view your NFT at {OPENSEA_URL.format(smart_nft.address, smart_nft.tokenCounter() - 1)}"
    )
    print("Please wait up to 20 minutes, and hit the refresh metadata button. ")
    return smart_nft

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in ["hardhat", "development", "ganache", "mainnet-fork"]:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])

def get_contract(contract_name):
    contract_to_mock = {"link_token": LinkToken, "vrf_coordinator": VRFCoordinatorMock}
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in ["hardhat", "development", "ganache", "mainnet-fork"]:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract

def deploy_mocks():
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    account = get_account()
    print("Deploying Mock LinkToken...")
    link_token = LinkToken.deploy({"from": account})
    print(f"Link Token deployed to {link_token.address}")
    print("Deploying Mock VRF Coordinator...")
    vrf_coordinator = VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print(f"VRFCoordinator deployed to {vrf_coordinator.address}")
    
def create_metadata():    
    advanced_collectible = AdvancedCollectible[-1]
    number_of_advanced_collectibles = advanced_collectible.tokenCounter()
    print(f"You have created {number_of_advanced_collectibles} collectibles!")
    BREED_MAPPING = {0: "SNFT_00", 1: "SNFT_01", 2: "SNFT_02"}
    for token_id in range(number_of_advanced_collectibles):
        breed = BREED_MAPPING[advanced_collectible.tokenIdToBreed(token_id)]
        metadata_file_name = (
            f"./metadata/{network.show_active()}/{token_id}-{breed}.json"
        )
        collectible_metadata = metadata_template
        if Path(metadata_file_name).exists():
            print(f"{metadata_file_name} already exists! Delete it to overwrite")
        else:
            print(f"Creating Metadata file: {metadata_file_name}")
            collectible_metadata["name"] = breed
            collectible_metadata["description"] = f"An adorable {breed} pup!"
            image_path = "./img/" + breed.lower().replace("_", "-") + ".png"
            return image_path


def deploy_and_create():
    account = get_account()
    advanced_collectible = AdvancedCollectible.deploy(
        get_contract("vrf_coordinator"),
        get_contract("link_token"),
        config["networks"][network.show_active()]["keyhash"],
        config["networks"][network.show_active()]["fee"],
        {"from": account},
    )
    link_payment(advanced_collectible.address)
    cre_tx = advanced_collectible.createCollectible({"from": account})
    cre_tx.wait(1)
    print("New token has been created!")
    return advanced_collectible, cre_tx

def link_payment(
    contract_address, account=None, link_token=None, amount=Web3.toWei(0.3, "ether")
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    pay_tx = link_token.transfer(contract_address, amount, {"from": account})
    pay_tx.wait(1)
    print(f"Funded {contract_address}")
    return pay_tx

def main():
    deploy_snft()
    deploy_and_create()

