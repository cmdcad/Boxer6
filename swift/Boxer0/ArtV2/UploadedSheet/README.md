# Boxer0 V2 production artwork

The live asset catalog now contains 148 replacement frames: 74 blue and 74 orange. Stages A–E contain blue production frames and their source/rebuild tools; Stage F contains orange palette variants. The original uploaded sheet is `uploaded_sprites_original.png`.

Start with `INTEGRATION.md` for validation, remaining device checks and rollback. `integration_results.json` maps every installed catalog to its source and hash. `pre_v2_live_assets.zip` is the retained original-art rollback archive.

Superseded alternative artwork, failed extraction scripts, historical manual handoff notes, redundant export ZIPs and build caches were removed. `cleanup_results.json` lists the removals. Stage README files retain useful production limitations; their historical “not integrated” statements are superseded by INTEGRATION.md.

Rebuild package ZIPs only when an export is needed. The production source folders are authoritative; do not run legacy IdleAnimation generators against the live catalog.
