from .bases import PseudoValidationBase
from ..logic import ItemMappingData, LocationData, OptionData, OriginData, PseudoregaliaData, RefRuleData, RegionData, \
    RuleData, TagData, TagGroupData


def create_mock_rule(
        *, and_: list[RuleData] | None = None, or_: list[RuleData] | None = None,
        has: str | list[str] | dict[str, int] | None = None, can_reach_region: str | None = None,
        ref: str | None = None, tags: dict[str, int] | None = None, options: OptionData | None = None) -> RuleData:
    return RuleData(and_, or_, has, can_reach_region, ref, tags, options)

def create_mock_data(
        *, item_mapping: ItemMappingData = {}, tags: list[TagData] = [], tag_groups: list[TagGroupData] = [],
        ref_rules: list[RefRuleData] = [], regions: list[RegionData] = [], origins: list[OriginData] = [],
        locations: list[LocationData] = [], completion_rule: RuleData = create_mock_rule()) -> PseudoregaliaData:
    return PseudoregaliaData(item_mapping, tags, tag_groups, ref_rules, regions, origins, locations, completion_rule)


class TestValidationItemMappingFailure(PseudoValidationBase):
    data = create_mock_data(item_mapping={"non_existant_item": "fake_pseudo_item"})
    expect_errors = True


class TestValidationTagWithNoDifficulties(PseudoValidationBase):
    data = create_mock_data(tags=[])

# TODO: add tests for each CHECK in validate.py
