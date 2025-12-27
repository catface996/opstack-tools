# Feature Specification: Operations Tools Collection

**Feature Branch**: `002-ops-tools`
**Created**: 2025-12-27
**Status**: Draft
**Input**: User description: "支持K8S相关命令执行的工具，支持数据库相关命令执行的工具，支持Java应用相关命令执行的工具，支持aws 云服务相关命令执行的工具。"

## Overview

This feature adds a collection of pre-built operational tools to the AIOps Tools platform, organized into four categories:
1. **Kubernetes (K8S) Tools** - Container orchestration operations
2. **Database Tools** - Database query and management operations
3. **Java Application Tools** - JVM application monitoring and management
4. **AWS Cloud Tools** - Amazon Web Services resource management

These tools enable LLM agents to perform common DevOps and SRE tasks through the existing tool execution framework.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - K8S Pod Operations (Priority: P1)

As an SRE using an LLM agent, I want to execute Kubernetes operations such as listing pods, checking pod status, viewing logs, and restarting deployments so that I can quickly diagnose and resolve cluster issues.

**Why this priority**: Kubernetes is the most common container orchestration platform, and pod-level operations are the most frequently performed tasks in incident response.

**Independent Test**: Can be fully tested by deploying to a K8S cluster and executing pod list/describe/logs commands, delivering immediate visibility into cluster state.

**Acceptance Scenarios**:

1. **Given** a configured K8S context, **When** the agent invokes the "k8s_list_pods" tool with namespace parameter, **Then** the system returns a list of pods with name, status, and age
2. **Given** a running pod name, **When** the agent invokes "k8s_get_logs" with pod name and optional tail lines, **Then** the system returns the recent log output
3. **Given** a deployment name, **When** the agent invokes "k8s_restart_deployment", **Then** the system performs a rollout restart and returns confirmation
4. **Given** an invalid namespace, **When** the agent invokes any K8S tool, **Then** the system returns a clear error message

---

### User Story 2 - Database Query Operations (Priority: P1)

As a data analyst using an LLM agent, I want to execute read-only database queries and retrieve schema information so that I can quickly investigate data issues and answer business questions.

**Why this priority**: Database operations are fundamental to most business applications, and safe query execution is essential for data investigation.

**Independent Test**: Can be fully tested by connecting to a database and executing SELECT queries, delivering immediate data access capability.

**Acceptance Scenarios**:

1. **Given** valid database credentials, **When** the agent invokes "db_execute_query" with a SELECT statement, **Then** the system returns query results in structured format
2. **Given** a table name, **When** the agent invokes "db_describe_table", **Then** the system returns column names, types, and constraints
3. **Given** a database connection, **When** the agent invokes "db_list_tables", **Then** the system returns all accessible table names
4. **Given** a non-SELECT statement (INSERT/UPDATE/DELETE), **When** the agent invokes "db_execute_query", **Then** the system rejects the query with appropriate error

---

### User Story 3 - Java Application Monitoring (Priority: P2)

As a developer using an LLM agent, I want to retrieve JVM metrics and thread dumps from running Java applications so that I can diagnose performance issues and memory problems.

**Why this priority**: Java applications are prevalent in enterprise environments, and JVM diagnostics are critical for performance troubleshooting.

**Independent Test**: Can be fully tested by connecting to a running Java application's JMX endpoint and retrieving heap memory usage.

**Acceptance Scenarios**:

1. **Given** a JMX endpoint address, **When** the agent invokes "java_get_heap_usage", **Then** the system returns current heap memory statistics
2. **Given** a running Java process, **When** the agent invokes "java_get_thread_dump", **Then** the system returns a formatted thread dump
3. **Given** a JMX endpoint, **When** the agent invokes "java_get_gc_stats", **Then** the system returns garbage collection statistics
4. **Given** an unreachable JMX endpoint, **When** the agent invokes any Java tool, **Then** the system returns connection error details

---

### User Story 4 - AWS Resource Management (Priority: P2)

As a cloud engineer using an LLM agent, I want to query AWS resources such as EC2 instances, S3 buckets, and RDS databases so that I can monitor infrastructure and investigate issues.

**Why this priority**: AWS is the leading cloud provider, and resource visibility is essential for cloud operations.

**Independent Test**: Can be fully tested by configuring AWS credentials and listing EC2 instances in a region.

**Acceptance Scenarios**:

1. **Given** valid AWS credentials, **When** the agent invokes "aws_list_ec2_instances" with region, **Then** the system returns instance IDs, states, and types
2. **Given** an EC2 instance ID, **When** the agent invokes "aws_describe_instance", **Then** the system returns detailed instance information
3. **Given** AWS credentials, **When** the agent invokes "aws_list_s3_buckets", **Then** the system returns bucket names and creation dates
4. **Given** a bucket name, **When** the agent invokes "aws_list_s3_objects" with prefix, **Then** the system returns object keys and sizes
5. **Given** invalid AWS credentials, **When** the agent invokes any AWS tool, **Then** the system returns authentication error

---

### Edge Cases

- What happens when K8S cluster is unreachable? System returns connection timeout error with troubleshooting hints
- What happens when database query exceeds timeout? System terminates query and returns timeout error with elapsed time
- How does system handle AWS rate limiting? System returns rate limit error and suggests retry after delay
- What happens when JMX authentication fails? System returns authentication error with endpoint details
- How does system handle large query results? System limits result rows and indicates truncation

## Requirements *(mandatory)*

### Functional Requirements

#### K8S Tools
- **FR-001**: System MUST provide a tool to list pods in a specified namespace with status information
- **FR-002**: System MUST provide a tool to retrieve pod logs with configurable line limit
- **FR-003**: System MUST provide a tool to describe pod details including events
- **FR-004**: System MUST provide a tool to restart deployments via rollout restart
- **FR-005**: System MUST provide a tool to list namespaces in the cluster
- **FR-006**: System MUST provide a tool to get deployment status and replica counts

#### Database Tools
- **FR-007**: System MUST provide a tool to execute read-only SQL queries
- **FR-008**: System MUST enforce read-only mode by rejecting non-SELECT statements
- **FR-009**: System MUST provide a tool to list database tables
- **FR-010**: System MUST provide a tool to describe table schema
- **FR-011**: System MUST support configurable query timeout
- **FR-012**: System MUST limit query result rows to prevent memory issues

#### Java Application Tools
- **FR-013**: System MUST provide a tool to retrieve JVM heap memory usage via JMX
- **FR-014**: System MUST provide a tool to generate thread dumps
- **FR-015**: System MUST provide a tool to retrieve garbage collection statistics
- **FR-016**: System MUST provide a tool to list MBeans available on JMX endpoint
- **FR-017**: System MUST support JMX authentication when required

#### AWS Tools
- **FR-018**: System MUST provide a tool to list EC2 instances with filters
- **FR-019**: System MUST provide a tool to describe EC2 instance details
- **FR-020**: System MUST provide a tool to list S3 buckets
- **FR-021**: System MUST provide a tool to list S3 objects with prefix filtering
- **FR-022**: System MUST provide a tool to describe RDS instances
- **FR-023**: System MUST provide a tool to get CloudWatch metrics for resources

#### Common Requirements
- **FR-024**: All tools MUST follow the existing tool definition schema with input_schema and script_content
- **FR-025**: All tools MUST provide meaningful error messages on failure
- **FR-026**: All tools MUST be categorized under appropriate tool categories
- **FR-027**: All tools MUST include comprehensive descriptions for LLM understanding
- **FR-028**: Tools MUST support configurable credentials/endpoints via tool arguments

### Key Entities

- **Tool Category**: Organizes tools by domain (K8S, Database, Java, AWS), with name and description
- **Tool Definition**: Individual tool with name, description, input schema, and execution script
- **Tool Execution**: Record of tool invocation with input parameters, output results, and timing
- **Credential Configuration**: Connection parameters for external systems (stored separately from tool definitions)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 4 tool categories are created and contain at least 4 tools each
- **SC-002**: Each tool can be successfully invoked through the LLM tools/invoke endpoint
- **SC-003**: Tool execution completes within 30 seconds for standard operations
- **SC-004**: Error scenarios return user-friendly messages within 5 seconds
- **SC-005**: Tools can be discovered via LLM tools/list endpoint with accurate descriptions
- **SC-006**: 100% of tools have input schemas that validate required parameters
- **SC-007**: Tool documentation enables users to understand usage without additional guidance

## Assumptions

- K8S tools will use kubectl commands or Kubernetes Python client
- Database tools will initially support PostgreSQL and MySQL; other databases can be added later
- Java tools assume JMX is enabled and accessible on target applications
- AWS tools will use boto3 and require AWS credentials configured in the environment or passed as parameters
- All tools execute in the existing Python sandbox environment with configurable timeout
- Sensitive credentials will be passed as tool arguments rather than stored in tool definitions
- Tools are designed for read operations and safe administrative tasks; destructive operations require explicit confirmation
