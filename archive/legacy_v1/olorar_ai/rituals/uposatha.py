from ..wisdom.gems import WisdomVault

def perform_uposatha(vault: WisdomVault):
    """
    The Cycle of Purification.
    Removes low-weight gems and prevents logic calcification.
    """
    # Filter: Keep only Tier 3 gems or high-weight active gems
    active_gems = [
        g for g in vault.gems
        if g.tier == 3 or g.weight > 0.5
    ]

    vault.gems = active_gems
    return "PURIFICATION_COMPLETE"
