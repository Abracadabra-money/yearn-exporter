from random import randint
from brownie import chain
import pytest
from yearn.utils import contract_creation_block
from yearn.v2.registry import Registry
from yearn.v2.vaults import Vault

registry = Registry(watch_events_forever=False)
start_block = start_block = min(contract_creation_block(vault.vault.address)for vault in registry.vaults)
blocks = [randint(start_block,chain.height) for i in range(50)]


@pytest.mark.parametrize('block',blocks)
def test_describe_v2(block):
    assert registry.describe(block=block)


@pytest.mark.parametrize('vault',registry.vaults)
def test_describe_vault_v2(vault: Vault):
    blocks = [randint(contract_creation_block(vault.vault.address), chain.height) for i in range(25)]
    for block in blocks:
        description = vault.describe(block=block) 
        assert description["address"] == vault.vault.address, f'Incorrect address returned for {vault.name}.'
        assert description["version"] == "v2", f'Incorrect version returned for {vault.name}.'

        assert vault._views, f"Unable to fetch views for {vault.name}."
        for param in vault._views + ["experimental", "strategies"]:
            assert param in description, f"Unable to fetch {param} for {vault.name}."

        if 'totalAssets' in description:
            assert "tvl" in description, f"Unable to fetch tvl for {vault.name}."
                
        assert description["strategies"], f"No strategies fetched for {vault.name}."
        for strategy in description["strategies"]:
            strat_address = description["strategies"][strategy]["address"]
            strategy = vault._strategies[strat_address]
            assert strategy._views, f"Unable to fetch views for strategy {strategy.name}."
            for view in strategy._views:
                assert view in description["strategies"][strategy], f"Unable to fetch {view} for strategy {strategy.name}."


def test_active_vaults_at_v2_current():
    assert len(registry.active_vaults_at()) >= 91, "One or more vaults are missing from v2.Registry().active_vaults_at(None)"


@pytest.mark.parametrize('block',blocks)
def test_active_vaults_at_v2(block):
    assert registry.active_vaults_at(block=block), f"Unable to fetch active v2 vaults at block {block}."


@pytest.mark.parametrize('block',blocks)
def test_total_value_at_v2(block):
    assert registry.total_value_at(block=block), f"Unable to fetch v2 tvl at block {block}."