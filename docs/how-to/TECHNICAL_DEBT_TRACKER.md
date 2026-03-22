# Technical Debt Tracker

**Last Updated**: 2026-03-20
**Source**: docs/BOTTLENECKS_ANALYSIS.md
**Total Items**: 14 (11 medium, 3 low)

---

## 📊 Executive Summary

| Priority | Count | Percentage |
|----------|--------|------------|
| 🔴 **Critical** | 0 | 0% |
| 🟡 **High** | 0 | 0% |
| 🟢 **Medium** | 11 | 79% |
| 🟣 **Low** | 3 | 21% |
| **Total** | **14** | **100%** |

**Status**: 🟢 **MOSTLY MEDIUM PRIORITY DEBT**

---

## 🔴 Critical Priority

*No critical technical debt found*

---

## 🟡 High Priority

*No high priority technical debt found*

---

## 🟢 Medium Priority (11 items)

### Performance (2 items)

#### 1. Sequential Chain Execution
- **File**: `src/services/executor.py:125-157`
- **Line**: 125-157
- **Issue**: Chains execute sequentially (step1 → step2 → step3)
- **Impact**: Cumulative latency (5 steps × 2s = 10s)
- **Solution**: Implement parallel execution for independent steps
- **Estimated Effort**: 8 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 1.4
- **Status**: 📋 TODO

#### 2. In-Memory Audit Logs
- **File**: `src/api/server.py:152-196`
- **Line**: 152-196
- **Issue**: Stores 10,000 log entries in memory array
- **Impact**: GC pressure, memory bloat (~10MB+)
- **Solution**: Use circular buffer or rotate to disk
- **Estimated Effort**: 6 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 1.5
- **Status**: 📋 TODO

---

### Architecture (3 items)

#### 3. Mixed Concerns
- **File**: `src/api/server.py` (entire file)
- **Line**: 1-905
- **Issue**: Single file contains API keys, audit logging, storage, business logic
- **Impact**: Hard to test, maintain, and extend
- **Solution**: Separate into modules (api/, auth/, audit/, storage/)
- **Estimated Effort**: 24 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 2.1
- **Status**: 📋 TODO

#### 4. Tight Coupling - Hardcoded INTENT_MAP
- **File**: `src/api/server.py:347-405`
- **Line**: 347-405
- **Issue**: INTENT_MAP hardcoded with 30+ keyword-prompt pairs
- **Impact**: Requires redeploy to add/modify prompts, no hot-reload
- **Solution**: Externalize to JSON with hot-reload
- **Estimated Effort**: 8 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 2.2
- **Status**: 📋 TODO

#### 5. Complex Fallback Logic
- **File**: `src/api/server.py:237-289`
- **Line**: 237-289
- **Issue**: `load_prompt()` has 6 different fallback strategies
- **Impact**: Code complexity, maintenance nightmare
- **Solution**: Simplify to single resolution path
- **Estimated Effort**: 4 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 2.3
- **Status**: 📋 TODO

---

### Integration (3 items)

#### 6. Fragile Prompt Parsing
- **File**: `src/services/executor.py:64-123`
- **Line**: 64-123
- **Issue**: Complex manual parsing of markdown sections with multiple edge cases
- **Impact**: Fails on edge cases, hard to debug
- **Solution**: Use proper markdown parser (markdown-it, markdown2)
- **Estimated Effort**: 8 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 3.1
- **Status**: 📋 TODO

#### 7. No Structured Output Enforcement
- **File**: `src/services/llm_client.py:218-360`
- **Line**: 218-360
- **Issue**: LLM responses returned as raw strings, no JSON mode
- **Impact**: Fragile downstream parsing, hallucination errors
- **Solution**: Enable JSON mode/function calling where supported
- **Estimated Effort**: 12 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 3.2
- **Status**: 📋 TODO

#### 8. Manual Provider Format Handling
- **File**: `src/services/llm_client.py:142-217`
- **Line**: 142-217
- **Issue**: 7 different provider formats handled manually
- **Impact**: Maintenance burden, error-prone
- **Solution**: Unified adapter pattern with provider-specific implementations
- **Estimated Effort**: 16 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 3.3
- **Status**: 📋 TODO

---

### Security (1 item)

#### 9. Weak Rate Limiting
- **File**: `src/api/server.py:108-128`
- **Line**: 108-128
- **Issue**: Simple in-memory tracking, no distributed protection
- **Impact**: Susceptible to distributed DoS attacks
- **Solution**: Use Redis for distributed rate limiting
- **Estimated Effort**: 8 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 4.2
- **Status**: 📋 TODO

---

### Configuration (2 items)

#### 10. Duplicate ADR Numbers
- **File**: `docs/explanation/adr/`
- **Files**:
  - ADR-002-FINAL-REVIEW.md
  - ADR-002-REVIEW.md
  - ADR-002-tiered-prompt-architecture-mpv-integration.md
- **Issue**: ADR-002 appears in 3 files
- **Impact**: Documentation confusion, ADR numbering inconsistency
- **Solution**: Rename review files or move to reviews/ subdirectory
- **Estimated Effort**: 4 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 5.4
- **Status**: 📋 TODO

#### 11. Duplicate Topic Slugs
- **File**: `docs/explanation/adr/`
- **Issue**: Topic slug '002' appears in multiple files
- **Impact**: ADR identification conflicts, pre-commit hook detection
- **Solution**: Use proper slug format (e.g., 'tiered-prompt-architecture')
- **Estimated Effort**: 2 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 5.5
- **Status**: 📋 TODO

---

## 🟣 Low Priority (3 items)

#### 12. Deprecate prompts.py v1
- **File**: `src/storage/prompts.py`
- **Line**: 1-96
- **Issue**: Legacy storage implementation, no caching
- **Impact**: Confusion, duplicate code, performance issues
- **Solution**: Deprecate with @DeprecationWarning, migrate all code to v2
- **Estimated Effort**: 4 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 13
- **Status**: 📋 TODO

#### 13. Implement Parallel Chain Execution
- **File**: `src/services/executor.py:125-157`
- **Line**: 125-157
- **Issue**: Sequential execution of chains
- **Impact**: Cumulative latency, slow performance
- **Solution**: Parallelize independent steps using asyncio.gather()
- **Estimated Effort**: 8 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 14
- **Status**: 📋 TODO

#### 14. Optimize Audit Logging
- **File**: `src/api/server.py:152-196`
- **Line**: 152-196
- **Issue**: In-memory audit logs with manual management
- **Impact**: Performance issues, potential memory leaks
- **Solution**: Circular buffer, automatic rotation, metrics collection
- **Estimated Effort**: 6 hours
- **Reference**: BOTTLENECKS_ANALYSIS.md section 15
- **Status**: 📋 TODO

---

## 📈 Total Effort Estimation

| Priority | Items | Total Hours | Days |
|----------|--------|-------------|------|
| **Critical** | 0 | 0 hours | 0 days |
| **High** | 0 | 0 hours | 0 days |
| **Medium** | 11 | **112 hours** | **14 days** |
| **Low** | 3 | **18 hours** | **2.25 days** |
| **Total** | **14** | **130 hours** | **16.25 days** |

**Estimated Completion Time**: ~3-4 weeks with 1 developer

---

## 🎯 Prioritization Recommendations

### Week 1 (Immediate - High Impact)
1. **Security: Weak Rate Limiting** (8 hours) - Critical vulnerability
2. **Integration: Enable JSON Mode** (12 hours) - High impact on all requests
3. **Integration: Fragile Prompt Parsing** (8 hours) - Affects all prompt operations

### Week 2-3 (Architecture - Long-term Impact)
4. **Architecture: Mixed Concerns** (24 hours) - Foundation for all future work
5. **Architecture: Hardcoded INTENT_MAP** (8 hours) - Hot-reload capability
6. **Architecture: Complex Fallback Logic** (4 hours) - Code simplification

### Week 4 (Performance - Optimization)
7. **Performance: Sequential Chain Execution** (8 hours) - Speed improvement
8. **Performance: In-Memory Audit Logs** (6 hours) - Memory optimization

### Week 5-6 (Configuration - Cleanup)
9. **Configuration: Duplicate ADR Numbers** (4 hours) - Documentation cleanup
10. **Configuration: Duplicate Topic Slugs** (2 hours) - Documentation cleanup

### Month 2-3 (Technical Debt - Retirement)
11. **Deprecate prompts.py v1** (4 hours) - Code cleanup
12. **Implement Parallel Chain Execution** (8 hours) - Performance optimization
13. **Optimize Audit Logging** (6 hours) - Long-term improvement
14. **Manual Provider Format Handling** (16 hours) - Major refactoring

---

## 🔄 Tracking Status

| Item | Status | Assigned To | Target Date |
|-------|--------|------------|-------------|
| Sequential Chain Execution | 📋 TODO | - | - |
| In-Memory Audit Logs | 📋 TODO | - | - |
| Mixed Concerns | 📋 TODO | - | - |
| Hardcoded INTENT_MAP | 📋 TODO | - | - |
| Complex Fallback Logic | 📋 TODO | - | - |
| Fragile Prompt Parsing | 📋 TODO | - | - |
| No Structured Output | 📋 TODO | - | - |
| Weak Rate Limiting | 📋 TODO | - | - |
| Duplicate ADR Numbers | 📋 TODO | - | - |
| Duplicate Topic Slugs | 📋 TODO | - | - |
| Deprecate prompts.py v1 | 📋 TODO | - | - |
| Implement Parallel Chain Execution | 📋 TODO | - | - |
| Optimize Audit Logging | 📋 TODO | - | - |
| Manual Provider Format Handling | 📋 TODO | - | - |

---

## 🔍 How to Find Technical Debt

### Automatic Detection (via AI Auto-Fix)

The `promt-automated-code-fix.md` prompt automatically identifies technical debt as part of bottleneck analysis:

```bash
# Run analysis via p9i
mcp__ai-prompt-system__ai_prompts request="проанализируй bottleneck-ы и найди технические долги" context='{
  "reference_doc": "docs/BOTTLENECKS_ANALYSIS.md"
}'

# The AI will automatically categorize items by priority
# Critical → Auto-apply
# High/Medium/Low → Suggest fixes in PR comments
```

### Manual Tracking

When developers identify new technical debt, update this tracker:

```markdown
#### New Item
- **File**: `path/to/file.py`
- **Line**: XXX
- **Category**: [Performance|Architecture|Integration|Security|Configuration]
- **Priority**: [Critical|High|Medium|Low]
- **Issue**: Description
- **Solution**: Proposed solution
- **Estimated Effort**: X hours
- **Status**: 📋 TODO | 🔄 IN_PROGRESS | ✅ DONE
- **Reference**: BOTTLENECKS_ANALYSIS.md section X.Y
- **Assigned To**: @developer
- **Target Date**: YYYY-MM-DD
```

### Update Status

When work is completed, update the status:

- 📋 TODO → Not started
- 🔄 IN_PROGRESS → Currently working on
- ⏸️ BLOCKED → Waiting on dependencies
- ✅ DONE → Completed
- 🚫 CANCELLED → No longer relevant
- 🔄 REOPENED → Reopened after completion

---

## 📊 Metrics

### Current Debt Burden

- **Total Items**: 14
- **Estimated Hours**: 130 hours
- **Estimated Cost**: $X,XXX (based on hourly rate)
- **Age**: 0 days (newly identified)
- **Velocity**: 0 items/week (not started)

### Debt Categories

| Category | Items | Hours | Percentage |
|----------|--------|--------|------------|
| **Performance** | 2 | 14 | 15% |
| **Architecture** | 3 | 36 | 28% |
| **Integration** | 3 | 36 | 28% |
| **Security** | 1 | 8 | 7% |
| **Configuration** | 2 | 6 | 15% |
| **Total** | **11** | **112** | **100%** |

---

## 🎯 Success Metrics

When technical debt is paid down, these metrics should improve:

| Metric | Current | Target | Success Criteria |
|---------|----------|--------|-----------------|
| System Latency (prompt load) | 50-100ms | <10ms | ✅ |
| Code Quality (SOLID compliance) | 6.0/10 | 9.0/10 | ✅ |
| Security Score | 5.0/10 | 9.0/10 | ✅ |
| Test Coverage | <20% | >80% | ✅ |
| Maintainability Index | Medium | High | ✅ |

---

## 📚 Related Documentation

- **[Bottleneck Analysis](BOTTLENECKS_ANALYSIS.md)** - Source of technical debt items
- **[Auto-Fix Implementation](AUTO_FIX_IMPLEMENTATION.md)** - AI-powered automatic fixing system
- **[System Testing Report](SYSTEM_TESTING_REPORT.md)** - Validation of AI auto-fix system
- **ADR-003: Prompt Storage Strategy](docs/explanation/adr/ADR-003-prompt-storage-strategy.md)** - Prompt storage decisions

---

**Last Updated**: 2026-03-20
**Next Review**: 2026-04-20
**Maintainer**: Development Team
**Status**: 🟢 **READY FOR TRACKING**