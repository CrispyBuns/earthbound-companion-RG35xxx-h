# 1.0.11 / platform preview.23: item receipts and map edges

Item receipt messages now use the actual inventory slot filled by the reward.
This fixes Paula saying Ness received a Sand lot bat when the Franklin badge
was correctly awarded. Inventory holes and the final slot are handled without
changing the award or existing saves; key-item pool handling remains intact.

World-map tile lookups now check the east and south boundaries before computing
the sector index, preventing the east edge from reading the next map row.
This addresses a possible cause of the reported purple strip outside Paula's
cabin; the reporter's exact Android scene has not been replayed.

Original792 / Redux848 focused native checks passed, including every reward slot
and world-map bounds. Earlier PSI label, cinematic, dialogue, setup, touch
controls, achievements and icon fixes remain included. Full campaigns and
physical Android gameplay were not repeated.
