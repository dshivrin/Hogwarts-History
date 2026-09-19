#!/usr/bin/env python3
"""Build, validate, and query the 1984 open-questions editorial overlay."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
from typing import Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PATH = Path("project-control/structured-sources/open-questions.yaml")
TOC_PATH = Path("authoring/editions/1984/table-of-contents.yaml")
ENTRY_INDEX_PATH = Path("project-control/entry-index.yaml")
EXTERNAL_MANIFEST_PATH = Path("resources/manifests/external-sources.yaml")
DEFAULT_OVERLAY_PATH = Path(
    "resources/external/open-questions-scapping/hogwarts-open-questions-enriched.yaml"
)


DESTINATION_CHAPTER = {
    "C2": 2,
    "C3": 3,
    "SORTING": 4,
    "CASTLE": 6,
    "GROUNDS": 7,
    "GOVERNANCE": 8,
    "ACADEMICS": 9,
    "ADMISSIONS": 10,
    "LIBRARY": 11,
    "GHOSTS": 12,
    "TRADITIONS": 13,
    "SPORT": 14,
    "SECURITY": 17,
    "LATER": 19,
    "OMISSION": 8,
    "CONTROL": 11,
}


CHAPTER_OVERRIDES: dict[str, tuple[int, list[int]]] = {
    "sorting-ceremony-001": (4, [13]),
    "sorting-ceremony-002": (10, [7, 13]),
    "sorting-ceremony-003": (10, [7, 13]),
    "sorting-ceremony-004": (4, [11, 13]),
    "sorting-ceremony-005": (2, [4]),
    "sorting-ceremony-006": (2, [4]),
    "founding-and-the-four-houses-001": (3, [5]),
    "founding-and-the-four-houses-002": (5, [11]),
    "founding-and-the-four-houses-003": (3, []),
    "founding-and-the-four-houses-004": (2, [5]),
    "founding-and-the-four-houses-005": (5, [2, 4]),
    "pre-hogwarts-historical-context-008": (5, [19]),
    "pre-hogwarts-historical-context-009": (5, [4]),
    "pre-hogwarts-historical-context-010": (5, [19]),
    "castle-navigation-and-magical-architecture-025": (5, [6, 17]),
    "castle-navigation-and-magical-architecture-026": (17, [5, 6]),
    "castle-rooms-and-displays-012": (17, [6]),
    "protective-magic-and-security-028": (5, [17]),
    "protective-magic-and-security-098": (17, [5]),
    "protective-magic-and-security-099": (17, [5]),
    "protective-magic-and-security-101": (5, [17]),
    "protective-magic-and-security-102": (5, [6, 17]),
    "protective-magic-and-security-103": (6, [5, 17]),
    "protective-magic-and-security-104": (5, [17]),
    "protective-magic-and-security-105": (5, [17]),
    "protective-magic-and-security-107": (5, [17]),
    "protective-magic-and-security-108": (17, [5]),
    "protective-magic-and-security-114": (5, [17]),
    "pre-hogwarts-historical-context-001": (19, [20]),
    "pre-hogwarts-historical-context-002": (20, [19]),
    "pre-hogwarts-historical-context-003": (19, []),
    "pre-hogwarts-historical-context-004": (20, [8]),
    "pre-hogwarts-historical-context-005": (20, [19]),
    "pre-hogwarts-historical-context-006": (10, [9]),
    "pre-hogwarts-historical-context-011": (19, []),
    "pre-hogwarts-historical-context-012": (19, []),
    "pre-hogwarts-historical-context-013": (10, []),
    "pre-hogwarts-historical-context-014": (10, []),
    "pre-hogwarts-historical-context-040": (9, [10]),
    "pre-hogwarts-historical-context-043": (10, []),
    "feasts-and-school-traditions-003": (19, [10]),
    "feasts-and-school-traditions-037": (10, [7, 19]),
    "protective-magic-and-security-112": (16, [17]),
    "protective-magic-and-security-113": (15, [17]),
    "protective-magic-and-security-115": (17, []),
    "protective-magic-and-security-116": (17, []),
    "protective-magic-and-security-117": (17, []),
    "rules-and-discipline-028": (18, [20]),
    "source-processing-001": (11, []),
}


SOURCE_ID_MAP = {
    "W-SORT": "A02",
    "W-HATSTALL": "A20",
    "W-BOOK": "A03",
    "W-PEEVES": "A16",
    "W-SWORD": "A08",
    "W-CHAMBER": "A01",
    "W-PENSIEVE": "A17",
    "W-TRAIN": "A04",
    "W-KINGS": "A19",
    "W-GHOSTS": "A06",
    "W-PORTRAITS": "A05",
    "W-LUPIN": "A10",
    "W-POTTER": "A38",
    "W-MCG": "A12",
    "W-MIRROR": "A14",
}


LOCAL_ALTERNATIVES = {
    "W-MAP": ["A11"],
}


REVIEWED: dict[str, dict] = {
    "sorting-ceremony-001": {
        "status": "partially_answered",
        "facts": [
            (
                "Founder-era tradition says Godric Gryffindor's former hat was jointly enchanted by the four founders to continue House assignment.",
                ["ext-a02-001"],
            )
        ],
        "residual": "When did the later ceremonial form of Sorting begin?",
        "author_question": "eligible",
    },
    "sorting-ceremony-005": {
        "status": "partially_answered",
        "facts": [
            (
                "The sword is Godric Gryffindor's goblin-made relic and can return to a worthy Gryffindor.",
                ["ext-a08-001", "ext-a08-004", "dh-ch07-006"],
            )
        ],
        "residual": "When and by what mechanism did the sword become able to appear through the Sorting Hat?",
        "author_question": "eligible",
    },
    "sorting-ceremony-006": {
        "status": "partially_answered",
        "facts": [
            (
                "The sword dates to Godric Gryffindor and is said to present itself to worthy Gryffindors.",
                ["ext-a08-001", "ext-a08-004", "dh-ch07-006"],
            )
        ],
        "residual": "When was the first connection between the sword and the Sorting Hat established, and is worthiness defined more precisely?",
        "author_question": "eligible",
    },
    "castle-navigation-and-magical-architecture-009": {
        "status": "partially_answered",
        "facts": [
            (
                "The Marauders created the map during their school years; it uses the Homonculous Charm to track people in Hogwarts and was confiscated in their final year.",
                ["ext-a11-001", "ext-a11-002", "ext-a11-004", "poa-ch17-004"],
            )
        ],
        "residual": "What was the precise creation date, and how—if at all—does the map interact with Hogwarts's own protective enchantments?",
        "author_question": "eligible",
    },
    "castle-navigation-and-magical-architecture-010": {
        "status": "partially_answered",
        "facts": [
            (
                "The map was confiscated by Argus Filch in the makers' final school year.",
                ["ext-a11-004"],
            )
        ],
        "residual": "What exact incident led to confiscation, and what policy governed the dangerous-items drawer?",
        "author_question": "eligible",
    },
    "castle-navigation-and-magical-architecture-011": {
        "status": "partially_answered",
        "facts": [
            (
                "The map was deliberately enchanted to rebuff Severus Snape's attempts to inspect it.",
                ["ext-a11-002"],
            )
        ],
        "residual": "What precise enchantment lets the map recognize and tailor insults to an unauthorized reader?",
        "author_question": "eligible",
    },
    "castle-navigation-and-magical-architecture-012": {
        "status": "partially_answered",
        "facts": [
            (
                "The map tracks people under an Invisibility Cloak and identifies people in Animagus form by their human names.",
                ["poa-ch17-004", "poa-ch17-005", "ext-a11-002"],
            )
        ],
        "residual": "How the Homonculous Charm defeats those concealments is not explained.",
        "author_question": "eligible",
    },
    "castle-navigation-and-magical-architecture-015": {
        "status": "partially_answered",
        "facts": [
            (
                "Fred and George describe seven passages on the Marauder's Map and say which are known to Filch in Harry's era.",
                ["poa-ch10-003"],
            )
        ],
        "residual": "Which passages were known to staff, caretakers, or pupils before the Marauders and before Harry's era?",
        "author_question": "eligible",
    },
    "castle-navigation-and-magical-architecture-018": {
        "status": "partially_answered",
        "facts": [
            (
                "The Mirror of Erised is ancient and had remained in the Room of Requirement for roughly a century before Dumbledore brought it out.",
                ["ext-a14-001", "ext-a14-003"],
            )
        ],
        "residual": "Who brought the mirror to Hogwarts, when exactly did it arrive, and could the 1984 historian know its hidden storage history?",
        "author_question": "eligible",
    },
    "castle-navigation-and-magical-architecture-019": {
        "status": "partially_answered",
        "facts": [
            (
                "The mirror's long-term earlier storage was in the Room of Requirement; Dumbledore later modified it to protect the Philosopher's Stone.",
                ["ext-a14-003", "ext-a14-004"],
            )
        ],
        "residual": "Was the unused classroom merely temporary storage, and what route moved the mirror there?",
        "author_question": "eligible",
        "body_eligibility": "later_context_only",
    },
    "castle-navigation-and-magical-architecture-022": {
        "status": "partially_answered",
        "facts": [
            (
                "By tradition, headmasters and headmistresses train portraits before death so knowledge can pass to successors.",
                ["ext-a05-003"],
            )
        ],
        "residual": "When did the tradition begin, and what duties or powers are formally assigned to the portraits?",
        "author_question": "eligible",
    },
    "castle-navigation-and-magical-architecture-025": {
        "status": "partially_answered",
        "facts": [
            (
                "Slytherin created the Chamber as a founder-era basilisk lair; an eighteenth-century plumbing project later altered and concealed its entrance.",
                ["ext-a01-001", "ext-a01-002"],
            )
        ],
        "residual": "Which internal architectural details are original, and which—beyond the documented entrance—were altered later?",
        "author_question": "eligible",
    },
    "castle-rooms-and-displays-013": {
        "status": "partially_answered",
        "facts": [
            (
                "The Whomping Willow was planted in Lupin's arrival year and guarded a route arranged for his transformations.",
                ["poa-ch10-002", "poa-ch18-003", "ext-a10-001"],
            )
        ],
        "residual": "What calendar year was it planted, and what formal authorization or maintenance record survives?",
        "author_question": "eligible",
    },
    "castle-rooms-and-displays-015": {
        "status": "answered_with_access_gap",
        "facts": [
            (
                "The tree and route were arranged for Lupin's attendance, and Lupin says the tree was planted in his arrival year.",
                ["poa-ch10-002", "poa-ch18-003", "ext-a10-001"],
            )
        ],
        "residual": "Could a circa-1984 historian plausibly know the confidential purpose of the arrangement?",
        "author_question": "eligible",
    },
    "ghosts-and-magical-residents-001": {
        "status": "partially_answered",
        "facts": [
            (
                "Rowling's account connects Peeves to caretaker Hankerton Humble, appointed by the four founders; an attempted removal in 1876 caused a castle evacuation.",
                ["ext-a16-001", "ext-a16-003", "ext-a16-004"],
            )
        ],
        "residual": "What evidence, if any, dates Peeves's first manifestation more precisely and establishes what the 1984 historian could know?",
        "author_question": "eligible",
    },
    "ghosts-and-magical-residents-004": {
        "status": "partially_answered",
        "facts": [
            (
                "Myrtle died as a Hogwarts pupil, returned to haunt Olive Hornby, and remained in the girls' toilet.",
                ["ext-a06-005", "gof-ch25-004"],
            )
        ],
        "residual": "What exact year did Myrtle die and return, and was that chronology available in an institutional record?",
        "author_question": "eligible",
    },
    "ghosts-and-magical-residents-006": {
        "status": "partially_answered",
        "facts": [
            (
                "Professor Binns died after falling asleep by the staffroom fire and continued teaching History of Magic as a ghost.",
                ["ext-a06-006", "ps-ch08-005"],
            )
        ],
        "residual": "When did Binns die, and therefore how long had he taught as a ghost by the 1984 cutoff?",
        "author_question": "eligible",
    },
    "pre-hogwarts-historical-context-007": {
        "status": "partially_answered",
        "facts": [
            (
                "The Quill and Book react to a child's demonstrated magic and control Hogwarts selection.",
                ["ext-a03-002", "ext-a03-003"],
            )
        ],
        "residual": "How do families, Hogwarts, and public authorities manage accidental magic before first contact?",
        "author_question": "eligible",
    },
    "pre-hogwarts-historical-context-017": {
        "status": "partially_answered",
        "facts": [
            (
                "The founders installed the Book and Quill; the Quill attempts inscription at the first sign of magic, but the Book requires compelling evidence. Neville's inscription was attempted at birth and accepted only at age eight.",
                ["ext-a03-001", "ext-a03-002", "ext-a03-003", "ext-a03-004", "ext-a03-005"],
            )
        ],
        "residual": "How are addresses and first-contact logistics derived from the admissions record?",
        "author_question": "eligible",
    },
    "feasts-and-school-traditions-003": {
        "status": "partially_answered",
        "facts": [
            (
                "The 1692 secrecy regime led to a search for mass transport; the train later became compulsory, while the concealed King's Cross platform is associated with Minister Orpington's 1849–1855 term.",
                ["ext-a04-002", "ext-a04-004", "ext-a04-005", "ext-a19-002"],
            )
        ],
        "residual": "What exact year did the Express enter service and become compulsory, and what sources were available to the 1984 historian?",
        "author_question": "eligible",
    },
    "feasts-and-school-traditions-038": {
        "status": "partially_answered",
        "facts": [
            (
                "Herbert Beery staged the pantomime while Dippet was headmaster and Dumbledore was a young Transfiguration teacher; the disaster led to a schoolwide ban.",
                ["beedle-ch02-001", "beedle-ch02-002", "beedle-ch02-005"],
            )
        ],
        "residual": "Which exact school year did the production occur?",
        "author_question": "eligible",
    },
    "protective-magic-and-security-033": {
        "status": "partially_answered",
        "facts": [
            (
                "Dumbledore's alterations made the Mirror a hiding place and moral test for the Philosopher's Stone.",
                ["ext-a14-004"],
            )
        ],
        "residual": "Does the protection represent a unique alteration, or a broader class of desire-based security magic?",
        "author_question": "not_for_original_body",
        "body_eligibility": "later_context_only",
    },
    "protective-magic-and-security-101": {
        "status": "partially_answered",
        "facts": [
            (
                "Binns preserves the pre-cutoff Chamber legend; later Rowling evidence confirms its founder-era purpose and repeated failed searches.",
                ["cos-ch09-005", "cos-ch09-006", "ext-a01-001", "ext-a01-003"],
            )
        ],
        "residual": "Which parts were plausibly accessible to the 1984 historian beyond the already attested legend?",
        "author_question": "eligible",
    },
    "protective-magic-and-security-102": {
        "status": "partially_answered",
        "facts": [
            (
                "The entrance originally used a trapdoor and was concealed beneath new plumbing by Corvinus Gaunt in the eighteenth century.",
                ["ext-a01-002"],
            )
        ],
        "residual": "What exact date and magical method were used, and could the 1984 historian know the secret intervention?",
        "author_question": "eligible",
    },
    "protective-magic-and-security-104": {
        "status": "partially_answered",
        "facts": [
            (
                "Repeated searches by Hogwarts leaders, historians, and learned witches and wizards failed to enter the Chamber without Parseltongue.",
                ["cos-ch09-006", "ext-a01-003"],
            )
        ],
        "residual": "Who conducted the individual searches, when did they occur, and what methods did they use?",
        "author_question": "eligible",
    },
    "protective-magic-and-security-115": {
        "status": "answered_later_context",
        "facts": [
            (
                "Dumbledore explains that Petunia accepting Harry sealed a blood-based protection and identifies the Howler as a reminder of that pact.",
                ["ootp-ch02-006", "ootp-ch37-005"],
            )
        ],
        "residual": None,
        "author_question": "not_for_original_body",
        "body_eligibility": "later_context_only",
    },
    "protective-magic-and-security-116": {
        "status": "answered_later_context",
        "facts": [
            (
                "Grimmauld Place is Unplottable and Dumbledore's Secret-Keeper protection conceals the Order headquarters.",
                ["ootp-ch04-001", "ootp-ch06-007"],
            )
        ],
        "residual": None,
        "author_question": "not_for_original_body",
        "body_eligibility": "later_context_only",
    },
    "protective-magic-and-security-117": {
        "status": "answered_later_context",
        "facts": [
            (
                "Umbridge privately admits that she ordered the Dementor attack on Harry.",
                ["ootp-ch08-006", "ootp-ch32-007"],
            )
        ],
        "residual": None,
        "author_question": "not_for_original_body",
        "body_eligibility": "later_context_only",
    },
}


ALLOWED_RESEARCH_STATUSES = {
    "local_search_required",
    "partially_answered",
    "answered_with_access_gap",
    "answered_later_context",
    "excluded",
    "repository_only_resolved",
}
ALLOWED_BODY_ELIGIBILITY = {
    "not_yet_eligible",
    "requires_access_review",
    "later_context_only",
    "excluded",
    "repository_only",
}
ALLOWED_INFERENCE = {
    "not_assessed",
    "none",
    "bounded_candidate",
}
ALLOWED_CREATIVE = {
    "prohibited_until_research_review",
    "prohibited",
    "candidate_after_editorial_review",
}


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate keys instead of silently losing editorial records."""


def unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"Duplicate YAML key {key!r} at line {key_node.start_mark.line + 1}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = yaml.load(handle, Loader=UniqueKeyLoader)
    if not isinstance(value, dict):
        raise ValueError(f"Expected mapping in {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def external_inventory(root: Path) -> tuple[dict[str, dict], dict[str, str]]:
    manifest = load_yaml(root / EXTERNAL_MANIFEST_PATH)
    by_logical = {
        str(row["logical_id"]): row
        for row in manifest.get("sources", [])
        if isinstance(row, dict) and row.get("logical_id")
    }
    yaml_by_id: dict[str, str] = {}
    for path in sorted((root / "sources/external").glob("**/*.yaml")):
        data = load_yaml(path)
        source_id = (data.get("source_unit") or {}).get("source_id")
        if source_id:
            yaml_by_id[str(source_id)] = path.relative_to(root).as_posix()
    return by_logical, yaml_by_id


def build_source_catalog(root: Path, legacy: dict) -> dict[str, dict]:
    by_logical, yaml_by_id = external_inventory(root)
    registry = legacy.get("source_registry") or {}
    catalog: dict[str, dict] = {
        "P-NOVELS": {
            "canonical_source_id": "P-NOVELS",
            "legacy_source_keys": ["P-NOVELS"],
            "kind": "primary_novels",
            "availability": "already_extracted",
            "authority": "primary_text",
            "local_paths": ["pdfs/harrypotter.pdf", *[f"sources/book-{number:02}" for number in range(1, 8)]],
        },
        "P-QUIDDITCH": {
            "canonical_source_id": "P-QUIDDITCH",
            "legacy_source_keys": ["P-QUIDDITCH"],
            "kind": "companion",
            "availability": "already_extracted",
            "authority": "primary_text",
            "local_paths": ["pdfs/quidditch-through-the-ages.pdf", "sources/book-qtta"],
        },
        "P-BEEDLE": {
            "canonical_source_id": "P-BEEDLE",
            "legacy_source_keys": ["P-BEEDLE"],
            "kind": "companion",
            "availability": "already_extracted",
            "authority": "primary_text",
            "local_paths": ["pdfs/Beedle The Bard_text.pdf", "sources/book-beedle"],
        },
        "P-BEASTS": {
            "canonical_source_id": "P-BEASTS",
            "legacy_source_keys": ["P-BEASTS"],
            "kind": "companion",
            "availability": "already_extracted",
            "authority": "primary_text",
            "local_paths": ["pdfs/Fantastic-Beasts-Where-to-Find-Them.pdf", "sources/book-fb"],
        },
    }

    for legacy_key, logical_id in SOURCE_ID_MAP.items():
        row = by_logical[logical_id]
        catalog[logical_id] = {
            "canonical_source_id": logical_id,
            "manifest_id": row["id"],
            "legacy_source_keys": [legacy_key],
            "kind": row["source_class"],
            "availability": "already_extracted",
            "authority": row["authority"],
            "original_url": row["original_url"],
            "snapshot_path": row["local_path"],
            "evidence_yaml": yaml_by_id[logical_id],
        }

    # The proposal pointed at an uncaptured fact file, but the stronger Rowling
    # original A11 is already present and should be searched first.
    a11 = by_logical["A11"]
    catalog["A11"] = {
        "canonical_source_id": "A11",
        "manifest_id": a11["id"],
        "legacy_source_keys": [],
        "kind": a11["source_class"],
        "availability": "already_extracted",
        "authority": a11["authority"],
        "original_url": a11["original_url"],
        "snapshot_path": a11["local_path"],
        "evidence_yaml": yaml_by_id["A11"],
    }

    mapped_legacy = set(SOURCE_ID_MAP) | set(catalog)
    for legacy_key, row in registry.items():
        if legacy_key in mapped_legacy:
            continue
        locator = str(row.get("locator") or "")
        if not locator.startswith("http"):
            continue
        catalog[legacy_key] = {
            "canonical_source_id": None,
            "legacy_source_keys": [legacy_key],
            "kind": row.get("type"),
            "availability": "candidate_unverified",
            "authority": "unverified",
            "original_url": locator,
            "search_rule": "Investigate only after indexed local evidence and local snapshots fail to answer the residual question.",
        }
    return catalog


def source_plan(legacy_question: dict, catalog: dict[str, dict]) -> tuple[list[str], list[str]]:
    local: list[str] = []
    candidates: list[str] = []
    for legacy_key in (legacy_question.get("research") or {}).get("search_first", []):
        if legacy_key in SOURCE_ID_MAP:
            source_id = SOURCE_ID_MAP[legacy_key]
            if source_id not in local:
                local.append(source_id)
            continue
        for source_id in LOCAL_ALTERNATIVES.get(legacy_key, []):
            if source_id not in local:
                local.append(source_id)
        row = catalog.get(legacy_key)
        if row and row["availability"] == "already_extracted":
            if legacy_key not in local:
                local.append(legacy_key)
        elif row and row["availability"] == "candidate_unverified":
            if legacy_key not in candidates:
                candidates.append(legacy_key)
    return local, candidates


def placement_for(legacy_question: dict) -> tuple[int, list[int]]:
    question_id = str(legacy_question["id"])
    if question_id in CHAPTER_OVERRIDES:
        return CHAPTER_OVERRIDES[question_id]
    editorial = legacy_question.get("editorial") or {}
    primary_key = editorial.get("primary_destination")
    primary = DESTINATION_CHAPTER[primary_key]
    secondary = [
        DESTINATION_CHAPTER[key]
        for key in editorial.get("secondary_destinations", [])
        if key in DESTINATION_CHAPTER and DESTINATION_CHAPTER[key] != primary
    ]
    return primary, sorted(set(secondary))


def default_interpretation(legacy_question: dict) -> dict:
    mode = (legacy_question.get("editorial") or {}).get("mode")
    if mode == "excluded_topic":
        return {
            "body_eligibility": "excluded",
            "author_question": "prohibited",
            "historical_inference": "none",
            "creative_reconstruction": "prohibited",
            "note": "Excluded by the 1984 edition bible; retain only for omission awareness.",
        }
    if mode == "technical_only":
        return {
            "body_eligibility": "repository_only",
            "author_question": "prohibited",
            "historical_inference": "none",
            "creative_reconstruction": "prohibited",
            "note": "Repository process item; never manuscript content.",
        }
    if mode == "later_editorial_context":
        return {
            "body_eligibility": "later_context_only",
            "author_question": "not_for_original_body",
            "historical_inference": "none",
            "creative_reconstruction": "prohibited",
            "note": "Retain as later context; do not place the later event or testimony in the 1984 body.",
        }
    return {
        "body_eligibility": "not_yet_eligible",
        "author_question": "not_assessed",
        "historical_inference": "not_assessed",
        "creative_reconstruction": "prohibited_until_research_review",
        "note": "Complete local evidence review before selecting any narrative treatment.",
    }


def build_question(legacy_question: dict, catalog: dict[str, dict]) -> dict:
    question_id = str(legacy_question["id"])
    local_sources, external_candidates = source_plan(legacy_question, catalog)
    original_tags = [
        str(tag)
        for tag in legacy_question.get("tags", [])
        if not str(tag).startswith("oq-")
    ]
    primary, secondary = placement_for(legacy_question)
    interpretation = default_interpretation(legacy_question)
    reviewed = REVIEWED.get(question_id)

    if reviewed:
        facts = [
            {"statement": statement, "evidence_ids": evidence_ids}
            for statement, evidence_ids in reviewed["facts"]
        ]
        status = reviewed["status"]
        residual = reviewed.get("residual")
        body_eligibility = reviewed.get("body_eligibility", "requires_access_review")
        interpretation = {
            "body_eligibility": body_eligibility,
            "author_question": reviewed.get("author_question", "eligible"),
            "historical_inference": "bounded_candidate" if residual and body_eligibility != "later_context_only" else "none",
            "creative_reconstruction": (
                "candidate_after_editorial_review"
                if residual and body_eligibility != "later_context_only"
                else "prohibited"
            ),
            "note": "Verified facts may be used only within their stated limits; any residual gap remains non-canonical.",
        }
        gap_status = "actual_gap" if residual else "no_residual_gap"
    elif question_id.startswith("house-elves-and-hogwarts-"):
        facts = []
        status = "excluded"
        residual = legacy_question["question"]
        gap_status = "excluded_from_manuscript"
    elif question_id == "source-processing-001":
        local_sources = ["P-NOVELS"]
        facts = []
        status = "repository_only_resolved"
        residual = None
        gap_status = "repository_only"
        interpretation["note"] = (
            "The current schema already uses PDF pages plus text anchors, external content hashes, and hashed Cursed Child passage locators."
        )
    else:
        facts = []
        status = "local_search_required"
        residual = legacy_question["question"]
        gap_status = "not_yet_reviewed"

    return {
        "research": {
            "status": status,
            "verified_facts": facts,
            "local_source_ids": local_sources,
            "external_candidate_ids": external_candidates,
            "query_tags": original_tags[:6],
            "next_action": (
                "Inspect docs/instructions/schema-reference.md and scripts/validate_source_yaml.py alongside the local PDF corpus to verify locator policy."
                if status == "repository_only_resolved"
                else "No further lore research; retain the editorial disposition."
                if status in {"answered_later_context", "excluded", "repository_only_resolved"}
                else (
                    "Search the entry index with query_tags; inspect local_source_ids and canonical YAML, "
                    "then local snapshots/PDFs. Resolve: " + str(residual)
                )
            ),
        },
        "gap": {
            "status": gap_status,
            "residual_question": residual,
        },
        "placement": {
            "primary_chapter_id": primary,
            "secondary_chapter_ids": secondary,
        },
        "interpretation": interpretation,
    }


def build_overlay(root: Path, legacy: dict) -> dict:
    canonical_path = root / CANONICAL_PATH
    canonical = load_yaml(canonical_path)
    catalog = build_source_catalog(root, legacy)
    legacy_by_id = {
        str(row["id"]): row for row in legacy.get("questions", []) if isinstance(row, dict)
    }
    questions = {}
    for canonical_question in canonical.get("questions", []):
        question_id = str(canonical_question["id"])
        if question_id not in legacy_by_id:
            raise ValueError(f"Legacy proposal is missing canonical question {question_id}")
        # Legacy contributes editorial leads, never canonical wording or tags.
        input_row = {**legacy_by_id[question_id], **canonical_question}
        questions[question_id] = build_question(input_row, catalog)
    return {
        "schema_version": 1,
        "updated": "2026-09-18",
        "purpose": "Editorial overlay for researching and using canonical open questions without modifying the canonical question store.",
        "canonical_questions": {
            "path": CANONICAL_PATH.as_posix(),
            "version": canonical.get("version"),
            "sha256": sha256(canonical_path),
            "question_count": len(canonical.get("questions", [])),
        },
        "chapter_plan": {
            "path": TOC_PATH.as_posix(),
            "schema_version": load_yaml(root / TOC_PATH).get("schema_version"),
            "chapter_count": len(load_yaml(root / TOC_PATH).get("chapters", [])),
        },
        "policy": {
            "search_order": [
                "indexed_local_evidence",
                "exact_canonical_yaml",
                "local_snapshots_and_pdfs",
                "external_candidates_only_if_residual_gap_remains",
            ],
            "facts_require_evidence_ids": True,
            "inference_is_not_canonical": True,
            "creative_reconstruction_is_not_canonical": True,
            "creative_reconstruction_requires_completed_research_and_editorial_review": True,
            "questions_may_remain_unanswered": True,
        },
        "source_catalog": catalog,
        "questions": questions,
    }


def validate_overlay(root: Path, overlay: dict) -> list[str]:
    """Validate references and editorial safeguards without changing repository data."""
    errors: list[str] = []
    canonical = load_yaml(root / CANONICAL_PATH)
    canonical_ids = [row["id"] for row in canonical["questions"]]
    toc = load_yaml(root / TOC_PATH)
    chapter_ids = {row["id"] for row in toc["chapters"]}
    entries = load_yaml(root / ENTRY_INDEX_PATH)["by_entry"]
    manifest, yaml_by_id = external_inventory(root)
    inventory = load_yaml(root / "project-control/source-index.yaml")["processed_units"]
    inventory_paths = {row["source_file"] for row in inventory} | {row["output_yaml"] for row in inventory}
    inventory_directories = {str(Path(row["output_yaml"]).parent) for row in inventory}

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    def mapping(value, label):
        if not isinstance(value, dict):
            errors.append(f"{label}: must be a mapping")
            return {}
        return value

    def values(value, label):
        if not isinstance(value, list):
            errors.append(f"{label}: must be a list")
            return []
        if any(not text(item) for item in value):
            errors.append(f"{label}: must contain non-empty strings")
            return []
        if len(value) != len(set(value)):
            errors.append(f"{label}: duplicate values")
        return value

    def enum(value, allowed, label):
        if not isinstance(value, str) or value not in allowed:
            errors.append(f"{label}: invalid value {value!r}")

    def local_path(value):
        return text(value) and not Path(value).is_absolute() and ".." not in Path(value).parts and (root / value).exists()

    if overlay.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    meta = mapping(overlay.get("canonical_questions"), "canonical_questions")
    expected = {"path": CANONICAL_PATH.as_posix(), "sha256": sha256(root / CANONICAL_PATH),
                "question_count": len(canonical_ids), "version": canonical.get("version")}
    for key, value in expected.items():
        if meta.get(key) != value:
            errors.append(f"canonical_questions.{key}: does not match current canonical file")
    chapter_meta = mapping(overlay.get("chapter_plan"), "chapter_plan")
    for key, value in {"path": TOC_PATH.as_posix(), "schema_version": toc.get("schema_version"), "chapter_count": len(chapter_ids)}.items():
        if chapter_meta.get(key) != value:
            errors.append(f"chapter_plan.{key}: does not match current outline")

    catalog = mapping(overlay.get("source_catalog"), "source_catalog")
    for source_id, raw_source in catalog.items():
        source = mapping(raw_source, f"source {source_id}")
        availability = source.get("availability")
        if availability == "already_extracted":
            if source.get("canonical_source_id") != source_id:
                errors.append(f"source {source_id}: canonical source ID mismatch")
            if source_id in manifest:
                row = manifest[source_id]
                for key, expected_value in {"manifest_id": row["id"], "snapshot_path": row["local_path"],
                                            "evidence_yaml": yaml_by_id.get(source_id), "original_url": row["original_url"],
                                            "authority": row["authority"], "kind": row["source_class"]}.items():
                    if source.get(key) != expected_value:
                        errors.append(f"source {source_id}: {key} does not match inventory")
                for key in ("snapshot_path", "evidence_yaml"):
                    if not local_path(source.get(key)):
                        errors.append(f"source {source_id}: missing local {key}")
            elif source_id in {"P-NOVELS", "P-BEEDLE", "P-QUIDDITCH", "P-BEASTS"}:
                paths = values(source.get("local_paths"), f"source {source_id}.local_paths")
                if not paths:
                    errors.append(f"source {source_id}: requires inventory paths")
                for path in paths:
                    if not local_path(path) or path not in inventory_paths | inventory_directories:
                        errors.append(f"source {source_id}: unavailable or unindexed path {path}")
            else:
                errors.append(f"source {source_id}: missing from source inventory")
        elif availability == "candidate_unverified":
            if source.get("canonical_source_id") is not None or source.get("authority") != "unverified":
                errors.append(f"source {source_id}: candidate cannot claim verified authority or canonical ID")
            if not str(source.get("original_url") or "").startswith(("https://", "http://")):
                errors.append(f"source {source_id}: candidate requires external URL")
        else:
            errors.append(f"source {source_id}: invalid availability")

    questions = mapping(overlay.get("questions"), "questions")
    if list(questions) != canonical_ids or len(questions) != 386:
        errors.append("overlay question IDs/order must exactly match all 386 canonical questions")
    evidence_files = {}
    gap_for_status = {"local_search_required": "not_yet_reviewed", "partially_answered": "actual_gap",
                      "answered_with_access_gap": "actual_gap", "answered_later_context": "no_residual_gap",
                      "excluded": "excluded_from_manuscript", "repository_only_resolved": "repository_only"}
    for question_id, raw in questions.items():
        row = mapping(raw, str(question_id))
        if set(row) != {"research", "gap", "placement", "interpretation"}:
            errors.append(f"{question_id}: fields must be research, gap, placement, interpretation")
        research, gap, placement, interpretation = [mapping(row.get(key), f"{question_id}.{key}")
                                                   for key in ("research", "gap", "placement", "interpretation")]
        status = research.get("status")
        enum(status, ALLOWED_RESEARCH_STATUSES, f"{question_id}.research.status")
        facts = research.get("verified_facts")
        if not isinstance(facts, list):
            errors.append(f"{question_id}: verified_facts must be a list")
            facts = []
        if status in ("partially_answered", "answered_with_access_gap", "answered_later_context") and not facts:
            errors.append(f"{question_id}: reviewed answer requires verified facts")
        if status in ("local_search_required", "excluded", "repository_only_resolved") and facts:
            errors.append(f"{question_id}: disposition must not assert verified lore")
        for raw_fact in facts:
            fact = mapping(raw_fact, f"{question_id}.fact")
            if set(fact) != {"statement", "evidence_ids"} or not text(fact.get("statement")):
                errors.append(f"{question_id}: fact requires only statement and evidence_ids")
            evidence = values(fact.get("evidence_ids"), f"{question_id}.evidence_ids")
            if not evidence:
                errors.append(f"{question_id}: fact requires evidence IDs")
            for evidence_id in evidence:
                if evidence_id not in entries:
                    errors.append(f"{question_id}: unresolved evidence ID {evidence_id}")
                    continue
                path = entries[evidence_id].get("output_yaml")
                if not local_path(path):
                    errors.append(f"{question_id}: evidence YAML missing for {evidence_id}")
                    continue
                if path not in evidence_files:
                    evidence_files[path] = {entry["id"] for entry in load_yaml(root / path).get("entries", [])}
                if evidence_id not in evidence_files[path]:
                    errors.append(f"{question_id}: evidence ID absent from canonical YAML: {evidence_id}")
        for key, availability in (("local_source_ids", "already_extracted"), ("external_candidate_ids", "candidate_unverified")):
            source_ids = values(research.get(key), f"{question_id}.{key}")
            if key == "local_source_ids" and not source_ids:
                errors.append(f"{question_id}: local sources to inspect are required")
            for source_id in source_ids:
                source = catalog.get(source_id)
                if not isinstance(source, dict) or source.get("availability") != availability:
                    errors.append(f"{question_id}: unresolved or incorrectly classified source {source_id}")
        if not values(research.get("query_tags"), f"{question_id}.query_tags"):
            errors.append(f"{question_id}: query tags required")
        if not text(research.get("next_action")):
            errors.append(f"{question_id}: concrete next action required")
        if isinstance(status, str) and gap.get("status") != gap_for_status.get(status):
            errors.append(f"{question_id}: gap status inconsistent with research status")
        if status in ("partially_answered", "answered_with_access_gap", "local_search_required") and not text(gap.get("residual_question")):
            errors.append(f"{question_id}: partial/unreviewed answer requires residual question")
        primary = placement.get("primary_chapter_id")
        if type(primary) is not int or primary not in chapter_ids:
            errors.append(f"{question_id}: invalid primary chapter ID")
        secondary = placement.get("secondary_chapter_ids")
        if not isinstance(secondary, list):
            errors.append(f"{question_id}: secondary chapters must be a list")
        else:
            seen = []
            for chapter_id in secondary:
                if type(chapter_id) is not int or chapter_id not in chapter_ids or chapter_id == primary or chapter_id in seen:
                    errors.append(f"{question_id}: invalid or repeated secondary chapter ID")
                seen.append(chapter_id)
        enum(interpretation.get("body_eligibility"), ALLOWED_BODY_ELIGIBILITY, f"{question_id}.body_eligibility")
        enum(interpretation.get("historical_inference"), ALLOWED_INFERENCE, f"{question_id}.historical_inference")
        enum(interpretation.get("creative_reconstruction"), ALLOWED_CREATIVE, f"{question_id}.creative_reconstruction")
        enum(interpretation.get("author_question"), {"eligible", "not_assessed", "prohibited", "not_for_original_body"}, f"{question_id}.author_question")
        required_body = None
        if str(question_id).startswith("house-elves-and-hogwarts-"):
            required_body = "excluded"
            if status != "excluded":
                errors.append(f"{question_id}: house-elf questions must remain excluded")
        elif question_id == "source-processing-001":
            required_body = "repository_only"
            if status != "repository_only_resolved":
                errors.append(f"{question_id}: source processing must remain repository-only")
        elif status == "answered_later_context":
            required_body = "later_context_only"
        if required_body and interpretation.get("body_eligibility") != required_body:
            errors.append(f"{question_id}: body eligibility must be {required_body}")
        if interpretation.get("body_eligibility") in ("excluded", "repository_only", "later_context_only"):
            if interpretation.get("creative_reconstruction") != "prohibited" or interpretation.get("historical_inference") != "none":
                errors.append(f"{question_id}: excluded/repository/later context cannot authorize narrative reconstruction")
        if status == "local_search_required" and interpretation.get("creative_reconstruction") not in ("prohibited", "prohibited_until_research_review"):
            errors.append(f"{question_id}: unreviewed question cannot authorize creative use")
    return errors


def questions_for_chapter(overlay: dict, chapter_id: int) -> dict[str, dict]:
    result = {}
    for question_id, row in overlay.get("questions", {}).items():
        placement = row.get("placement") or {}
        if chapter_id == placement.get("primary_chapter_id") or chapter_id in placement.get(
            "secondary_chapter_ids", []
        ):
            result[question_id] = row
    return result


def query_payload(root: Path, overlay: dict, chapter_id: int) -> dict:
    canonical = load_yaml(root / CANONICAL_PATH)
    canonical_by_id = {
        str(row["id"]): row for row in canonical.get("questions", []) if isinstance(row, dict)
    }
    rows = []
    for question_id, overlay_row in questions_for_chapter(overlay, chapter_id).items():
        original = canonical_by_id[question_id]
        rows.append(
            {
                "id": question_id,
                "topic": original.get("topic"),
                "question": original.get("question"),
                **overlay_row,
            }
        )
    return {"chapter_id": chapter_id, "question_count": len(rows), "questions": rows}


def write_yaml(path: Path, value: dict) -> None:
    path.write_text(
        yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    subparsers = parser.add_subparsers(dest="command", required=True)

    migrate = subparsers.add_parser("migrate", help="Build the overlay from the legacy proposal")
    migrate.add_argument("--legacy", type=Path, required=True)
    migrate.add_argument("--output", type=Path, default=DEFAULT_OVERLAY_PATH)

    validate = subparsers.add_parser("validate", help="Validate an existing overlay")
    validate.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY_PATH)

    query = subparsers.add_parser("query", help="Return questions relevant to one chapter")
    query.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY_PATH)
    query.add_argument("--chapter", type=int, required=True)
    return parser.parse_args(list(argv) if argv is not None else None)


def resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    if args.command == "migrate":
        legacy = load_yaml(resolve(root, args.legacy))
        overlay = build_overlay(root, legacy)
        errors = validate_overlay(root, overlay)
        if errors:
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        output = resolve(root, args.output)
        write_yaml(output, overlay)
        try:
            display_path = output.relative_to(root)
        except ValueError:
            display_path = output
        print(
            f"Wrote {len(overlay['questions'])} open-question overlay records to "
            f"{display_path}"
        )
        return 0
    overlay = load_yaml(resolve(root, args.overlay))
    if args.command == "validate":
        errors = validate_overlay(root, overlay)
        if errors:
            print("Open-question overlay validation failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print(f"Open-question overlay validation passed ({len(overlay['questions'])} questions).")
        return 0
    payload = query_payload(root, overlay, args.chapter)
    print(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
