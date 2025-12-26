# Tasks: LLM Tool Management System

**Input**: Design documents from `/specs/001-llm-tool-management/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested - test tasks omitted (add via /speckit.checklist if needed)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `src/aiops_tools/` (existing FastAPI project)
- **Frontend**: `frontend/` (new React project)
- **Tests**: `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and database migrations

- [x] T001 Update tool_execution_timeout from 300 to 30 in src/aiops_tools/core/config.py
- [x] T002 Create Alembic migration to add script_content column to tools table in alembic/versions/
- [x] T003 Create Alembic migration to add script_content column to tool_versions table in alembic/versions/
- [ ] T004 Run database migrations to apply schema changes (manual: `alembic upgrade head`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Add script_content field to Tool model in src/aiops_tools/models/tool.py
- [x] T006 Add script_content field to ToolVersion model in src/aiops_tools/models/tool.py
- [x] T007 [P] Add script_content to ToolCreate schema in src/aiops_tools/schemas/tool.py
- [x] T008 [P] Add script_content to ToolUpdate schema in src/aiops_tools/schemas/tool.py
- [x] T009 [P] Add script_content to ToolResponse schema in src/aiops_tools/schemas/tool.py
- [x] T010 Create tool_validator.py service with validate_python_syntax() in src/aiops_tools/services/tool_validator.py
- [x] T011 Create tool_executor.py service with execute_script() using subprocess in src/aiops_tools/services/tool_executor.py
- [x] T012 Create Celery task for async script execution in src/aiops_tools/tasks/executor.py
- [x] T013 Update schemas/__init__.py to export new schemas in src/aiops_tools/schemas/__init__.py
- [x] T014 Initialize frontend React project with TypeScript and Ant Design in frontend/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Browse and Search Tools (Priority: P1) 🎯 MVP

**Goal**: Users can browse, search, and view tool details through a web interface

**Independent Test**: Access tool list page, apply search filters, click a tool to see details

### Implementation for User Story 1

- [x] T015 [P] [US1] Create ToolList page component in frontend/src/pages/ToolList.tsx
- [x] T016 [P] [US1] Create ToolCard component for list display in frontend/src/components/ToolCard.tsx
- [x] T017 [P] [US1] Create SearchBar component with keyword input in frontend/src/components/SearchBar.tsx
- [x] T018 [P] [US1] Create Pagination component in frontend/src/components/Pagination.tsx
- [x] T019 [US1] Create ToolDetail page component in frontend/src/pages/ToolDetail.tsx
- [x] T020 [US1] Create API service for tool list and detail in frontend/src/services/toolApi.ts
- [x] T021 [US1] Setup React Router with /tools and /tools/:id routes in frontend/src/App.tsx
- [x] T022 [US1] Add status badge and tag display to ToolCard in frontend/src/components/ToolCard.tsx
- [x] T023 [US1] Integrate search with debounce and URL params in frontend/src/pages/ToolList.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Create New Tool (Priority: P1)

**Goal**: Users can create new tools with name, description, parameters, and Python script through web interface

**Independent Test**: Navigate to create page, fill form, save tool, verify it appears in list

### Implementation for User Story 2

- [x] T024 [P] [US2] Create ToolForm component with form fields in frontend/src/components/ToolForm.tsx
- [x] T025 [P] [US2] Create MonacoEditor component for Python script editing in frontend/src/components/MonacoEditor.tsx
- [x] T026 [P] [US2] Create JsonSchemaEditor component for parameters in frontend/src/components/JsonSchemaEditor.tsx
- [x] T027 [US2] Create ToolCreate page using ToolForm in frontend/src/pages/ToolCreate.tsx
- [x] T028 [US2] Add createTool API method in frontend/src/services/toolApi.ts
- [x] T029 [US2] Add route /tools/new to React Router in frontend/src/App.tsx
- [x] T030 [US2] Implement form validation with error display in frontend/src/components/ToolForm.tsx
- [x] T031 [US2] Update tools.py endpoint to handle script_content on create in src/aiops_tools/api/v1/endpoints/tools.py
- [x] T032 [US2] Add Python syntax validation on tool create in src/aiops_tools/api/v1/endpoints/tools.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Query Tools for LLM (Priority: P1)

**Goal**: LLM systems can query available tools in OpenAI function calling format

**Independent Test**: Call GET /api/v1/llm/tools and verify response matches OpenAI format

### Implementation for User Story 3

- [x] T033 [P] [US3] Create LLM schemas (LLMTool, LLMToolListResponse) in src/aiops_tools/schemas/llm.py
- [x] T034 [P] [US3] Create transform_to_llm_format() helper in src/aiops_tools/schemas/llm.py
- [x] T035 [US3] Create llm.py endpoint file with router in src/aiops_tools/api/v1/endpoints/llm.py
- [x] T036 [US3] Implement GET /llm/tools endpoint (list active tools in LLM format) in src/aiops_tools/api/v1/endpoints/llm.py
- [x] T037 [US3] Implement GET /llm/tools/{tool_name} endpoint (single tool by name) in src/aiops_tools/api/v1/endpoints/llm.py
- [x] T038 [US3] Register llm router in api_router in src/aiops_tools/api/v1/router.py
- [x] T039 [US3] Update schemas/__init__.py to export LLM schemas in src/aiops_tools/schemas/__init__.py

**Checkpoint**: At this point, all P1 user stories should be independently functional

---

## Phase 6: User Story 4 - Execute Tool (Priority: P2)

**Goal**: Users and LLMs can invoke tools and receive execution results

**Independent Test**: Call POST /api/v1/llm/tools/{name}/invoke with parameters, verify result

### Implementation for User Story 4

- [x] T040 [P] [US4] Create ToolInvokeRequest and ToolInvokeResponse schemas in src/aiops_tools/schemas/llm.py
- [x] T041 [US4] Implement POST /llm/tools/{tool_name}/invoke endpoint in src/aiops_tools/api/v1/endpoints/llm.py
- [x] T042 [US4] Integrate tool_executor service with invoke endpoint in src/aiops_tools/api/v1/endpoints/llm.py
- [x] T043 [US4] Add parameter validation against input_schema before execution in src/aiops_tools/api/v1/endpoints/llm.py
- [x] T044 [US4] Implement timeout handling (30s) with proper error response in src/aiops_tools/services/tool_executor.py
- [x] T045 [US4] Create ToolExecution record on each invocation in src/aiops_tools/api/v1/endpoints/llm.py
- [x] T046 [US4] Update existing execute endpoint to use tool_executor in src/aiops_tools/api/v1/endpoints/executions.py
- [x] T047 [P] [US4] Create ToolTestPanel component for frontend testing in frontend/src/components/ToolTestPanel.tsx
- [x] T048 [US4] Add test panel to ToolDetail page in frontend/src/pages/ToolDetail.tsx

**Checkpoint**: Tool execution should work for both API and frontend

---

## Phase 7: User Story 5 - Edit and Update Tool (Priority: P2)

**Goal**: Users can edit existing tools with version auto-increment

**Independent Test**: Edit a tool's description or script, verify version increments and changes persist

### Implementation for User Story 5

- [x] T049 [US5] Create ToolEdit page reusing ToolForm in frontend/src/pages/ToolEdit.tsx
- [x] T050 [US5] Add updateTool API method in frontend/src/services/toolApi.ts
- [x] T051 [US5] Add route /tools/:id/edit to React Router in frontend/src/App.tsx
- [x] T052 [US5] Implement version auto-increment on tool update in src/aiops_tools/api/v1/endpoints/tools.py
- [x] T053 [US5] Create ToolVersion snapshot on each update in src/aiops_tools/api/v1/endpoints/tools.py
- [x] T054 [US5] Add Edit button to ToolDetail page in frontend/src/pages/ToolDetail.tsx
- [x] T055 [US5] Add success notification after save in frontend/src/pages/ToolEdit.tsx

**Checkpoint**: Tool editing with version history should work

---

## Phase 8: User Story 6 - Delete Tool (Priority: P3)

**Goal**: Users can delete tools with confirmation dialog

**Independent Test**: Delete a tool, confirm via dialog, verify it no longer appears in list

### Implementation for User Story 6

- [x] T056 [P] [US6] Create DeleteConfirmModal component in frontend/src/components/DeleteConfirmModal.tsx
- [x] T057 [US6] Add deleteTool API method in frontend/src/services/toolApi.ts
- [x] T058 [US6] Add Delete button with confirmation to ToolDetail page in frontend/src/pages/ToolDetail.tsx
- [x] T059 [US6] Redirect to tool list after successful deletion in frontend/src/pages/ToolDetail.tsx

**Checkpoint**: Tool deletion with confirmation should work

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T060 [P] Add loading states to all frontend pages in frontend/src/pages/
- [x] T061 [P] Add error handling and error boundary in frontend/src/components/ErrorBoundary.tsx
- [x] T062 [P] Create consistent Layout component with navigation in frontend/src/components/Layout.tsx
- [x] T063 Add status toggle (activate/deactivate) to ToolDetail page in frontend/src/pages/ToolDetail.tsx
- [ ] T064 Add category filter to tool list in frontend/src/pages/ToolList.tsx
- [ ] T065 Create sample tool data for demo/testing in src/aiops_tools/scripts/seed_data.py
- [ ] T066 Update quickstart.md with actual working commands in specs/001-llm-tool-management/quickstart.md
- [ ] T067 Verify all API endpoints match contracts in specs/001-llm-tool-management/contracts/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Browse/Search): Can start immediately after Phase 2
  - US2 (Create Tool): Can start immediately after Phase 2
  - US3 (LLM Query): Can start immediately after Phase 2
  - US4 (Execute): Depends on US3 (LLM endpoints) for invoke endpoint
  - US5 (Edit): Can start immediately after Phase 2
  - US6 (Delete): Can start immediately after Phase 2
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories - Pure frontend
- **User Story 2 (P1)**: No dependencies on other stories - Frontend + minor backend update
- **User Story 3 (P1)**: No dependencies on other stories - Pure backend (LLM API)
- **User Story 4 (P2)**: Depends on US3 being complete (uses same endpoint file)
- **User Story 5 (P2)**: No dependencies on other stories
- **User Story 6 (P3)**: No dependencies on other stories

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: T002, T003 can run in parallel
- **Phase 2**: T007, T008, T009 can run in parallel; T014 is independent
- **Phase 3**: T015, T016, T017, T018 can run in parallel
- **Phase 4**: T024, T025, T026 can run in parallel
- **Phase 5**: T033, T034 can run in parallel
- **Phase 6**: T040, T047 can run in parallel
- **Phase 8**: T056 is independent
- **Phase 9**: T060, T061, T062 can run in parallel
- **Cross-Story**: US1, US2, US3, US5, US6 can all be worked on in parallel after Phase 2

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch schema updates together:
Task: "Add script_content to ToolCreate schema in src/aiops_tools/schemas/tool.py"
Task: "Add script_content to ToolUpdate schema in src/aiops_tools/schemas/tool.py"
Task: "Add script_content to ToolResponse schema in src/aiops_tools/schemas/tool.py"
Task: "Initialize frontend React project with TypeScript and Ant Design in frontend/"
```

## Parallel Example: User Story 1 (Browse/Search)

```bash
# Launch all page components together:
Task: "Create ToolList page component in frontend/src/pages/ToolList.tsx"
Task: "Create ToolCard component for list display in frontend/src/components/ToolCard.tsx"
Task: "Create SearchBar component with keyword input in frontend/src/components/SearchBar.tsx"
Task: "Create Pagination component in frontend/src/components/Pagination.tsx"
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Browse/Search) - Visible frontend
4. Complete Phase 4: User Story 2 (Create Tool) - Add content
5. Complete Phase 5: User Story 3 (LLM Query) - LLM integration
6. **STOP and VALIDATE**: All P1 stories testable independently
7. Deploy/demo if ready (MVP complete!)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Users can browse tools
3. Add User Story 2 → Test independently → Users can create tools
4. Add User Story 3 → Test independently → LLMs can discover tools
5. Add User Story 4 → Test independently → Tools can be executed
6. Add User Story 5 → Test independently → Tools can be updated
7. Add User Story 6 → Test independently → Tools can be deleted
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Frontend browse) + User Story 2 (Frontend create)
   - Developer B: User Story 3 (LLM API) + User Story 4 (Execution)
   - Developer C: User Story 5 (Edit) + User Story 6 (Delete)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Frontend initialized as new React project in frontend/ directory
- Backend extends existing FastAPI project in src/aiops_tools/
