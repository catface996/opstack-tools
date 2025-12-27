# Tasks: Operations Tools Collection

**Input**: Design documents from `/specs/002-ops-tools/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec - test tasks omitted. Add test tasks if TDD approach is desired.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## User Stories Mapping

| Story | Title | Priority | Tools Count |
|-------|-------|----------|-------------|
| US1 | K8S Pod Operations | P1 | 6 tools |
| US2 | Database Query Operations | P1 | 3 tools + validator |
| US3 | Java Application Monitoring | P2 | 4 tools |
| US4 | AWS Resource Management | P2 | 6 tools |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependencies

- [x] T001 Add kubernetes dependency to pyproject.toml
- [x] T002 [P] Add psycopg2-binary dependency to pyproject.toml
- [x] T003 [P] Add mysql-connector-python dependency to pyproject.toml
- [x] T004 [P] Add boto3 dependency to pyproject.toml
- [x] T005 Create tools package directory structure in src/aiops_tools/tools/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Tool loader service and category setup that MUST be complete before tool implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create tool loader service in src/aiops_tools/services/tool_loader.py
- [x] T007 [P] Create k8s tools package in src/aiops_tools/tools/k8s/__init__.py
- [x] T008 [P] Create database tools package in src/aiops_tools/tools/database/__init__.py
- [x] T009 [P] Create java tools package in src/aiops_tools/tools/java/__init__.py
- [x] T010 [P] Create aws tools package in src/aiops_tools/tools/aws/__init__.py
- [x] T011 Create seed script for tool categories in scripts/seed_categories.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - K8S Pod Operations (Priority: P1) 🎯 MVP

**Goal**: Enable LLM agents to execute Kubernetes operations (list pods, check status, view logs, restart deployments)

**Independent Test**: Deploy to a K8S cluster and execute pod list/describe/logs commands via the /llm/tools/invoke endpoint

### Implementation for User Story 1

- [x] T012 [P] [US1] Implement k8s_list_pods tool in src/aiops_tools/tools/k8s/list_pods.py
- [x] T013 [P] [US1] Implement k8s_get_logs tool in src/aiops_tools/tools/k8s/get_logs.py
- [x] T014 [P] [US1] Implement k8s_describe_pod tool in src/aiops_tools/tools/k8s/describe_pod.py
- [x] T015 [P] [US1] Implement k8s_restart_deployment tool in src/aiops_tools/tools/k8s/restart_deployment.py
- [x] T016 [P] [US1] Implement k8s_list_namespaces tool in src/aiops_tools/tools/k8s/list_namespaces.py
- [x] T017 [P] [US1] Implement k8s_get_deployment_status tool in src/aiops_tools/tools/k8s/get_deployment_status.py
- [x] T018 [US1] Create seed script for K8S tools in scripts/seed_k8s_tools.py
- [ ] T019 [US1] Verify K8S tools via curl commands per quickstart.md

**Checkpoint**: K8S tools fully functional - can list pods, get logs, describe pods, restart deployments

---

## Phase 4: User Story 2 - Database Query Operations (Priority: P1)

**Goal**: Enable LLM agents to execute read-only database queries and retrieve schema information

**Independent Test**: Connect to a database and execute SELECT queries via the /llm/tools/invoke endpoint

### Implementation for User Story 2

- [x] T020 [P] [US2] Implement SQL query validator in src/aiops_tools/tools/database/query_validator.py
- [x] T021 [P] [US2] Implement db_execute_query tool in src/aiops_tools/tools/database/execute_query.py
- [x] T022 [P] [US2] Implement db_list_tables tool in src/aiops_tools/tools/database/list_tables.py
- [x] T023 [P] [US2] Implement db_describe_table tool in src/aiops_tools/tools/database/describe_table.py
- [x] T024 [US2] Create seed script for Database tools in scripts/seed_db_tools.py
- [ ] T025 [US2] Verify Database tools via curl commands per quickstart.md

**Checkpoint**: Database tools fully functional - can execute queries, list tables, describe schema

---

## Phase 5: User Story 3 - Java Application Monitoring (Priority: P2)

**Goal**: Enable LLM agents to retrieve JVM metrics and thread dumps from running Java applications

**Independent Test**: Connect to a running Java application's JMX/Jolokia endpoint and retrieve heap memory usage

### Implementation for User Story 3

- [x] T026 [P] [US3] Implement java_get_heap_usage tool in src/aiops_tools/tools/java/get_heap_usage.py
- [x] T027 [P] [US3] Implement java_get_thread_dump tool in src/aiops_tools/tools/java/get_thread_dump.py
- [x] T028 [P] [US3] Implement java_get_gc_stats tool in src/aiops_tools/tools/java/get_gc_stats.py
- [x] T029 [P] [US3] Implement java_list_mbeans tool in src/aiops_tools/tools/java/list_mbeans.py
- [x] T030 [US3] Create seed script for Java tools in scripts/seed_java_tools.py
- [ ] T031 [US3] Verify Java tools via curl commands per quickstart.md

**Checkpoint**: Java tools fully functional - can get heap usage, thread dumps, GC stats

---

## Phase 6: User Story 4 - AWS Resource Management (Priority: P2)

**Goal**: Enable LLM agents to query AWS resources (EC2, S3, RDS, CloudWatch)

**Independent Test**: Configure AWS credentials and list EC2 instances via the /llm/tools/invoke endpoint

### Implementation for User Story 4

- [x] T032 [P] [US4] Implement aws_list_ec2_instances tool in src/aiops_tools/tools/aws/list_ec2_instances.py
- [x] T033 [P] [US4] Implement aws_describe_instance tool in src/aiops_tools/tools/aws/describe_instance.py
- [x] T034 [P] [US4] Implement aws_list_s3_buckets tool in src/aiops_tools/tools/aws/list_s3_buckets.py
- [x] T035 [P] [US4] Implement aws_list_s3_objects tool in src/aiops_tools/tools/aws/list_s3_objects.py
- [x] T036 [P] [US4] Implement aws_describe_rds tool in src/aiops_tools/tools/aws/describe_rds.py
- [x] T037 [P] [US4] Implement aws_get_cloudwatch_metrics tool in src/aiops_tools/tools/aws/get_cloudwatch_metrics.py
- [x] T038 [US4] Create seed script for AWS tools in scripts/seed_aws_tools.py
- [ ] T039 [US4] Verify AWS tools via curl commands per quickstart.md

**Checkpoint**: AWS tools fully functional - can list EC2, S3, RDS, get CloudWatch metrics

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Integration, documentation, and final validation

- [x] T040 Create master seed script that runs all category seeds in scripts/seed_all_tools.py
- [ ] T041 [P] Update CLAUDE.md with operations tools usage examples
- [ ] T042 [P] Add error handling examples to quickstart.md
- [ ] T043 Run full end-to-end validation of all 19 tools
- [ ] T044 Performance validation - verify all tools complete within 30 seconds

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 - can proceed in parallel
  - US3 and US4 are both P2 - can proceed in parallel after P1 stories or concurrently
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational (BLOCKS ALL)
    ↓
    ├── Phase 3: US1 (K8S) ─────┐
    │                           │
    └── Phase 4: US2 (Database) ├── Both P1, can run in parallel
                                │
    ├── Phase 5: US3 (Java) ────┤
    │                           │
    └── Phase 6: US4 (AWS) ─────┘── Both P2, can run in parallel
                                │
                                ↓
                        Phase 7: Polish
```

### Within Each User Story

1. All tool implementations marked [P] can run in parallel
2. Seed script depends on all tools being implemented
3. Verification depends on seed script

### Parallel Opportunities

**Phase 1**: T002, T003, T004 can all run in parallel (different dependencies)
**Phase 2**: T007, T008, T009, T010 can all run in parallel (different packages)
**Phase 3**: T012-T017 can all run in parallel (different tool files)
**Phase 4**: T020-T023 can all run in parallel (different tool files)
**Phase 5**: T026-T029 can all run in parallel (different tool files)
**Phase 6**: T032-T037 can all run in parallel (different tool files)
**Phase 7**: T041, T042 can run in parallel

---

## Parallel Example: User Story 1 (K8S Tools)

```bash
# Launch all K8S tool implementations in parallel:
Task: "Implement k8s_list_pods in src/aiops_tools/tools/k8s/list_pods.py"
Task: "Implement k8s_get_logs in src/aiops_tools/tools/k8s/get_logs.py"
Task: "Implement k8s_describe_pod in src/aiops_tools/tools/k8s/describe_pod.py"
Task: "Implement k8s_restart_deployment in src/aiops_tools/tools/k8s/restart_deployment.py"
Task: "Implement k8s_list_namespaces in src/aiops_tools/tools/k8s/list_namespaces.py"
Task: "Implement k8s_get_deployment_status in src/aiops_tools/tools/k8s/get_deployment_status.py"
```

---

## Parallel Example: All P1 Stories

```bash
# After Phase 2, launch both P1 stories in parallel:

# US1: K8S Tools (6 tools)
Task: "Implement all K8S tools" (T012-T017 in parallel)

# US2: Database Tools (4 files)
Task: "Implement all Database tools" (T020-T023 in parallel)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (add dependencies)
2. Complete Phase 2: Foundational (tool loader + packages)
3. Complete Phase 3: User Story 1 (K8S tools)
4. Complete Phase 4: User Story 2 (Database tools)
5. **STOP and VALIDATE**: Test K8S and Database tools independently
6. Deploy/demo if ready - **10 tools delivered**

### Full Delivery

1. Complete MVP (Phases 1-4) → 10 tools
2. Add User Story 3 (Java) → 14 tools
3. Add User Story 4 (AWS) → 19 tools
4. Complete Polish phase → Production ready

### Parallel Team Strategy

With 2 developers after Phase 2:
- Developer A: US1 (K8S) → US3 (Java)
- Developer B: US2 (Database) → US4 (AWS)

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 44 |
| Setup Tasks | 5 |
| Foundational Tasks | 6 |
| US1 (K8S) Tasks | 8 |
| US2 (Database) Tasks | 6 |
| US3 (Java) Tasks | 6 |
| US4 (AWS) Tasks | 8 |
| Polish Tasks | 5 |
| Parallel Opportunities | 26 tasks marked [P] |
| MVP Scope | US1 + US2 (10 tools, 25 tasks) |

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each tool follows the standard pattern from research.md (main function, JSON in/out)
- Each tool must return standardized error responses per research.md
- All tools use existing /api/v1/tools/create and /api/v1/llm/tools/invoke endpoints
- Seed scripts create tool records in database with correct schemas from contracts/
- Verification tasks use curl commands as documented in quickstart.md
