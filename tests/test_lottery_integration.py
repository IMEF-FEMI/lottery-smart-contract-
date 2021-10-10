from web3 import Web3
from brownie import exceptions, network
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    fund_with_link,
    get_account,
    get_contract,
)
import pytest

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0



    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RND = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RND, lottery.address, {"from": account}
    )
    starting_balance_of_winner = account.balance()
    balance_of_lottery = lottery.balance()
    # 777 % 3 = 0
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_winner + balance_of_lottery