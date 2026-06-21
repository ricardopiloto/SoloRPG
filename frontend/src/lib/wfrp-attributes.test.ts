import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { computeSkillTarget, formatSkillRowMeta, type SkillCatalogEntry } from "./wfrp-attributes";

describe("formatSkillRowMeta", () => {
  it("shows WFRP advance format when advances > 0", () => {
    assert.equal(formatSkillRowMeta("Fel", 4), "4+[Fel]");
  });

  it("shows only attribute tag when advances === 0", () => {
    assert.equal(formatSkillRowMeta("Ag", 0), "[Ag]");
  });

  it("shows high advances before attribute", () => {
    assert.equal(formatSkillRowMeta("BS", 5), "5+[BS]");
  });
});

describe("pregen skill row meta", () => {
  const catalog: SkillCatalogEntry[] = [
    { name: "Armas Corpo a Corpo (Básicas)", linked_attribute: "WS" },
    { name: "Conhecimento (Magia)", linked_attribute: "Int" },
    { name: "Furtividade", linked_attribute: "Ag" },
  ];

  it("Helena: Armas Corpo a Corpo (Básicas) → 1+[WS]", () => {
    assert.equal(formatSkillRowMeta("WS", 1), "1+[WS]");
  });

  it("Tobias: Conhecimento (Magia) → 2+[Int]", () => {
    assert.equal(formatSkillRowMeta("Int", 2), "2+[Int]");
  });

  it("unowned skill: target equals attribute only", () => {
    const helenaAttributes = {
      WS: 42,
      BS: 33,
      S: 35,
      T: 38,
      I: 32,
      Ag: 34,
      Dex: 28,
      Int: 29,
      WP: 31,
      Fel: 27,
    };
    assert.equal(formatSkillRowMeta("Ag", 0), "[Ag]");
    assert.equal(
      computeSkillTarget(helenaAttributes, "Furtividade", catalog, []),
      34
    );
  });
});
