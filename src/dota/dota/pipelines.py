# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from dota.items import HeroItem, ItemItem
import re


class HeroBioPipeline:
    def process_item(self, item, spider):
        if isinstance(item, HeroItem):
            adapter = ItemAdapter(item)
            if adapter.get("bio"):
                adapter["bio"] = (
                    " ".join(adapter["bio"]).replace('"', "`").replace("\n", " ")
                )
                return item
            else:
                raise DropItem(f"Missing price in {item}")
        else:
            return item


class HeroDescriptorPipeline:
    def process_item(self, item, spider):
        if isinstance(item, HeroItem):
            adapter = ItemAdapter(item)
            if adapter.get("descriptor"):
                adapter["descriptor"] = adapter["descriptor"].strip()
                return item
            else:
                raise DropItem(f"Missing price in {item}")
        else:
            return item


class HeroDescriptionPipeline:
    def process_item(self, item, spider):
        if isinstance(item, HeroItem):
            adapter = ItemAdapter(item)
            if adapter.get("description"):
                adapter["description"] = re.sub(
                    r"\.([A-Z])",
                    r". \1",
                    adapter["description"].strip().replace('"', "`"),
                )
                return item
            else:
                raise DropItem(f"Missing price in {item}")
        else:
            return item


class HeroAbilitiesPipeline:
    def process_item(self, item, spider):
        if isinstance(item, HeroItem):
            adapter = ItemAdapter(item)
            if adapter.get("abilities"):
                abilities = {}
                old_abilities = adapter["abilities"]
                ability_names = old_abilities.keys()
                for name in ability_names:
                    old_features = adapter["abilities"][name]["features"]
                    old_description = adapter["abilities"][name]["description"]
                    old_upgrades = adapter["abilities"][name]["upgrades"]

                    new_name = name.strip()
                    new_features = self.get_ability_features(old_features)
                    new_description = self.get_ability_description(old_description)
                    new_upgrades = self.get_ability_upgrades(old_upgrades)
                    new_lore = adapter["abilities"][name]["lore"]
                    abilities[new_name] = {
                        "features": new_features,
                        "description": new_description,
                        "upgrades": new_upgrades,
                        "lore": new_lore if new_lore else "None",
                    }
                adapter["abilities"] = abilities
                return item
            else:
                raise DropItem(f"Missing price in {item}")
        else:
            return item

    def get_ability_features(self, ability_features):
        features = {}
        new_features = ability_features.strip().replace("\xa0", "").split("\n")
        for i in range(len(new_features)):
            feature = re.sub(r"\(.*?\)", "", new_features[i]).replace("  ", " ").strip()
            if "Ability" in feature:
                feature_value = feature[7:]
                features["Ability"] = feature_value
            elif "Affects" in feature:
                feature_value = feature[7:]
                features["Affects"] = feature_value
            elif "Damage" in feature:
                feature_value = feature[6:]
                features["Damage"] = feature_value
            new_features[i] = feature
        return features

    def get_ability_description(self, old_description):
        description = re.sub(
            r"\.([A-Z])",
            r". \1",
            "".join(old_description)
            .strip()
            .replace("\n", "")
            .replace('"', "`")
            .replace("/ ", "/")
            .replace(" /", "/")
            .replace("/", " / "),
        )
        return description

    def get_ability_upgrades(self, old_upgrades):
        upgrades = {}
        if old_upgrades == "None":
            upgrades["Aghanim's Scepter"] = "None"
            upgrades["Aghanim's Shard"] = "None"
        else:
            aghs_upgrades = list(
                filter(lambda item: item != "", old_upgrades.strip().split("\n"))
            )
            for i in range(0, len(aghs_upgrades), 2):
                if "Scepter" in aghs_upgrades[i]:
                    upgrades["Aghanim's Scepter"] = (
                        aghs_upgrades[i + 1]
                        .replace("/ ", "/")
                        .replace(" /", "/")
                        .replace("/", " / ")
                    )
                else:
                    upgrades["Aghanim's Scepter"] = "None"

                if "Shard" in aghs_upgrades[i]:
                    upgrades["Aghanim's Shard"] = (
                        aghs_upgrades[i + 1]
                        .replace("/ ", "/")
                        .replace(" /", "/")
                        .replace("/", " / ")
                    )
                else:
                    upgrades["Aghanim's Shard"] = "None"
        return upgrades


class HeroTalentsPipeline:
    def process_item(self, item, spider):
        if isinstance(item, HeroItem):
            adapter = ItemAdapter(item)
            if adapter.get("talents"):
                talents = {}
                old_talents = adapter["talents"]
                talent_levels = old_talents.keys()
                for level in talent_levels:
                    talents[level] = {
                        "left": old_talents[level]["left"]
                        .strip()
                        .replace("  ", " ")
                        .replace("/ ", "/")
                        .replace(" /", "/")
                        .replace("/", " / "),
                        "right": old_talents[level]["right"]
                        .strip()
                        .replace("  ", " ")
                        .replace("/ ", "/")
                        .replace(" /", "/")
                        .replace("/", " / "),
                    }
                adapter["talents"] = talents
                return item
            else:
                raise DropItem(f"Missing price in {item}")
        else:
            return item