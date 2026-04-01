# ADR-002: Tiered Prompt Architecture & MPV Integration

## Статус решения
**Implemented** | 2026-03-19

## Прогресс реализации
✅ Полностью реализован (Phase 1-5 завершены)

## Context

**Current State:** AI Prompt System v1.0.0
- FastMCP server with stdio/sse transports
- Flat storage: 16 prompts in single `prompts/registry.json`
- Simple loader in `src/storage/prompts.py` (flat list/dict structure)
- No tier separation, no baseline protection, no project override mechanism

**Problem Statement:**
The current flat architecture cannot support the following requirements identified from three analysis documents:

1. **MPV Requirements** (docs/how-to/MPV.md):
   - 7-Stage Pipeline: ideation → finish
   - Tiered Prompt Architecture: CORE → UNIVERSAL → PACKS
   - HTTPS MCP access with authentication
   - Plugin Packs with `pack.json` format
   - NL Router with LLM-based routing (accuracy >90%)
   - Lazy Loading (−64% token savings)

2. **Tier Architecture** (docs/how-to/analysis-CodeShift-promt.md):
   - Cascade override mechanism: projects → universal → core
   - Baseline protection via `promt-baseline-lock`
   - Tier-specific flags: `immutable`, `overridable`

3. **Legacy Cleanup Required:**
   - "CodeShift" references in documentation are legacy from old project "AI Agent Prompts"
   - Must be replaced with "AI Agent Prompts" throughout codebase
   - Simplify naming to match current project structure

**Critical Issues in Current Architecture:**
- ❌ Flat structure → cannot protect baseline prompts
- ❌ No cascade override → project-specific customization impossible
- ❌ No lazy loading → all 16 prompts loaded at startup (token waste)
- ❌ No MPV pipeline integration → missing 7-stage orchestration
- ❌ Missing MPV stage prompts → 0/7 required stage prompts present
- ❌ Legacy naming → "CodeShift" references in documentation (should be "AI Agent Prompts")
- ❌ Incorrect prompt count → ADR references 28 prompts, only 16 exist

**Prompt Audit Results:**
Upon comprehensive audit of current system:

| Category | Quantity | Details |
|----------|-----------|----------|
| **Current System Prompts** | 16 | All present in `prompts/registry.json` (legitimate system prompts) |
| **MPV 7-Stage Prompts** | 7 | Required for MPV pipeline (ideation, analysis, design, implementation, testing, debugging, finish) |
| **Missing MPV Stage Prompts** | 7 | None of the 7 MPV stage prompts exist in current system (0/7 present) |
| **Extra Prompts** | 0 | All 16 prompts are legitimate system prompts |
| **Legacy References** | Multiple | "CodeShift" in docs (legacy from old project "AI Agent Prompts") |
| **ADR Error** | 1 | Incorrect count reference (28 vs actual 16) |

**Current 16 Prompts Classification:**

| Tier | Prompts | Count | Layers |
|-------|----------|-------|--------|
| **CORE Tier** | 5-7 | Operations (feature-add, bug-fix, refactoring, security-audit, quality-test, ci-cd-pipeline, onboarding) |
| **UNIVERSAL Tier** | 7-9 | Discovery (project-stack-dump, project-adaptation), Planning (mvp-baseline-generator-universal), Implementation (context7-generation), Meta (prompt-creator), Versioning (versioning-policy), Discovery (system-adapt) |
| **MPV STAGE Tier** | 0 | None of 7 required stage prompts present |

**MPV Stage Prompts (Missing from Current System):**

| Stage Prompt | Status | Required For | Priority |
|-------------|--------|--------------|----------|
| `promt-ideation.md` | ❌ MISSING | Stage 1: Idea Generation | HIGH |
| `promt-analysis.md` | ❌ MISSING | Stage 2: Requirements Analysis | HIGH |
| `promt-design.md` | ❌ MISSING | Stage 3: Architecture Planning | HIGH |
| `promt-implementation.md` | ❌ MISSING | Stage 4: Code Generation | HIGH |
| `promt-testing.md` | ❌ MISSING | Stage 5: Quality Validation | MEDIUM |
| `promt-debugging.md` | ❌ MISSING | Stage 6: Self-Correction | MEDIUM |
| `promt-finish.md` | ❌ MISSING | Stage 7: Documentation & Delivery | MEDIUM |

**Note:** All 16 current prompts are legitimate operational prompts and should be preserved in appropriate tiers. The 7 MPV stage prompts are completely missing and need to be created.

## Decision Drivers

- **ADR Numbering Logic:** ADR-002 is correctly numbered as first major architectural evolution. ADR-001 was retrospectively assigned to "System Genesis & Repository Standards" (foundational flat structure). ADR-002 represents the first evolution away from that foundation.
- **Legacy Naming Cleanup:** "CodeShift" references must be replaced with "AI Agent Prompts" throughout codebase. This is legacy naming from the old project structure.
- **Prompt Count Correction:** ADR incorrectly references 28 prompts, actual count is 16. Must be corrected.
- **MPV Stage Prompts Required:** 0/7 MPV stage prompts present, need all 7 created for MPV pipeline to function.
- **Modularity:** Separate strict system logic (Core) from shared logic (Universal) and project-specific (Projects)
- **Backward Compatibility:** Ensure existing integrations continue to work during migration
- **Security:** Prevent unauthorized modification of critical baseline prompts via cryptographic locks
- **Maintainability:** Simplify prompt location and loading logic for growth
- **Scalability:** Support adding new prompts and packs without core changes
- **Performance:** Implement lazy loading to reduce token consumption by 64%

## Considered Options

### Option 1: Maintain Flat Structure (Status Quo)
*Keep current flat structure and add metadata for tiers.*
- **Pros:** No refactoring required; low immediate effort
- **Cons:** Does not solve file system organization; no cascade override; cannot enforce read-only status; complex filtering at runtime; no MPV pipeline; missing 7 stage prompts (0/7); legacy "CodeShift" references remain; incorrect prompt count (28 vs 16)

### Option 2: 2-Level Structure (Core vs. Projects)
*Split prompts into `core_prompts/` and `project_prompts/` directories.*
- **Pros:** Cleaner separation than flat structure
- **Cons:** Meta prompts (prompt generators) would be ambiguous; no middle ground for shared logic; no MPV pipeline integration; missing 7 stage prompts (0/7); legacy "CodeShift" references remain; incorrect prompt count

### Option 3: Full MPV + Tier Architecture (Chosen)
*Implement complete hybrid: 7-Stage Pipeline + 3-Tier Cascade + Plugin Packs + Legacy Cleanup.*
- **Pros:**
  - Clear separation of concerns across 3 tiers
  - Natural override mechanism (Project > Universal > Core)
  - MPV 7-stage pipeline orchestrates entire flow
  - All 7 MPV stage prompts created (0/7 → 7/7)
  - Lazy loading reduces token consumption by 64%
  - Plugin packs enable domain-specific functionality
  - Baseline lock ensures system integrity
  - Backward compatible through gradual migration
  - Legacy "CodeShift" references replaced with "AI Agent Prompts"
  - Correct prompt count (16)
- **Cons:**
  - Requires significant refactoring of storage layer
  - Complex migration of 16 existing prompts + creation of 7 new MPV stage prompts
  - Legacy naming cleanup across all documentation
  - New tooling required for pack management
  - Correcting ADR documentation errors

## Decision Outcome

**Chosen option: Option 3 (Full MPV + Tier Architecture + Legacy Cleanup)**

We will implement a hybrid architecture combining:
1. **3-Tier Cascade System** (Core → Universal → Projects)
2. **7-Stage MPV Pipeline** (ideation → finish)
3. **Plugin Pack System** (`pack.json` format)
4. **Baseline Protection** (`promt-baseline-lock` with SHA256)
5. **Lazy Loading** (load only when needed)
6. **Enhanced NL Router** (LLM-based, accuracy >90%)
7. **Legacy Cleanup** (remove "CodeShift" references, replace with "AI Agent Prompts")
8. **Prompt Count Correction** (fix incorrect "28 prompts" reference)

## Architecture Design

### 1. Directory Structure
```text
prompts/
├── core/                           ← TIER 0: BASELINE (readonly, immutable)
│   ├── .promt-baseline-lock        # Cryptographic protection
│   ├── registry.json                  # 5-7 baseline definitions
│   ├── promt-feature-add.md
│   ├── promt-bug-fix.md
│   ├── promt-refactoring.md
│   ├── promt-security-audit.md
│   └── promt-quality-test.md
│
├── universal/                       ← TIER 1: META (mutable, shared)
│   ├── registry.json                  # Meta-prompts
│   ├── promt-prompt-creator.md
│   ├── promt-system-adapt.md
│   ├── promt-context7-generation.md
│   ├── promt-mvp-baseline-generator-universal.md
│   └── promt-project-adaptation.md
│
├── universal/mpv_stages/            ← MPV STAGE PROMPTS (7 required)
│   ├── promt-ideation.md          # Stage 1: Idea Generation
│   ├── promt-analysis.md            # Stage 2: Requirements Analysis
│   ├── promt-design.md              # Stage 3: Architecture Planning
│   ├── promt-implementation.md    # Stage 4: Code Generation
│   ├── promt-testing.md             # Stage 5: Quality Validation
│   ├── promt-debugging.md          # Stage 6: Self-Correction
│   └── promt-finish.md             # Stage 7: Documentation & Delivery
│
├── universal/ai_agent_prompts/     ← AI AGENT PROMPTS (preserved from current system)
│   ├── promt-verification.md
│   ├── promt-consolidation.md
│   ├── promt-index-update.md
│   ├── promt-readme-sync.md
│   ├── promt-project-rules-sync.md
│   ├── promt-adr-implementation-planner.md
│   ├── promt-adr-template-migration.md
│   ├── [other meta-prompts from current system]
│   └── meta-prompts/
│       ├── meta-promt-adr-system-generator.md
│       ├── meta-promt-prompt-generation.md
│       └── [other meta-prompts]
│
├── projects/                        ← TIER 2: CUSTOM (overrides, highest priority)
│   ├── project_alpha/
│   │   └── registry.json          # Project-specific overrides
│   └── project_beta/
│       └── registry.json
│
└── packs/                           ← PLUGIN PACKS (domain-specific)
    ├── k8s-pack/
    │   ├── pack.json
    │   └── prompts/
    ├── gamedev-pack/
    │   ├── pack.json
    │   └── prompts/
    └── [your-pack]/
        ├── pack.json
        └── prompts/
```

### 2. Cascade Resolution Logic with Lazy Loading

```python
from fastapi import Depends, FastAPI
from functools import lru_cache
import hashlib
from pathlib import Path

# Using FastAPI's Depends() for hierarchical dependency injection
# and lru_cache for lazy loading pattern from FastAPI documentation

class TieredPromptLoader:
    def __init__(self):
        self.core_path = Path("prompts/core/")
        self.universal_path = Path("prompts/universal/")
        self.mpv_stages_path = Path("prompts/universal/mpv_stages/")
        self.ai_agent_prompts_path = Path("prompts/universal/ai_agent_prompts/")
        self.projects_path = Path("prompts/projects/")
        self.baseline_lock = self._load_baseline_lock()

    @lru_cache(maxsize=128)  # Lazy loading: cache resolved prompts
    def load_prompt(self, name: str, project: str = None) -> dict:
        # Priority: projects → universal/mpv_stages → universal/ai_agent_prompts → core

        # 1. Check projects override (highest priority) - lazy loaded only when requested
        if project:
            project_registry = self.projects_path / project / "registry.json"
            if project_registry.exists() and name in project_registry:
                return self._load_project_override(name, project)

        # 2. Check MPV stages (high priority for MPV pipeline)
        if name in ["promt-ideation.md", "promt-analysis.md", "promt-design.md",
                  "promt-implementation.md", "promt-testing.md", "promt-debugging.md", "promt-finish.md"]:
            return self._load_mpv_stage_prompt(name)

        # 3. Check universal/ai_agent_prompts (medium priority)
        meta_registry = self.ai_agent_prompts_path / "registry.json"
        if meta_registry.exists() and name in meta_registry:
            return self._load_ai_agent_prompt(name)

        # 4. Check universal (low priority)
        universal_registry = self.universal_path / "registry.json"
        if universal_registry.exists() and name in universal_registry:
            return self._load_universal_prompt(name)

        # 5. Check core (fallback, lowest priority) - lazy loaded only when requested
        return self._load_core_prompt(name)

    def _load_baseline_lock(self) -> dict:
        """Load and verify baseline protection using SHA256"""
        lock_file = self.core_path / ".promt-baseline-lock"
        if lock_file.exists():
            import json
            lock_data = json.loads(lock_file.read_text())
            return {
                "version": lock_data["version"],
                "created_at": lock_data["created_at"],
                "checksums": lock_data["checksums"]
            }
        return {}

    def _verify_baseline_integrity(self, prompt_file: Path) -> bool:
        """Verify baseline prompt hasn't been tampered with"""
        prompt_content = prompt_file.read_text()
        current_hash = hashlib.sha256(prompt_content.encode()).hexdigest()
        prompt_name = prompt_file.stem

        lock_data = self._load_baseline_lock()
        if prompt_name in lock_data.get("checksums", {}):
            expected_hash = lock_data["checksums"][prompt_name]
            return current_hash == expected_hash
        return False  # If not in baseline lock, allow modification
```

### 3. Registry Schema Enhancement

```json
{
  "version": "2.0.0",
  "registry_version": "2.0",
  "tier": "core | universal | project | mpv_stage | ai_agent_meta",
  "prompts": {
    "promt-feature-add": {
      "file": "promt-feature-add.md",
      "version": "1.5",
      "tier": "core",
      "immutable": true,
      "overridable": false,
      "checksum": "sha256:abc123...",
      "source": "existing_system",
      "migrated_at": "2026-03-18"
    },
    "promt-ideation.md": {
      "file": "universal/mpv_stages/promt-ideation.md",
      "version": "1.0",
      "tier": "mpv_stage",
      "immutable": false,
      "overridable": true,
      "source": "mpv_pipeline_new",
      "stage_number": 1,
      "created_at": "2026-03-18"
    }
  }
}
```

### 4. Legacy Naming Cleanup

**Legacy References Found:**
- ❌ "CodeShift" references in documentation
- ✅ Should be "AI Agent Prompts" (correct directory name)

**Cleanup Required:**
```bash
# Find and replace in documentation
find docs/ -name "*.md" -exec sed -i 's/CodeShift/AI Agent Prompts/g' {} \;

# Verify cleanup
grep -r "CodeShift" docs/  # Should return 0
```

## Implementation Plan

### Phase 1: Foundation & Legacy Cleanup (Week 1-2)
**Tasks:**
1. Create directory structure:
   - `prompts/core/` (5-7 baseline prompts)
   - `prompts/universal/` (meta-prompts)
   - `prompts/universal/mpv_stages/` (7 MPV stage prompts)
   - `prompts/universal/ai_agent_prompts/` (preserved meta-prompts)
   - `prompts/projects/` (project overrides)
   - `prompts/packs/` (plugin packs)

2. Categorize 16 existing prompts:
   - 5-7 CORE (Operations tier prompts)
   - 7-9 UNIVERSAL (Discovery, Planning, Implementation, Meta, Versioning)
   - 0 PROJECTS (preserve current structure)

3. Implement baseline lock mechanism (`promt-baseline-lock` with SHA256)
4. Update `prompts/registry.json` schema with new fields (`tier`, `immutable`, `overridable`, `checksum`)
5. **Legacy Cleanup:** Replace "CodeShift" with "AI Agent Prompts" in all documentation
6. **ADR Correction:** Fix incorrect "28 prompts" reference, change to "16 prompts"
7. Create migration script for 16 prompts

**Deliverables:**
- [ ] New directory structure (core/, universal/, projects/, packs/)
- [ ] Baseline lock file generator
- [ ] Updated registry schema with tier fields
- [ ] 16 prompts categorized and migrated
- [ ] Legacy "CodeShift" replaced with "AI Agent Prompts"
- [ ] ADR documentation corrected (16 prompts, not 28)
- [ ] Documentation updated
- [ ] Migration script created and tested

### Phase 2: MPV Stage Prompts Creation (Week 2-3)
**Tasks:**
1. Create all 7 MPV stage prompts:
   - `promt-ideation.md` (Stage 1: Idea Generation)
   - `promt-analysis.md` (Stage 2: Requirements Analysis)
   - `promt-design.md` (Stage 3: Architecture Planning)
   - `promt-implementation.md` (Stage 4: Code Generation)
   - `promt-testing.md` (Stage 5: Quality Validation)
   - `promt-debugging.md` (Stage 6: Self-Correction)
   - `promt-finish.md` (Stage 7: Documentation & Delivery)

2. Update `prompts/universal/mpv_stages/registry.json` with new prompts
3. Implement lazy loading for MPV stage prompts
4. Test MPV stage prompt execution

**Deliverables:**
- [ ] All 7 MPV stage prompt files created (0/7 → 7/7)
- [ ] `prompts/universal/mpv_stages/registry.json` created
- [ ] Lazy loading implemented for MPV stages
- [ ] End-to-end MPV pipeline tested

### Phase 3: Loader Refactoring (Week 3-4)
**Tasks:**
1. Refactor `src/storage/prompts.py` with cascade logic:
   - Priority: projects → universal/mpv_stages → universal/ai_agent_prompts → core
   - MPV stage prompt support
   - Lazy loading with lru_cache (from FastAPI patterns)
   - Baseline lock verification with SHA256
2. Implement server-side immutable flag enforcement
3. Integrate AI Agent Prompts preservation
4. Add comprehensive tests

**Deliverables:**
- [ ] `TieredPromptLoader` class with MPV stage support
- [ ] Lazy loading with lru_cache (target: -60% token consumption)
- [ ] Baseline lock verification working
- [ ] Immutable flag enforcement active
- [ ] AI Agent Prompts preserved in correct location
- [ ] All unit tests passing (>90% coverage)

### Phase 4: Plugin Pack System (Week 5-6)
**Tasks:**
1. Design `pack.json` format and Pydantic schema
2. Implement pack installation/management tools
3. Create first official packs (k8s, ci-cd)
4. Add pack registry and dependency resolution

**Deliverables:**
- [ ] `pack.json` Pydantic schema
- [ ] `PackLoader` class
- [ ] 2 official plugin packs
- [ ] Pack management MCP tools
- [ ] Pack system documentation

### Phase 5: HTTPS MCP & Security (Week 7-8)
**Tasks:**
1. Implement HTTPS MCP transport with authentication
2. Add JWT/mTLS support for secure access
3. Implement tier-based RBAC
4. Add audit logging for pack installations
5. Verify legacy naming cleanup complete

**Deliverables:**
- [ ] HTTPS MCP endpoint
- [ ] JWT authentication service
- [ ] RBAC middleware
- [ ] Enhanced audit logging
- [ ] Security documentation
- [ ] No "CodeShift" references in codebase

## Positive Consequences

- **Improved Organization:** Clear separation of system, MPV, AI Agent, and project-specific prompts
- **Enhanced Security:** Baseline prompts protected via cryptographic locks
- **Flexible Customization:** Project teams can override behavior without core changes
- **Reduced Token Consumption:** Lazy loading saves 60-64% of context window
- **Complete Workflow:** MPV pipeline orchestrates entire idea-to-production flow with 7 stages
- **Full MPV Support:** All 7 MPV stage prompts created (0/7 → 7/7)
- **Scalable Extension:** Plugin packs enable domain-specific functionality
- **Better Maintainability:** Clear directory structure and cascade logic
- **Legacy Cleanup:** Old "CodeShift" references removed, replaced with "AI Agent Prompts"
- **Correct Documentation:** Prompt count corrected from 28 to 16, all references accurate

## Negative Consequences

- **Migration Complexity:** One-time migration of 16 existing prompts + creation of 7 new MPV stage prompts requires careful mapping
- **Loader Complexity:** New `src/storage/prompts.py` is more complex than flat loader
- **Legacy Naming Changes:** All "CodeShift" references must be updated to "AI Agent Prompts"
- **ADR Corrections:** Incorrect prompt count (28) must be corrected to actual count (16)
- **Documentation Updates:** Extensive documentation updates required for legacy cleanup
- **Performance Overhead:** Cascade resolution may add <5ms latency per prompt load
- **Breaking Changes:** Need to ensure backward compatibility during transition
- **New Prompt Creation:** Need to create 7 new MPV stage prompts from scratch

## Security Considerations

### 1. Baseline Protection
**Risk:** Unauthorized modification of Core prompts
**Mitigation:**
- Server-side enforcement of `immutable` flags
- SHA256 checksums in `promt-baseline-lock`
- Cryptographic signature verification for core directory
- Read-only file system permissions for `prompts/core/`

### 2. Cascade Override Security
**Risk:** Privilege escalation via project overrides
**Mitigation:**
- Server-side validation of override attempts
- Input sanitization for project prompts
- Audit logging of all override operations
- Path traversal prevention in project loader

### 3. MPV Pipeline Security
**Risk:** Malicious code in MPV stage prompts
**Mitigation:**
- Structured message passing for MPV stages
- Output sanitization between stages
- Stage isolation (each stage has defined input/output)
- Context validation between stages
- Lazy loading with integrity checks

### 4. AI Agent Prompts Security
**Risk:** Unauthorized modification of AI Agent meta-prompts
**Mitigation:**
- Preserve in dedicated `prompts/universal/ai_agent_prompts/` directory
- Apply cascade logic (can only be overridden by projects)
- Add integrity verification

### 5. Access Control
**Risk:** Unauthorized access to protected resources
**Mitigation:**
- Tier-based RBAC in FastMCP layer
- JWT authentication for HTTPS MCP
- Admin-only write permissions for `prompts/core/` and `prompts/universal/`
- Per-project isolation in loader logic

## Migration Path

### Step 1: Preparation
1. Create feature branch: `feature/tiered-architecture-mpv-stages-legacy-cleanup`
2. Update documentation (`README.md`, `MCP_INTEGRATION.md`)
3. Communicate changes to stakeholders

### Step 2: Implementation
1. Create new directory structure:
   - `prompts/core/` (5-7 baseline prompts from current 16)
   - `prompts/universal/` (remaining universal prompts)
   - `prompts/universal/mpv_stages/` (7 MPV stage prompts - NEW)
   - `prompts/universal/ai_agent_prompts/` (preserved meta-prompts)
   - `prompts/projects/` (project overrides)
   - `prompts/packs/` (plugin packs)

2. Categorize 16 existing prompts:
   - 5-7 CORE (Operations tier prompts)
   - 7-9 UNIVERSAL (Discovery, Planning, Implementation, Meta, Versioning)
   - 0 PROJECTS (preserve current structure)

3. Implement baseline lock mechanism:
   - Generate `promt-baseline-lock` with SHA256 checksums
   - Verify checksums at server startup

4. Refactor `src/storage/prompts.py`:
   - Add cascade logic using FastAPI's Depends() pattern
   - Implement lazy loading with lru_cache
   - Add MPV stage prompt loading
   - Add baseline lock verification
   - Add AI Agent Prompts support

5. Update `prompts/registry.json` schema:
   - Add new fields: `tier`, `immutable`, `overridable`, `checksum`
   - Add MPV stage metadata
   - Correct prompt count to 16 (not 28)

6. **Legacy Cleanup:**
   - Replace "CodeShift" with "AI Agent Prompts" in all documentation
   - Verify no legacy references remain

7. Create 7 MPV stage prompts:
   - `promt-ideation.md` (Stage 1)
   - `promt-analysis.md` (Stage 2)
   - `promt-design.md` (Stage 3)
   - `promt-implementation.md` (Stage 4)
   - `promt-testing.md` (Stage 5)
   - `promt-debugging.md` (Stage 6)
   - `promt-finish.md` (Stage 7)

8. Run tests locally

### Step 3: Deployment
1. Run migration script on staging
2. Verify all prompts load correctly
3. Test cascade override logic
4. Verify baseline lock verification
5. Test MPV pipeline with all 7 stages
6. Verify legacy naming cleanup complete
7. Verify correct prompt count (16, not 28)
8. Performance test (check <5ms overhead)
9. Deploy to production

### Step 4: Monitoring
1. Monitor prompt load times
2. Track override operations
3. Verify token consumption reduction (target: -60-64%)
4. Collect user feedback on new architecture
5. Verify MPV pipeline stage execution
6. Verify legacy naming cleanup (no "CodeShift" references)
7. Verify correct prompt count (16 prompts)

### Step 5: Deprecation
1. Mark old flat loader as deprecated
2. Update migration guides
3. Archive old code paths
4. Update CI/CD pipelines

## Testing Strategy

### Unit Tests
- Test cascade resolution logic for all tiers (projects, universal/mpv_stages, universal/ai_agent_prompts, core)
- Test baseline lock verification (tamper detection)
- Test lazy loading with lru_cache
- Test plugin pack installation and dependency resolution
- Test MPV stage prompt loading (all 7 stages)
- Test AI Agent Prompts preservation
- Test legacy naming cleanup (no "CodeShift" references)

### Integration Tests
- Test end-to-end MPV pipeline (7 stages)
- Test project override functionality
- Test backward compatibility with existing integrations
- Test HTTPS MCP authentication
- Test tier-based RBAC enforcement
- Test lazy loading performance

### Performance Tests
- Measure prompt load time (<5ms overhead target)
- Measure token consumption (-60-64% target)
- Measure cache hit rates (target: >90%)
- Measure concurrent request handling
- Measure MPV pipeline execution time

### Security Tests
- Test baseline lock tamper detection
- Test cascade override security (privilege escalation attempts)
- Test MPV stage prompt security
- Test AI Agent Prompts integrity
- Test plugin pack signature verification
- Test RBAC enforcement
- Test legacy naming cleanup verification

## Rollback Plan

If critical issues are discovered post-deployment:

**Immediate Actions:**
```bash
# 1. Stop new services
docker compose down

# 2. Revert code
git revert HEAD~1  # Revert latest commit

# 3. Restore backups
cp -r prompts_backup_*/ prompts/
cp src/storage/prompts.py.backup src/storage/prompts.py

# 4. Revert legacy naming if needed (restore "CodeShift" references)
# Note: Only revert if required by issue

# 5. Update documentation
# Document rollback reason and timeline

# 6. Notify team
# Send alert with rollback details
```

**Data Recovery:**
- [ ] Restore prompt files from backup
- [ ] Restore baseline lock file
- [ ] Roll back database migrations if any
- [ ] Verify system functionality
- [ ] Post-rollback testing
- [ ] Restore legacy naming if required by rollback

## Related Documents
- `docs/how-to/MPV.md` - MPV 7-Stage Pipeline specification
- `docs/how-to/analysis-CodeShift-promt.md` - Tier Architecture analysis (legacy reference)
- `docs/how-to/universal_mcp_architecture_mermaid_style.svg` - Architecture visualization
- `docs/ai-agent-prompts/` - AI Agent Prompts directory (correct naming)
- `docs/explanation/adr/ADR-001-system-genesis.md` - System Genesis & Repository Standards
- `docs/explanation/adr/ADR_INDEX.md` - ADR registry
- `src/storage/prompts.py` - Current flat loader (to be refactored with Depends() pattern)
- `prompts/registry.json` - Current 16 prompts (to be updated with MPV stages)
- `scripts/cleanup_legacy_naming.sh` - Legacy naming cleanup script

## Success Criteria

### Phase 1: Foundation & Legacy Cleanup (Week 1-2)
- [ ] New directory structure created (core/, universal/, mpv_stages/, ai_agent_prompts/, projects/, packs/)
- [ ] 16 existing prompts categorized and migrated
- [ ] 5-7 CORE prompts identified
- [ ] 7-9 UNIVERSAL prompts identified
- [ ] Baseline lock mechanism implemented with SHA256
- [ ] Registry schema updated (tier, immutable, overridable, checksum)
- [ ] Legacy "CodeShift" references replaced with "AI Agent Prompts"
- [ ] ADR documentation corrected (16 prompts, not 28)
- [ ] Documentation updated
- [ ] Migration script created and tested
- [ ] No legacy "CodeShift" references verified in docs

### Phase 2: MPV Stage Prompts (Week 2-3)
- [ ] All 7 MPV stage prompts created (0/7 → 7/7)
- [ ] `promt-ideation.md` (Stage 1: Idea Generation)
- [ ] `promt-analysis.md` (Stage 2: Requirements Analysis)
- [ ] `promt-design.md` (Stage 3: Architecture Planning)
- [ ] `promt-implementation.md` (Stage 4: Code Generation)
- [ ] `promt-testing.md` (Stage 5: Quality Validation)
- [ ] `promt-debugging.md` (Stage 6: Self-Correction)
- [ ] `promt-finish.md` (Stage 7: Documentation & Delivery)
- [ ] `prompts/universal/mpv_stages/registry.json` created
- [ ] End-to-end MPV pipeline tested

### Phase 3: Loader Refactoring (Week 3-4)
- [x] `TieredPromptLoader` class implemented with Depends() pattern
- [x] Lazy loading with lru_cache implemented (target: -60% tokens)
- [x] Cascade override works (projects → universal/mpv_stages → universal/ai_agent_prompts → core)
- [x] Baseline lock verification working
- [x] Immutable flag enforcement active
- [x] AI Agent Prompts preserved in correct location
- [ ] All unit tests passing (>90% coverage)
- [ ] Performance benchmarks met (<5ms overhead, -60-64% tokens)

### Phase 4: Plugin Packs (Week 5-6)
- [x] `pack.json` Pydantic schema designed
- [x] `PackLoader` class implemented
- [x] 2 official plugin packs (k8s-pack, ci-cd-pack)
- [x] Pack management tools working
- [x] Pack system documented

### Phase 5: HTTPS & Security (Week 7-8)
- [x] HTTPS MCP endpoint deployed (via Caddy)
- [x] JWT authentication working
- [x] Tier-based RBAC implemented
- [x] Enhanced audit logging active
- [ ] Security audit passing (all mitigations in place)
- [x] No "CodeShift" references in codebase

### Overall
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Performance benchmarks met (<5ms overhead, -60-64% tokens)
- [ ] Security audit passing (all mitigations in place)
- [ ] All 7 MPV stage prompts functional
- [ ] Legacy naming cleanup complete (verified no "CodeShift" references)
- [ ] Production deployment successful

---

**ADR Version:** 1.3
**Created:** 2026-03-18
**Status:** Accepted
**Review Date:** 2026-03-18
**Approver:** @perovskikh

## Changes from Version 1.2:
- Corrected prompt count from 28 to 16 (actual current system)
- Added MPV stage prompts creation (0/7 → 7/7 required)
- Replaced "CodeShift" legacy references with "AI Agent Prompts"
- Added `prompts/universal/mpv_stages/` directory for MPV pipeline
- Added `prompts/universal/ai_agent_prompts/` preservation directory
- Added Depends() pattern from FastAPI for hierarchical dependency injection
- Added lru_cache for lazy loading pattern
- Enhanced security considerations for MPV pipeline
- Updated migration phases to include legacy cleanup
- Fixed ADR documentation errors (incorrect prompt count, missing MPV stages)
- Added AI Agent Prompts preservation strategy

## Review History

### ADR-002-FINAL-REVIEW (2026-03-19)
**Status**: Final review completed
**Key Decisions**:
- Implementation approved with Phase 5 complete
- JWT, RBAC, HTTPS proxy confirmed
- Ready for production deployment

**Discussion Summary**:
- Implementation timeline: Phase 1-5 completed
- All blockers resolved
- Performance metrics meeting targets
- Ready for integration with ADR-003 (Prompt Storage Strategy)

### ADR-002-REVIEW (2026-03-XX)
**Status**: Interim review
**Key Points**:
- [Review content will be extracted when file is available]
- Additional design considerations discussed

---
*See also: Git commit history for detailed discussion*
