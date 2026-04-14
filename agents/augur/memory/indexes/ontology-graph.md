---
description: Generated ontology graph index for Augur concepts and frameworks
---
# Ontology Graph

Generated from `memory/catalog/concepts/*.md` and `memory/catalog/frameworks/*/semantics.yaml`.

Authored relationship metadata comes from concept frontmatter and framework semantics.
Framework-authored edges take precedence over inferred framework hints, and concept-authored edges take precedence over prose-link references.
Plain prose links are kept as low-confidence inferred `references` edges for maintenance rather than treated as equal authority.

## Maintenance

- Authored edges: `72`
- Inferred edges: `666`
- Low-confidence inferred references needing review: `38`

Top low-confidence inferred references:
- `framework:fastapi` `commonly_implies` `concept:repository`
- `concept:block-content` `references` `concept:component`
- `concept:block-content` `references` `concept:search-index`
- `concept:block-content` `references` `concept:versioned-document`
- `concept:catalog` `references` `concept:rule-engine`
- `concept:catalog` `references` `concept:search-index`
- `concept:catalog` `references` `concept:subscription`
- `concept:conversation-thread` `references` `concept:pagination`
- `concept:conversation-thread` `references` `concept:pub-sub`
- `concept:conversation-thread` `references` `concept:websocket`
- `concept:ledger` `references` `concept:audit-logging`
- `concept:ledger` `references` `concept:event-sourcing`

```mermaid
graph TD
  abstraction_algorithmic["algorithmic"]
  abstraction_api["api"]
  abstraction_architectural["architectural"]
  abstraction_collaboration["collaboration"]
  abstraction_commerce["commerce"]
  abstraction_communication["communication"]
  abstraction_compiler["compiler"]
  abstraction_compute["compute"]
  abstraction_concurrency["concurrency"]
  abstraction_content["content"]
  abstraction_data["data"]
  abstraction_deployment["deployment"]
  abstraction_design["design"]
  abstraction_error_handling["error-handling"]
  abstraction_financial["financial"]
  abstraction_frontend["frontend"]
  abstraction_geospatial["geospatial"]
  abstraction_graph["graph"]
  abstraction_infrastructure["infrastructure"]
  abstraction_integration["integration"]
  abstraction_lifecycle["lifecycle"]
  abstraction_logic["logic"]
  abstraction_messaging["messaging"]
  abstraction_ml["ml"]
  abstraction_observability["observability"]
  abstraction_realtime["realtime"]
  abstraction_resilience["resilience"]
  abstraction_search["search"]
  abstraction_security["security"]
  abstraction_social["social"]
  abstraction_temporal["temporal"]
  abstraction_testing["testing"]
  concept_abstract_factory["Abstract Factory"]
  concept_active_record["Active Record"]
  concept_actor_model["Actor Model"]
  concept_adapter["Adapter"]
  concept_aggregate["Aggregate Root"]
  concept_anemic_domain_model["Anemic Domain Model"]
  concept_anti_corruption_layer["Anti-Corruption Layer"]
  concept_api_gateway["API Gateway"]
  concept_api_key_auth["API Key Authentication"]
  concept_ast["Abstract Syntax Tree (AST)"]
  concept_audit_logging["Audit Logging"]
  concept_backpressure["Backpressure"]
  concept_batch_loader["Batch Loader (N+1 Prevention)"]
  concept_batch_processing["Batch Processing"]
  concept_bff["Backend for Frontend"]
  concept_big_ball_of_mud["Big Ball of Mud"]
  concept_block_content["Block Content"]
  concept_bloom_filter["Bloom Filter"]
  concept_blue_green["Blue-Green Deployment"]
  concept_boolean_blindness["Boolean Blindness"]
  concept_breaking_changes["Breaking Changes"]
  concept_bridge["Bridge"]
  concept_builder["Builder"]
  concept_bulkhead["Bulkhead"]
  concept_busy_waiting["Busy Waiting"]
  concept_cache_aside["Cache-Aside"]
  concept_cache_stampede_prevention["Cache Stampede Prevention"]
  concept_callback_hell["Callback Hell"]
  concept_canary["Canary Release"]
  concept_cargo_cult["Cargo Cult Programming"]
  concept_catalog["Catalog"]
  concept_cell_based["Cell-Based"]
  concept_chain_of_responsibility["Chain of Responsibility"]
  concept_change_data_capture["Change Data Capture (CDC)"]
  concept_chatty_api["Chatty API"]
  concept_choreography["Choreography"]
  concept_circuit_breaker["Circuit Breaker"]
  concept_circular_dependency["Circular Dependency"]
  concept_claim_check["Claim Check"]
  concept_command["Command"]
  concept_competing_consumers["Competing Consumers"]
  concept_component["Component Architecture"]
  concept_component_slot["Component Slot"]
  concept_composite["Composite"]
  concept_config_management["Configuration Management"]
  concept_config_sprawl["Configuration Sprawl"]
  concept_connection_pooling["Connection Pooling"]
  concept_content_negotiation["Content/Protocol Negotiation"]
  concept_contract_testing["Contract Testing"]
  concept_conversation_thread["Conversation Thread"]
  concept_copy_paste_programming["Copy-Paste Programming"]
  concept_correlation_id["Correlation ID"]
  concept_cors["CORS (Cross-Origin Resource Sharing)"]
  concept_cqrs["CQRS"]
  concept_data_mapper["Data Mapper"]
  concept_data_pipeline["Data Pipeline"]
  concept_database_migration["Database Migration"]
  concept_ddd["Domain-Driven Design (DDD)"]
  concept_dead_letter["Dead Letter Queue"]
  concept_deadlock["Deadlock"]
  concept_decorator["Decorator/Wrapper"]
  concept_deep_nesting["Deep Nesting"]
  concept_dependency_injection["Dependency Injection"]
  concept_distributed_lock["Distributed Lock"]
  concept_distributed_monolith["Distributed Monolith"]
  concept_distributed_tracing["Distributed Tracing"]
  concept_dual_writes["Dual Writes"]
  concept_entity_component_system["Entity-Component-System (ECS)"]
  concept_environment_parity_gap["Environment Parity Gap"]
  concept_error_boundary["Error Boundary"]
  concept_error_code_returns["Error Code Returns"]
  concept_etl["ETL/ELT"]
  concept_event_carried_state["Event-Carried State Transfer (Fat Events)"]
  concept_event_driven["Event-Driven Architecture"]
  concept_event_log["Event Log"]
  concept_event_notification["Event Notification (Thin Events)"]
  concept_event_sourcing["Event Sourcing"]
  concept_experiment_framework["A/B Experiment Framework"]
  concept_facade["Facade"]
  concept_factory["Factory"]
  concept_failure_cascade["Failure Cascade"]
  concept_fan_in["Fan-In"]
  concept_fan_out["Fan-Out"]
  concept_feature_envy["Feature Envy"]
  concept_feature_flag["Feature Flag/Toggle"]
  concept_feature_store["Feature Store"]
  concept_fire_and_forget["Fire and Forget"]
  concept_fixture_builder["Test Fixture / Data Builder"]
  concept_flaky_tests["Flaky Tests"]
  concept_flux["Flux/Redux (Unidirectional Data Flow)"]
  concept_flyweight["Flyweight"]
  concept_form_binding["Form Binding"]
  concept_future_promise["Future/Promise"]
  concept_game_loop["Game Loop"]
  concept_gateway_backends["Gateway-Backends"]
  concept_gitops["GitOps"]
  concept_god_endpoint["God Endpoint"]
  concept_god_object["God Object/Class"]
  concept_golden_hammer["Golden Hammer"]
  concept_graceful_degradation["Graceful Degradation"]
  concept_graph["Graph"]
  concept_graphql["GraphQL"]
  concept_grpc["gRPC/RPC"]
  concept_hardcoded_credentials["Hardcoded Credentials"]
  concept_hardcoded_urls["Hardcoded URLs"]
  concept_health_check["Health Check"]
  concept_hexagonal["Hexagonal (Ports & Adapters)"]
  concept_hidden_side_effects["Hidden Side Effects"]
  concept_hydration["Hydration"]
  concept_ice_cream_cone["Ice Cream Cone"]
  concept_idempotent_consumer["Idempotent Consumer"]
  concept_immutable_infra["Immutable Infrastructure"]
  concept_inbox["Inbox"]
  concept_inconsistent_naming["Inconsistent Naming"]
  concept_infrastructure_as_code["Infrastructure as Code"]
  concept_input_validation["Input Validation"]
  concept_insecure_deserialization["Insecure Deserialization"]
  concept_intermediate_representation["Intermediate Representation (IR)"]
  concept_iterator["Iterator"]
  concept_key_value_model["Key-Value"]
  concept_lava_flow["Lava Flow (Dead Code)"]
  concept_layered["Layered"]
  concept_lazy_loading["Lazy Loading"]
  concept_leader_election["Leader Election"]
  concept_leaky_abstraction["Leaky Abstraction"]
  concept_ledger["Ledger"]
  concept_lexer_parser["Lexer/Parser"]
  concept_log_and_throw["Log and Throw"]
  concept_log_spam["Log Spam"]
  concept_long_polling["Long Polling"]
  concept_long_transactions["Long Transactions"]
  concept_lru_cache["LRU Cache"]
  concept_magic_numbers["Magic Numbers/Strings"]
  concept_mapreduce["MapReduce"]
  concept_materialized_view["Materialized View"]
  concept_mediator["Mediator"]
  concept_memento["Memento"]
  concept_memory_leak["Memory Leak"]
  concept_message_queue["Message Queue"]
  concept_metric_cardinality_explosion["Metric Cardinality Explosion"]
  concept_metrics_instrumentation["Metrics Instrumentation"]
  concept_micro_frontend["Micro-Frontend"]
  concept_microservices["Microservices"]
  concept_middleware["Middleware"]
  concept_misleading_names["Misleading Names"]
  concept_missing_log_context["Missing Log Context"]
  concept_model_registry["Model Registry"]
  concept_modular_monolith["Modular Monolith"]
  concept_monad["Monad/Railway-Oriented Programming"]
  concept_mtls["Mutual TLS"]
  concept_multi_tenant["Multi-Tenant"]
  concept_mvc["Model-View-Controller"]
  concept_mvvm["Model-View-ViewModel"]
  concept_n_plus_one["N+1 Queries"]
  concept_null_object["Null Object"]
  concept_oauth_oidc["OAuth2/OpenID Connect"]
  concept_object_pool["Object Pool"]
  concept_observer["Observer"]
  concept_optimistic_locking["Optimistic Locking"]
  concept_optimistic_update["Optimistic Update"]
  concept_outbox["Outbox"]
  concept_over_under_fetching["Over/Under-Fetching"]
  concept_pagination["Pagination"]
  concept_pipeline_filter["Pipeline/Filter"]
  concept_pipeline_stages["Pipeline Stages"]
  concept_plugin["Plugin Architecture"]
  concept_plugin_host["Plugin Host"]
  concept_pokemon_exception["Pokemon Exception"]
  concept_polling_flow["Polling"]
  concept_premature_optimization["Premature Optimization"]
  concept_primitive_obsession["Primitive Obsession"]
  concept_producer_consumer["Producer-Consumer"]
  concept_prop_drilling["Prop Drilling"]
  concept_property_graph["Property Graph"]
  concept_property_testing["Property-Based Testing"]
  concept_prototype["Prototype"]
  concept_proxy["Proxy"]
  concept_pub_sub["Publish-Subscribe"]
  concept_race_condition["Race Condition"]
  concept_rate_limiting["Rate Limiting/Throttling"]
  concept_rbac["Role-Based Access Control"]
  concept_reactive_store["Reactive Store"]
  concept_reactor["Reactor/Event Loop"]
  concept_read_through["Read-Through Cache"]
  concept_read_write_lock["Read-Write Lock"]
  concept_refresh_ahead["Refresh-Ahead Cache"]
  concept_registry_model["Registry"]
  concept_reinventing_the_wheel["Reinventing the Wheel"]
  concept_repository["Repository"]
  concept_request_path["Request Path"]
  concept_request_reply["Request-Reply"]
  concept_rest["REST API"]
  concept_result_type["Result/Either Type"]
  concept_retry["Retry with Backoff"]
  concept_ring_buffer["Ring Buffer"]
  concept_route_guard["Route Guard"]
  concept_router["Router"]
  concept_rule_engine["Rule Engine"]
  concept_saga["Saga"]
  concept_saga_orchestrator["Saga Orchestrator"]
  concept_scatter_gather["Scatter-Gather"]
  concept_scheduler["Cron/Scheduler"]
  concept_schema_on_read["Schema-on-Read"]
  concept_search_index["Search Index"]
  concept_secret_management["Secret Management"]
  concept_select_star["Select Star"]
  concept_server_prefetch["Server Prefetch"]
  concept_server_route_registration["Server Route Registration"]
  concept_server_sent_events["Server-Sent Events (SSE)"]
  concept_serverless["Serverless / FaaS"]
  concept_service_discovery["Service Discovery"]
  concept_service_manager["Service Manager"]
  concept_service_mesh["Service Mesh"]
  concept_session_auth["Session-Based Authentication"]
  concept_sharding["Sharding"]
  concept_shotgun_surgery["Shotgun Surgery"]
  concept_side_effect_hook["Side Effect Hook"]
  concept_sidecar["Sidecar"]
  concept_sidecar_mesh["Sidecar Mesh"]
  concept_singleton["Singleton"]
  concept_snapshot_testing["Snapshot Testing"]
  concept_snowflake_server["Snowflake Server"]
  concept_social_graph["Social Graph"]
  concept_soft_delete["Soft Delete"]
  concept_spaghetti_code["Spaghetti Code"]
  concept_spatial["Spatial"]
  concept_spatial_partitioning["Spatial Partitioning"]
  concept_specification["Specification Pattern"]
  concept_sql_injection["SQL Injection"]
  concept_state_machine["State Machine"]
  concept_strangler_fig["Strangler Fig"]
  concept_strategy["Strategy"]
  concept_stream_to_store["Stream-to-Store"]
  concept_streaming_flow["Streaming"]
  concept_stringly_typed["Stringly Typed"]
  concept_structured_logging["Structured Logging"]
  concept_subscription["Subscription"]
  concept_suspense_boundary["Suspense Boundary"]
  concept_swallowed_exception["Swallowed Exception"]
  concept_sync_in_async["Sync-in-Async"]
  concept_template_method["Template Method"]
  concept_temporal_coupling["Temporal Coupling"]
  concept_tenant_isolation["Tenant Isolation"]
  concept_tenant_routing["Tenant-Aware Routing"]
  concept_tensor["Tensor"]
  concept_test_doubles["Test Doubles (Mock/Stub/Fake/Spy)"]
  concept_test_pollution["Test Pollution"]
  concept_tick_simulation["Tick-Based Simulation"]
  concept_tight_coupling["Tight Coupling"]
  concept_time_series["Time Series"]
  concept_timeout["Timeout"]
  concept_token_auth["Token-Based Authentication (JWT)"]
  concept_train_wreck["Train Wreck"]
  concept_training_pipeline["Training Pipeline"]
  concept_trie["Trie (Prefix Tree)"]
  concept_unbounded_growth["Unbounded Growth"]
  concept_unit_of_work["Unit of Work"]
  concept_value_object["Value Object"]
  concept_versioned_document["Versioned Document"]
  concept_visitor["Visitor"]
  concept_webhook["Webhook"]
  concept_websocket["WebSocket"]
  concept_worker_pool["Worker/Thread Pool"]
  concept_workflow_engine["Workflow Engine"]
  concept_workflow_state_machine["Workflow / State Machine"]
  concept_write_behind["Write-Behind"]
  type_anti_pattern["anti-pattern"]
  type_domain_model["domain-model"]
  type_flow_shape["flow-shape"]
  type_pattern["pattern"]
  type_structure_shape["structure-shape"]
  type_unknown["unknown"]
  framework_fastapi["FastAPI"]
  language_python["python"]
  classDef status_0 fill:#d7f5d1,stroke:#2f6b2f,stroke-width:2px
  classDef status_1 fill:#e7f0ff,stroke:#315c99,stroke-width:1px
  classDef status_2 fill:#fff1cf,stroke:#9b6a00,stroke-width:1px
  classDef status_3 fill:#f5e1f7,stroke:#7d3c8c,stroke-width:1px,stroke-dasharray: 4 2
  classDef status_4 fill:#eeeeee,stroke:#777777,stroke-width:1px
  class concept_abstract_factory status_4
  class concept_active_record status_4
  class concept_actor_model status_4
  class concept_adapter status_4
  class concept_aggregate status_4
  class concept_anemic_domain_model status_4
  class concept_anti_corruption_layer status_4
  class concept_api_gateway status_4
  class concept_api_key_auth status_0
  class concept_ast status_4
  class concept_audit_logging status_4
  class concept_backpressure status_4
  class concept_batch_loader status_4
  class concept_batch_processing status_4
  class concept_bff status_4
  class concept_big_ball_of_mud status_4
  class concept_block_content status_4
  class concept_bloom_filter status_4
  class concept_blue_green status_4
  class concept_boolean_blindness status_4
  class concept_breaking_changes status_4
  class concept_bridge status_4
  class concept_builder status_4
  class concept_bulkhead status_4
  class concept_busy_waiting status_4
  class concept_cache_aside status_4
  class concept_cache_stampede_prevention status_4
  class concept_callback_hell status_4
  class concept_canary status_4
  class concept_cargo_cult status_4
  class concept_catalog status_4
  class concept_cell_based status_4
  class concept_chain_of_responsibility status_4
  class concept_change_data_capture status_4
  class concept_chatty_api status_4
  class concept_choreography status_4
  class concept_circuit_breaker status_4
  class concept_circular_dependency status_4
  class concept_claim_check status_4
  class concept_command status_4
  class concept_competing_consumers status_4
  class concept_component status_0
  class concept_component_slot status_1
  class concept_composite status_4
  class concept_config_management status_4
  class concept_config_sprawl status_4
  class concept_connection_pooling status_4
  class concept_content_negotiation status_4
  class concept_contract_testing status_4
  class concept_conversation_thread status_4
  class concept_copy_paste_programming status_4
  class concept_correlation_id status_4
  class concept_cors status_4
  class concept_cqrs status_4
  class concept_data_mapper status_4
  class concept_data_pipeline status_4
  class concept_database_migration status_4
  class concept_ddd status_4
  class concept_dead_letter status_4
  class concept_deadlock status_4
  class concept_decorator status_4
  class concept_deep_nesting status_4
  class concept_dependency_injection status_4
  class concept_distributed_lock status_4
  class concept_distributed_monolith status_4
  class concept_distributed_tracing status_4
  class concept_dual_writes status_4
  class concept_entity_component_system status_4
  class concept_environment_parity_gap status_4
  class concept_error_boundary status_4
  class concept_error_code_returns status_4
  class concept_etl status_4
  class concept_event_carried_state status_1
  class concept_event_driven status_0
  class concept_event_log status_4
  class concept_event_notification status_1
  class concept_event_sourcing status_4
  class concept_experiment_framework status_4
  class concept_facade status_4
  class concept_factory status_4
  class concept_failure_cascade status_4
  class concept_fan_in status_4
  class concept_fan_out status_4
  class concept_feature_envy status_4
  class concept_feature_flag status_4
  class concept_feature_store status_4
  class concept_fire_and_forget status_4
  class concept_fixture_builder status_4
  class concept_flaky_tests status_4
  class concept_flux status_4
  class concept_flyweight status_4
  class concept_form_binding status_4
  class concept_future_promise status_4
  class concept_game_loop status_4
  class concept_gateway_backends status_4
  class concept_gitops status_4
  class concept_god_endpoint status_4
  class concept_god_object status_4
  class concept_golden_hammer status_4
  class concept_graceful_degradation status_4
  class concept_graph status_0
  class concept_graphql status_4
  class concept_grpc status_4
  class concept_hardcoded_credentials status_4
  class concept_hardcoded_urls status_4
  class concept_health_check status_4
  class concept_hexagonal status_4
  class concept_hidden_side_effects status_4
  class concept_hydration status_4
  class concept_ice_cream_cone status_4
  class concept_idempotent_consumer status_4
  class concept_immutable_infra status_4
  class concept_inbox status_4
  class concept_inconsistent_naming status_4
  class concept_infrastructure_as_code status_4
  class concept_input_validation status_4
  class concept_insecure_deserialization status_4
  class concept_intermediate_representation status_4
  class concept_iterator status_4
  class concept_key_value_model status_4
  class concept_lava_flow status_4
  class concept_layered status_0
  class concept_lazy_loading status_4
  class concept_leader_election status_4
  class concept_leaky_abstraction status_4
  class concept_ledger status_4
  class concept_lexer_parser status_4
  class concept_log_and_throw status_4
  class concept_log_spam status_4
  class concept_long_polling status_4
  class concept_long_transactions status_4
  class concept_lru_cache status_4
  class concept_magic_numbers status_4
  class concept_mapreduce status_4
  class concept_materialized_view status_4
  class concept_mediator status_4
  class concept_memento status_4
  class concept_memory_leak status_4
  class concept_message_queue status_4
  class concept_metric_cardinality_explosion status_4
  class concept_metrics_instrumentation status_4
  class concept_micro_frontend status_4
  class concept_microservices status_4
  class concept_middleware status_0
  class concept_misleading_names status_4
  class concept_missing_log_context status_4
  class concept_model_registry status_4
  class concept_modular_monolith status_4
  class concept_monad status_4
  class concept_mtls status_4
  class concept_multi_tenant status_4
  class concept_mvc status_1
  class concept_mvvm status_1
  class concept_n_plus_one status_4
  class concept_null_object status_4
  class concept_oauth_oidc status_0
  class concept_object_pool status_4
  class concept_observer status_4
  class concept_optimistic_locking status_4
  class concept_optimistic_update status_4
  class concept_outbox status_4
  class concept_over_under_fetching status_4
  class concept_pagination status_4
  class concept_pipeline_filter status_4
  class concept_pipeline_stages status_4
  class concept_plugin status_0
  class concept_plugin_host status_1
  class concept_pokemon_exception status_4
  class concept_polling_flow status_4
  class concept_premature_optimization status_4
  class concept_primitive_obsession status_4
  class concept_producer_consumer status_4
  class concept_prop_drilling status_4
  class concept_property_graph status_1
  class concept_property_testing status_4
  class concept_prototype status_4
  class concept_proxy status_4
  class concept_pub_sub status_4
  class concept_race_condition status_4
  class concept_rate_limiting status_4
  class concept_rbac status_4
  class concept_reactive_store status_4
  class concept_reactor status_4
  class concept_read_through status_4
  class concept_read_write_lock status_4
  class concept_refresh_ahead status_4
  class concept_registry_model status_4
  class concept_reinventing_the_wheel status_4
  class concept_repository status_4
  class concept_request_path status_2
  class concept_request_reply status_4
  class concept_rest status_4
  class concept_result_type status_4
  class concept_retry status_4
  class concept_ring_buffer status_4
  class concept_route_guard status_1
  class concept_router status_0
  class concept_rule_engine status_4
  class concept_saga status_4
  class concept_saga_orchestrator status_4
  class concept_scatter_gather status_4
  class concept_scheduler status_4
  class concept_schema_on_read status_4
  class concept_search_index status_4
  class concept_secret_management status_4
  class concept_select_star status_4
  class concept_server_prefetch status_4
  class concept_server_route_registration status_0
  class concept_server_sent_events status_4
  class concept_serverless status_4
  class concept_service_discovery status_4
  class concept_service_manager status_4
  class concept_service_mesh status_4
  class concept_session_auth status_0
  class concept_sharding status_4
  class concept_shotgun_surgery status_4
  class concept_side_effect_hook status_4
  class concept_sidecar status_4
  class concept_sidecar_mesh status_4
  class concept_singleton status_4
  class concept_snapshot_testing status_4
  class concept_snowflake_server status_4
  class concept_social_graph status_1
  class concept_soft_delete status_4
  class concept_spaghetti_code status_4
  class concept_spatial status_4
  class concept_spatial_partitioning status_4
  class concept_specification status_4
  class concept_sql_injection status_4
  class concept_state_machine status_0
  class concept_strangler_fig status_4
  class concept_strategy status_4
  class concept_stream_to_store status_4
  class concept_streaming_flow status_4
  class concept_stringly_typed status_4
  class concept_structured_logging status_4
  class concept_subscription status_4
  class concept_suspense_boundary status_4
  class concept_swallowed_exception status_4
  class concept_sync_in_async status_4
  class concept_template_method status_4
  class concept_temporal_coupling status_4
  class concept_tenant_isolation status_4
  class concept_tenant_routing status_4
  class concept_tensor status_4
  class concept_test_doubles status_4
  class concept_test_pollution status_4
  class concept_tick_simulation status_4
  class concept_tight_coupling status_4
  class concept_time_series status_4
  class concept_timeout status_4
  class concept_token_auth status_0
  class concept_train_wreck status_4
  class concept_training_pipeline status_4
  class concept_trie status_4
  class concept_unbounded_growth status_4
  class concept_unit_of_work status_4
  class concept_value_object status_4
  class concept_versioned_document status_4
  class concept_visitor status_4
  class concept_webhook status_4
  class concept_websocket status_4
  class concept_worker_pool status_4
  class concept_workflow_engine status_0
  class concept_workflow_state_machine status_3
  class concept_write_behind status_4
  class framework_fastapi status_0
  framework_fastapi -->|commonly implies| concept_repository
  linkStyle 0 stroke-dasharray: 4 2
  concept_api_key_auth -->|disambiguates| concept_oauth_oidc
  concept_api_key_auth -->|disambiguates| concept_session_auth
  concept_api_key_auth -->|disambiguates| concept_token_auth
  concept_oauth_oidc -->|disambiguates| concept_api_key_auth
  concept_server_route_registration -->|disambiguates| concept_router
  concept_session_auth -->|disambiguates| concept_api_key_auth
  concept_session_auth -->|disambiguates| concept_oauth_oidc
  concept_session_auth -->|disambiguates| concept_token_auth
  concept_token_auth -->|disambiguates| concept_api_key_auth
  concept_token_auth -->|disambiguates| concept_session_auth
  concept_abstract_factory -->|has abstraction| abstraction_design
  linkStyle 11 stroke-dasharray: 4 2
  concept_active_record -->|has abstraction| abstraction_data
  linkStyle 12 stroke-dasharray: 4 2
  concept_active_record -->|has abstraction| abstraction_design
  linkStyle 13 stroke-dasharray: 4 2
  concept_actor_model -->|has abstraction| abstraction_architectural
  linkStyle 14 stroke-dasharray: 4 2
  concept_actor_model -->|has abstraction| abstraction_concurrency
  linkStyle 15 stroke-dasharray: 4 2
  concept_adapter -->|has abstraction| abstraction_design
  linkStyle 16 stroke-dasharray: 4 2
  concept_adapter -->|has abstraction| abstraction_integration
  linkStyle 17 stroke-dasharray: 4 2
  concept_aggregate -->|has abstraction| abstraction_data
  linkStyle 18 stroke-dasharray: 4 2
  concept_aggregate -->|has abstraction| abstraction_design
  linkStyle 19 stroke-dasharray: 4 2
  concept_anti_corruption_layer -->|has abstraction| abstraction_design
  linkStyle 20 stroke-dasharray: 4 2
  concept_anti_corruption_layer -->|has abstraction| abstraction_integration
  linkStyle 21 stroke-dasharray: 4 2
  concept_api_gateway -->|has abstraction| abstraction_infrastructure
  linkStyle 22 stroke-dasharray: 4 2
  concept_api_gateway -->|has abstraction| abstraction_integration
  linkStyle 23 stroke-dasharray: 4 2
  concept_api_gateway -->|has abstraction| abstraction_security
  linkStyle 24 stroke-dasharray: 4 2
  concept_api_key_auth -->|has abstraction| abstraction_security
  linkStyle 25 stroke-dasharray: 4 2
  concept_ast -->|has abstraction| abstraction_compiler
  linkStyle 26 stroke-dasharray: 4 2
  concept_ast -->|has abstraction| abstraction_data
  linkStyle 27 stroke-dasharray: 4 2
  concept_audit_logging -->|has abstraction| abstraction_observability
  linkStyle 28 stroke-dasharray: 4 2
  concept_audit_logging -->|has abstraction| abstraction_security
  linkStyle 29 stroke-dasharray: 4 2
  concept_backpressure -->|has abstraction| abstraction_concurrency
  linkStyle 30 stroke-dasharray: 4 2
  concept_backpressure -->|has abstraction| abstraction_resilience
  linkStyle 31 stroke-dasharray: 4 2
  concept_batch_loader -->|has abstraction| abstraction_data
  linkStyle 32 stroke-dasharray: 4 2
  concept_batch_processing -->|has abstraction| abstraction_data
  linkStyle 33 stroke-dasharray: 4 2
  concept_batch_processing -->|has abstraction| abstraction_lifecycle
  linkStyle 34 stroke-dasharray: 4 2
  concept_bff -->|has abstraction| abstraction_api
  linkStyle 35 stroke-dasharray: 4 2
  concept_bff -->|has abstraction| abstraction_architectural
  linkStyle 36 stroke-dasharray: 4 2
  concept_block_content -->|has abstraction| abstraction_content
  linkStyle 37 stroke-dasharray: 4 2
  concept_block_content -->|has abstraction| abstraction_data
  linkStyle 38 stroke-dasharray: 4 2
  concept_bloom_filter -->|has abstraction| abstraction_data
  linkStyle 39 stroke-dasharray: 4 2
  concept_blue_green -->|has abstraction| abstraction_deployment
  linkStyle 40 stroke-dasharray: 4 2
  concept_bridge -->|has abstraction| abstraction_design
  linkStyle 41 stroke-dasharray: 4 2
  concept_builder -->|has abstraction| abstraction_design
  linkStyle 42 stroke-dasharray: 4 2
  concept_bulkhead -->|has abstraction| abstraction_resilience
  linkStyle 43 stroke-dasharray: 4 2
  concept_cache_aside -->|has abstraction| abstraction_data
  linkStyle 44 stroke-dasharray: 4 2
  concept_cache_aside -->|has abstraction| abstraction_resilience
  linkStyle 45 stroke-dasharray: 4 2
  concept_cache_stampede_prevention -->|has abstraction| abstraction_concurrency
  linkStyle 46 stroke-dasharray: 4 2
  concept_cache_stampede_prevention -->|has abstraction| abstraction_data
  linkStyle 47 stroke-dasharray: 4 2
  concept_cache_stampede_prevention -->|has abstraction| abstraction_resilience
  linkStyle 48 stroke-dasharray: 4 2
  concept_canary -->|has abstraction| abstraction_deployment
  linkStyle 49 stroke-dasharray: 4 2
  concept_catalog -->|has abstraction| abstraction_commerce
  linkStyle 50 stroke-dasharray: 4 2
  concept_catalog -->|has abstraction| abstraction_data
  linkStyle 51 stroke-dasharray: 4 2
  concept_cell_based -->|has abstraction| abstraction_architectural
  linkStyle 52 stroke-dasharray: 4 2
  concept_cell_based -->|has abstraction| abstraction_deployment
  linkStyle 53 stroke-dasharray: 4 2
  concept_chain_of_responsibility -->|has abstraction| abstraction_design
  linkStyle 54 stroke-dasharray: 4 2
  concept_change_data_capture -->|has abstraction| abstraction_data
  linkStyle 55 stroke-dasharray: 4 2
  concept_change_data_capture -->|has abstraction| abstraction_integration
  linkStyle 56 stroke-dasharray: 4 2
  concept_choreography -->|has abstraction| abstraction_architectural
  linkStyle 57 stroke-dasharray: 4 2
  concept_choreography -->|has abstraction| abstraction_integration
  linkStyle 58 stroke-dasharray: 4 2
  concept_circuit_breaker -->|has abstraction| abstraction_integration
  linkStyle 59 stroke-dasharray: 4 2
  concept_circuit_breaker -->|has abstraction| abstraction_resilience
  linkStyle 60 stroke-dasharray: 4 2
  concept_claim_check -->|has abstraction| abstraction_integration
  linkStyle 61 stroke-dasharray: 4 2
  concept_claim_check -->|has abstraction| abstraction_messaging
  linkStyle 62 stroke-dasharray: 4 2
  concept_command -->|has abstraction| abstraction_design
  linkStyle 63 stroke-dasharray: 4 2
  concept_competing_consumers -->|has abstraction| abstraction_concurrency
  linkStyle 64 stroke-dasharray: 4 2
  concept_competing_consumers -->|has abstraction| abstraction_messaging
  linkStyle 65 stroke-dasharray: 4 2
  concept_component -->|has abstraction| abstraction_design
  linkStyle 66 stroke-dasharray: 4 2
  concept_component -->|has abstraction| abstraction_frontend
  linkStyle 67 stroke-dasharray: 4 2
  concept_component_slot -->|has abstraction| abstraction_design
  linkStyle 68 stroke-dasharray: 4 2
  concept_component_slot -->|has abstraction| abstraction_frontend
  linkStyle 69 stroke-dasharray: 4 2
  concept_composite -->|has abstraction| abstraction_design
  linkStyle 70 stroke-dasharray: 4 2
  concept_config_management -->|has abstraction| abstraction_infrastructure
  linkStyle 71 stroke-dasharray: 4 2
  concept_config_management -->|has abstraction| abstraction_lifecycle
  linkStyle 72 stroke-dasharray: 4 2
  concept_connection_pooling -->|has abstraction| abstraction_infrastructure
  linkStyle 73 stroke-dasharray: 4 2
  concept_content_negotiation -->|has abstraction| abstraction_api
  linkStyle 74 stroke-dasharray: 4 2
  concept_contract_testing -->|has abstraction| abstraction_integration
  linkStyle 75 stroke-dasharray: 4 2
  concept_contract_testing -->|has abstraction| abstraction_testing
  linkStyle 76 stroke-dasharray: 4 2
  concept_conversation_thread -->|has abstraction| abstraction_communication
  linkStyle 77 stroke-dasharray: 4 2
  concept_conversation_thread -->|has abstraction| abstraction_data
  linkStyle 78 stroke-dasharray: 4 2
  concept_correlation_id -->|has abstraction| abstraction_integration
  linkStyle 79 stroke-dasharray: 4 2
  concept_correlation_id -->|has abstraction| abstraction_observability
  linkStyle 80 stroke-dasharray: 4 2
  concept_cors -->|has abstraction| abstraction_api
  linkStyle 81 stroke-dasharray: 4 2
  concept_cors -->|has abstraction| abstraction_security
  linkStyle 82 stroke-dasharray: 4 2
  concept_cqrs -->|has abstraction| abstraction_architectural
  linkStyle 83 stroke-dasharray: 4 2
  concept_cqrs -->|has abstraction| abstraction_data
  linkStyle 84 stroke-dasharray: 4 2
  concept_data_mapper -->|has abstraction| abstraction_data
  linkStyle 85 stroke-dasharray: 4 2
  concept_data_mapper -->|has abstraction| abstraction_design
  linkStyle 86 stroke-dasharray: 4 2
  concept_data_pipeline -->|has abstraction| abstraction_data
  linkStyle 87 stroke-dasharray: 4 2
  concept_data_pipeline -->|has abstraction| abstraction_integration
  linkStyle 88 stroke-dasharray: 4 2
  concept_database_migration -->|has abstraction| abstraction_data
  linkStyle 89 stroke-dasharray: 4 2
  concept_database_migration -->|has abstraction| abstraction_lifecycle
  linkStyle 90 stroke-dasharray: 4 2
  concept_ddd -->|has abstraction| abstraction_architectural
  linkStyle 91 stroke-dasharray: 4 2
  concept_ddd -->|has abstraction| abstraction_design
  linkStyle 92 stroke-dasharray: 4 2
  concept_dead_letter -->|has abstraction| abstraction_messaging
  linkStyle 93 stroke-dasharray: 4 2
  concept_dead_letter -->|has abstraction| abstraction_resilience
  linkStyle 94 stroke-dasharray: 4 2
  concept_decorator -->|has abstraction| abstraction_design
  linkStyle 95 stroke-dasharray: 4 2
  concept_dependency_injection -->|has abstraction| abstraction_architectural
  linkStyle 96 stroke-dasharray: 4 2
  concept_dependency_injection -->|has abstraction| abstraction_design
  linkStyle 97 stroke-dasharray: 4 2
  concept_distributed_lock -->|has abstraction| abstraction_concurrency
  linkStyle 98 stroke-dasharray: 4 2
  concept_distributed_lock -->|has abstraction| abstraction_resilience
  linkStyle 99 stroke-dasharray: 4 2
  concept_distributed_tracing -->|has abstraction| abstraction_integration
  linkStyle 100 stroke-dasharray: 4 2
  concept_distributed_tracing -->|has abstraction| abstraction_observability
  linkStyle 101 stroke-dasharray: 4 2
  concept_entity_component_system -->|has abstraction| abstraction_architectural
  linkStyle 102 stroke-dasharray: 4 2
  concept_entity_component_system -->|has abstraction| abstraction_realtime
  linkStyle 103 stroke-dasharray: 4 2
  concept_error_boundary -->|has abstraction| abstraction_error_handling
  linkStyle 104 stroke-dasharray: 4 2
  concept_error_boundary -->|has abstraction| abstraction_frontend
  linkStyle 105 stroke-dasharray: 4 2
  concept_etl -->|has abstraction| abstraction_data
  linkStyle 106 stroke-dasharray: 4 2
  concept_event_carried_state -->|has abstraction| abstraction_data
  linkStyle 107 stroke-dasharray: 4 2
  concept_event_carried_state -->|has abstraction| abstraction_messaging
  linkStyle 108 stroke-dasharray: 4 2
  concept_event_driven -->|has abstraction| abstraction_architectural
  linkStyle 109 stroke-dasharray: 4 2
  concept_event_driven -->|has abstraction| abstraction_messaging
  linkStyle 110 stroke-dasharray: 4 2
  concept_event_log -->|has abstraction| abstraction_data
  linkStyle 111 stroke-dasharray: 4 2
  concept_event_log -->|has abstraction| abstraction_messaging
  linkStyle 112 stroke-dasharray: 4 2
  concept_event_notification -->|has abstraction| abstraction_integration
  linkStyle 113 stroke-dasharray: 4 2
  concept_event_notification -->|has abstraction| abstraction_messaging
  linkStyle 114 stroke-dasharray: 4 2
  concept_event_sourcing -->|has abstraction| abstraction_architectural
  linkStyle 115 stroke-dasharray: 4 2
  concept_event_sourcing -->|has abstraction| abstraction_data
  linkStyle 116 stroke-dasharray: 4 2
  concept_experiment_framework -->|has abstraction| abstraction_deployment
  linkStyle 117 stroke-dasharray: 4 2
  concept_experiment_framework -->|has abstraction| abstraction_ml
  linkStyle 118 stroke-dasharray: 4 2
  concept_facade -->|has abstraction| abstraction_design
  linkStyle 119 stroke-dasharray: 4 2
  concept_factory -->|has abstraction| abstraction_design
  linkStyle 120 stroke-dasharray: 4 2
  concept_failure_cascade -->|has abstraction| abstraction_integration
  linkStyle 121 stroke-dasharray: 4 2
  concept_failure_cascade -->|has abstraction| abstraction_resilience
  linkStyle 122 stroke-dasharray: 4 2
  concept_fan_in -->|has abstraction| abstraction_data
  linkStyle 123 stroke-dasharray: 4 2
  concept_fan_in -->|has abstraction| abstraction_integration
  linkStyle 124 stroke-dasharray: 4 2
  concept_fan_out -->|has abstraction| abstraction_integration
  linkStyle 125 stroke-dasharray: 4 2
  concept_fan_out -->|has abstraction| abstraction_messaging
  linkStyle 126 stroke-dasharray: 4 2
  concept_feature_flag -->|has abstraction| abstraction_deployment
  linkStyle 127 stroke-dasharray: 4 2
  concept_feature_flag -->|has abstraction| abstraction_design
  linkStyle 128 stroke-dasharray: 4 2
  concept_feature_store -->|has abstraction| abstraction_data
  linkStyle 129 stroke-dasharray: 4 2
  concept_feature_store -->|has abstraction| abstraction_ml
  linkStyle 130 stroke-dasharray: 4 2
  concept_fixture_builder -->|has abstraction| abstraction_testing
  linkStyle 131 stroke-dasharray: 4 2
  concept_flux -->|has abstraction| abstraction_architectural
  linkStyle 132 stroke-dasharray: 4 2
  concept_flux -->|has abstraction| abstraction_data
  linkStyle 133 stroke-dasharray: 4 2
  concept_flux -->|has abstraction| abstraction_frontend
  linkStyle 134 stroke-dasharray: 4 2
  concept_flyweight -->|has abstraction| abstraction_design
  linkStyle 135 stroke-dasharray: 4 2
  concept_form_binding -->|has abstraction| abstraction_data
  linkStyle 136 stroke-dasharray: 4 2
  concept_form_binding -->|has abstraction| abstraction_frontend
  linkStyle 137 stroke-dasharray: 4 2
  concept_future_promise -->|has abstraction| abstraction_concurrency
  linkStyle 138 stroke-dasharray: 4 2
  concept_future_promise -->|has abstraction| abstraction_design
  linkStyle 139 stroke-dasharray: 4 2
  concept_game_loop -->|has abstraction| abstraction_lifecycle
  linkStyle 140 stroke-dasharray: 4 2
  concept_game_loop -->|has abstraction| abstraction_realtime
  linkStyle 141 stroke-dasharray: 4 2
  concept_gateway_backends -->|has abstraction| abstraction_api
  linkStyle 142 stroke-dasharray: 4 2
  concept_gateway_backends -->|has abstraction| abstraction_architectural
  linkStyle 143 stroke-dasharray: 4 2
  concept_gitops -->|has abstraction| abstraction_deployment
  linkStyle 144 stroke-dasharray: 4 2
  concept_graceful_degradation -->|has abstraction| abstraction_lifecycle
  linkStyle 145 stroke-dasharray: 4 2
  concept_graceful_degradation -->|has abstraction| abstraction_resilience
  linkStyle 146 stroke-dasharray: 4 2
  concept_graph -->|has abstraction| abstraction_algorithmic
  linkStyle 147 stroke-dasharray: 4 2
  concept_graph -->|has abstraction| abstraction_data
  linkStyle 148 stroke-dasharray: 4 2
  concept_graphql -->|has abstraction| abstraction_api
  linkStyle 149 stroke-dasharray: 4 2
  concept_graphql -->|has abstraction| abstraction_integration
  linkStyle 150 stroke-dasharray: 4 2
  concept_grpc -->|has abstraction| abstraction_api
  linkStyle 151 stroke-dasharray: 4 2
  concept_grpc -->|has abstraction| abstraction_integration
  linkStyle 152 stroke-dasharray: 4 2
  concept_health_check -->|has abstraction| abstraction_lifecycle
  linkStyle 153 stroke-dasharray: 4 2
  concept_health_check -->|has abstraction| abstraction_observability
  linkStyle 154 stroke-dasharray: 4 2
  concept_hexagonal -->|has abstraction| abstraction_architectural
  linkStyle 155 stroke-dasharray: 4 2
  concept_hydration -->|has abstraction| abstraction_data
  linkStyle 156 stroke-dasharray: 4 2
  concept_hydration -->|has abstraction| abstraction_frontend
  linkStyle 157 stroke-dasharray: 4 2
  concept_idempotent_consumer -->|has abstraction| abstraction_data
  linkStyle 158 stroke-dasharray: 4 2
  concept_idempotent_consumer -->|has abstraction| abstraction_messaging
  linkStyle 159 stroke-dasharray: 4 2
  concept_idempotent_consumer -->|has abstraction| abstraction_resilience
  linkStyle 160 stroke-dasharray: 4 2
  concept_immutable_infra -->|has abstraction| abstraction_deployment
  linkStyle 161 stroke-dasharray: 4 2
  concept_immutable_infra -->|has abstraction| abstraction_infrastructure
  linkStyle 162 stroke-dasharray: 4 2
  concept_inbox -->|has abstraction| abstraction_data
  linkStyle 163 stroke-dasharray: 4 2
  concept_inbox -->|has abstraction| abstraction_messaging
  linkStyle 164 stroke-dasharray: 4 2
  concept_inbox -->|has abstraction| abstraction_resilience
  linkStyle 165 stroke-dasharray: 4 2
  concept_infrastructure_as_code -->|has abstraction| abstraction_deployment
  linkStyle 166 stroke-dasharray: 4 2
  concept_infrastructure_as_code -->|has abstraction| abstraction_infrastructure
  linkStyle 167 stroke-dasharray: 4 2
  concept_input_validation -->|has abstraction| abstraction_api
  linkStyle 168 stroke-dasharray: 4 2
  concept_input_validation -->|has abstraction| abstraction_security
  linkStyle 169 stroke-dasharray: 4 2
  concept_intermediate_representation -->|has abstraction| abstraction_compiler
  linkStyle 170 stroke-dasharray: 4 2
  concept_intermediate_representation -->|has abstraction| abstraction_data
  linkStyle 171 stroke-dasharray: 4 2
  concept_iterator -->|has abstraction| abstraction_design
  linkStyle 172 stroke-dasharray: 4 2
  concept_key_value_model -->|has abstraction| abstraction_data
  linkStyle 173 stroke-dasharray: 4 2
  concept_layered -->|has abstraction| abstraction_architectural
  linkStyle 174 stroke-dasharray: 4 2
  concept_lazy_loading -->|has abstraction| abstraction_deployment
  linkStyle 175 stroke-dasharray: 4 2
  concept_lazy_loading -->|has abstraction| abstraction_frontend
  linkStyle 176 stroke-dasharray: 4 2
  concept_leader_election -->|has abstraction| abstraction_concurrency
  linkStyle 177 stroke-dasharray: 4 2
  concept_leader_election -->|has abstraction| abstraction_resilience
  linkStyle 178 stroke-dasharray: 4 2
  concept_ledger -->|has abstraction| abstraction_data
  linkStyle 179 stroke-dasharray: 4 2
  concept_ledger -->|has abstraction| abstraction_financial
  linkStyle 180 stroke-dasharray: 4 2
  concept_lexer_parser -->|has abstraction| abstraction_compiler
  linkStyle 181 stroke-dasharray: 4 2
  concept_lexer_parser -->|has abstraction| abstraction_design
  linkStyle 182 stroke-dasharray: 4 2
  concept_long_polling -->|has abstraction| abstraction_integration
  linkStyle 183 stroke-dasharray: 4 2
  concept_lru_cache -->|has abstraction| abstraction_data
  linkStyle 184 stroke-dasharray: 4 2
  concept_lru_cache -->|has abstraction| abstraction_infrastructure
  linkStyle 185 stroke-dasharray: 4 2
  concept_mapreduce -->|has abstraction| abstraction_concurrency
  linkStyle 186 stroke-dasharray: 4 2
  concept_mapreduce -->|has abstraction| abstraction_data
  linkStyle 187 stroke-dasharray: 4 2
  concept_materialized_view -->|has abstraction| abstraction_data
  linkStyle 188 stroke-dasharray: 4 2
  concept_mediator -->|has abstraction| abstraction_design
  linkStyle 189 stroke-dasharray: 4 2
  concept_mediator -->|has abstraction| abstraction_integration
  linkStyle 190 stroke-dasharray: 4 2
  concept_memento -->|has abstraction| abstraction_design
  linkStyle 191 stroke-dasharray: 4 2
  concept_message_queue -->|has abstraction| abstraction_infrastructure
  linkStyle 192 stroke-dasharray: 4 2
  concept_message_queue -->|has abstraction| abstraction_messaging
  linkStyle 193 stroke-dasharray: 4 2
  concept_metrics_instrumentation -->|has abstraction| abstraction_observability
  linkStyle 194 stroke-dasharray: 4 2
  concept_micro_frontend -->|has abstraction| abstraction_architectural
  linkStyle 195 stroke-dasharray: 4 2
  concept_micro_frontend -->|has abstraction| abstraction_deployment
  linkStyle 196 stroke-dasharray: 4 2
  concept_micro_frontend -->|has abstraction| abstraction_frontend
  linkStyle 197 stroke-dasharray: 4 2
  concept_microservices -->|has abstraction| abstraction_architectural
  linkStyle 198 stroke-dasharray: 4 2
  concept_middleware -->|has abstraction| abstraction_integration
  linkStyle 199 stroke-dasharray: 4 2
  concept_middleware -->|has abstraction| abstraction_lifecycle
  linkStyle 200 stroke-dasharray: 4 2
  concept_model_registry -->|has abstraction| abstraction_lifecycle
  linkStyle 201 stroke-dasharray: 4 2
  concept_model_registry -->|has abstraction| abstraction_ml
  linkStyle 202 stroke-dasharray: 4 2
  concept_modular_monolith -->|has abstraction| abstraction_architectural
  linkStyle 203 stroke-dasharray: 4 2
  concept_monad -->|has abstraction| abstraction_design
  linkStyle 204 stroke-dasharray: 4 2
  concept_monad -->|has abstraction| abstraction_error_handling
  linkStyle 205 stroke-dasharray: 4 2
  concept_mtls -->|has abstraction| abstraction_infrastructure
  linkStyle 206 stroke-dasharray: 4 2
  concept_mtls -->|has abstraction| abstraction_security
  linkStyle 207 stroke-dasharray: 4 2
  concept_multi_tenant -->|has abstraction| abstraction_architectural
  linkStyle 208 stroke-dasharray: 4 2
  concept_multi_tenant -->|has abstraction| abstraction_data
  linkStyle 209 stroke-dasharray: 4 2
  concept_mvc -->|has abstraction| abstraction_architectural
  linkStyle 210 stroke-dasharray: 4 2
  concept_mvc -->|has abstraction| abstraction_frontend
  linkStyle 211 stroke-dasharray: 4 2
  concept_mvvm -->|has abstraction| abstraction_architectural
  linkStyle 212 stroke-dasharray: 4 2
  concept_mvvm -->|has abstraction| abstraction_frontend
  linkStyle 213 stroke-dasharray: 4 2
  concept_null_object -->|has abstraction| abstraction_design
  linkStyle 214 stroke-dasharray: 4 2
  concept_oauth_oidc -->|has abstraction| abstraction_security
  linkStyle 215 stroke-dasharray: 4 2
  concept_object_pool -->|has abstraction| abstraction_design
  linkStyle 216 stroke-dasharray: 4 2
  concept_object_pool -->|has abstraction| abstraction_infrastructure
  linkStyle 217 stroke-dasharray: 4 2
  concept_observer -->|has abstraction| abstraction_design
  linkStyle 218 stroke-dasharray: 4 2
  concept_observer -->|has abstraction| abstraction_messaging
  linkStyle 219 stroke-dasharray: 4 2
  concept_optimistic_locking -->|has abstraction| abstraction_concurrency
  linkStyle 220 stroke-dasharray: 4 2
  concept_optimistic_locking -->|has abstraction| abstraction_data
  linkStyle 221 stroke-dasharray: 4 2
  concept_optimistic_update -->|has abstraction| abstraction_data
  linkStyle 222 stroke-dasharray: 4 2
  concept_optimistic_update -->|has abstraction| abstraction_frontend
  linkStyle 223 stroke-dasharray: 4 2
  concept_optimistic_update -->|has abstraction| abstraction_resilience
  linkStyle 224 stroke-dasharray: 4 2
  concept_outbox -->|has abstraction| abstraction_data
  linkStyle 225 stroke-dasharray: 4 2
  concept_outbox -->|has abstraction| abstraction_messaging
  linkStyle 226 stroke-dasharray: 4 2
  concept_outbox -->|has abstraction| abstraction_resilience
  linkStyle 227 stroke-dasharray: 4 2
  concept_pagination -->|has abstraction| abstraction_api
  linkStyle 228 stroke-dasharray: 4 2
  concept_pagination -->|has abstraction| abstraction_data
  linkStyle 229 stroke-dasharray: 4 2
  concept_pipeline_filter -->|has abstraction| abstraction_data
  linkStyle 230 stroke-dasharray: 4 2
  concept_pipeline_filter -->|has abstraction| abstraction_design
  linkStyle 231 stroke-dasharray: 4 2
  concept_pipeline_stages -->|has abstraction| abstraction_architectural
  linkStyle 232 stroke-dasharray: 4 2
  concept_pipeline_stages -->|has abstraction| abstraction_data
  linkStyle 233 stroke-dasharray: 4 2
  concept_plugin -->|has abstraction| abstraction_design
  linkStyle 234 stroke-dasharray: 4 2
  concept_plugin_host -->|has abstraction| abstraction_architectural
  linkStyle 235 stroke-dasharray: 4 2
  concept_plugin_host -->|has abstraction| abstraction_design
  linkStyle 236 stroke-dasharray: 4 2
  concept_polling_flow -->|has abstraction| abstraction_integration
  linkStyle 237 stroke-dasharray: 4 2
  concept_polling_flow -->|has abstraction| abstraction_lifecycle
  linkStyle 238 stroke-dasharray: 4 2
  concept_producer_consumer -->|has abstraction| abstraction_concurrency
  linkStyle 239 stroke-dasharray: 4 2
  concept_producer_consumer -->|has abstraction| abstraction_messaging
  linkStyle 240 stroke-dasharray: 4 2
  concept_property_graph -->|has abstraction| abstraction_data
  linkStyle 241 stroke-dasharray: 4 2
  concept_property_graph -->|has abstraction| abstraction_graph
  linkStyle 242 stroke-dasharray: 4 2
  concept_property_testing -->|has abstraction| abstraction_testing
  linkStyle 243 stroke-dasharray: 4 2
  concept_prototype -->|has abstraction| abstraction_design
  linkStyle 244 stroke-dasharray: 4 2
  concept_proxy -->|has abstraction| abstraction_design
  linkStyle 245 stroke-dasharray: 4 2
  concept_pub_sub -->|has abstraction| abstraction_integration
  linkStyle 246 stroke-dasharray: 4 2
  concept_pub_sub -->|has abstraction| abstraction_messaging
  linkStyle 247 stroke-dasharray: 4 2
  concept_rate_limiting -->|has abstraction| abstraction_resilience
  linkStyle 248 stroke-dasharray: 4 2
  concept_rate_limiting -->|has abstraction| abstraction_security
  linkStyle 249 stroke-dasharray: 4 2
  concept_rbac -->|has abstraction| abstraction_security
  linkStyle 250 stroke-dasharray: 4 2
  concept_reactive_store -->|has abstraction| abstraction_data
  linkStyle 251 stroke-dasharray: 4 2
  concept_reactive_store -->|has abstraction| abstraction_frontend
  linkStyle 252 stroke-dasharray: 4 2
  concept_reactor -->|has abstraction| abstraction_architectural
  linkStyle 253 stroke-dasharray: 4 2
  concept_reactor -->|has abstraction| abstraction_concurrency
  linkStyle 254 stroke-dasharray: 4 2
  concept_read_through -->|has abstraction| abstraction_data
  linkStyle 255 stroke-dasharray: 4 2
  concept_read_write_lock -->|has abstraction| abstraction_concurrency
  linkStyle 256 stroke-dasharray: 4 2
  concept_refresh_ahead -->|has abstraction| abstraction_data
  linkStyle 257 stroke-dasharray: 4 2
  concept_refresh_ahead -->|has abstraction| abstraction_resilience
  linkStyle 258 stroke-dasharray: 4 2
  concept_registry_model -->|has abstraction| abstraction_data
  linkStyle 259 stroke-dasharray: 4 2
  concept_repository -->|has abstraction| abstraction_data
  linkStyle 260 stroke-dasharray: 4 2
  concept_repository -->|has abstraction| abstraction_design
  linkStyle 261 stroke-dasharray: 4 2
  concept_request_path -->|has abstraction| abstraction_api
  linkStyle 262 stroke-dasharray: 4 2
  concept_request_path -->|has abstraction| abstraction_integration
  linkStyle 263 stroke-dasharray: 4 2
  concept_request_reply -->|has abstraction| abstraction_integration
  linkStyle 264 stroke-dasharray: 4 2
  concept_request_reply -->|has abstraction| abstraction_messaging
  linkStyle 265 stroke-dasharray: 4 2
  concept_rest -->|has abstraction| abstraction_api
  linkStyle 266 stroke-dasharray: 4 2
  concept_rest -->|has abstraction| abstraction_integration
  linkStyle 267 stroke-dasharray: 4 2
  concept_result_type -->|has abstraction| abstraction_design
  linkStyle 268 stroke-dasharray: 4 2
  concept_result_type -->|has abstraction| abstraction_error_handling
  linkStyle 269 stroke-dasharray: 4 2
  concept_retry -->|has abstraction| abstraction_integration
  linkStyle 270 stroke-dasharray: 4 2
  concept_retry -->|has abstraction| abstraction_resilience
  linkStyle 271 stroke-dasharray: 4 2
  concept_ring_buffer -->|has abstraction| abstraction_concurrency
  linkStyle 272 stroke-dasharray: 4 2
  concept_ring_buffer -->|has abstraction| abstraction_data
  linkStyle 273 stroke-dasharray: 4 2
  concept_route_guard -->|has abstraction| abstraction_frontend
  linkStyle 274 stroke-dasharray: 4 2
  concept_route_guard -->|has abstraction| abstraction_security
  linkStyle 275 stroke-dasharray: 4 2
  concept_router -->|has abstraction| abstraction_frontend
  linkStyle 276 stroke-dasharray: 4 2
  concept_router -->|has abstraction| abstraction_integration
  linkStyle 277 stroke-dasharray: 4 2
  concept_rule_engine -->|has abstraction| abstraction_design
  linkStyle 278 stroke-dasharray: 4 2
  concept_rule_engine -->|has abstraction| abstraction_logic
  linkStyle 279 stroke-dasharray: 4 2
  concept_saga -->|has abstraction| abstraction_integration
  linkStyle 280 stroke-dasharray: 4 2
  concept_saga -->|has abstraction| abstraction_resilience
  linkStyle 281 stroke-dasharray: 4 2
  concept_saga_orchestrator -->|has abstraction| abstraction_integration
  linkStyle 282 stroke-dasharray: 4 2
  concept_saga_orchestrator -->|has abstraction| abstraction_messaging
  linkStyle 283 stroke-dasharray: 4 2
  concept_scatter_gather -->|has abstraction| abstraction_integration
  linkStyle 284 stroke-dasharray: 4 2
  concept_scheduler -->|has abstraction| abstraction_lifecycle
  linkStyle 285 stroke-dasharray: 4 2
  concept_search_index -->|has abstraction| abstraction_data
  linkStyle 286 stroke-dasharray: 4 2
  concept_search_index -->|has abstraction| abstraction_search
  linkStyle 287 stroke-dasharray: 4 2
  concept_secret_management -->|has abstraction| abstraction_infrastructure
  linkStyle 288 stroke-dasharray: 4 2
  concept_secret_management -->|has abstraction| abstraction_security
  linkStyle 289 stroke-dasharray: 4 2
  concept_server_prefetch -->|has abstraction| abstraction_data
  linkStyle 290 stroke-dasharray: 4 2
  concept_server_prefetch -->|has abstraction| abstraction_frontend
  linkStyle 291 stroke-dasharray: 4 2
  concept_server_route_registration -->|has abstraction| abstraction_api
  linkStyle 292 stroke-dasharray: 4 2
  concept_server_route_registration -->|has abstraction| abstraction_integration
  linkStyle 293 stroke-dasharray: 4 2
  concept_server_sent_events -->|has abstraction| abstraction_infrastructure
  linkStyle 294 stroke-dasharray: 4 2
  concept_server_sent_events -->|has abstraction| abstraction_integration
  linkStyle 295 stroke-dasharray: 4 2
  concept_serverless -->|has abstraction| abstraction_architectural
  linkStyle 296 stroke-dasharray: 4 2
  concept_serverless -->|has abstraction| abstraction_deployment
  linkStyle 297 stroke-dasharray: 4 2
  concept_service_discovery -->|has abstraction| abstraction_infrastructure
  linkStyle 298 stroke-dasharray: 4 2
  concept_service_discovery -->|has abstraction| abstraction_integration
  linkStyle 299 stroke-dasharray: 4 2
  concept_service_manager -->|has abstraction| abstraction_lifecycle
  linkStyle 300 stroke-dasharray: 4 2
  concept_service_mesh -->|has abstraction| abstraction_infrastructure
  linkStyle 301 stroke-dasharray: 4 2
  concept_service_mesh -->|has abstraction| abstraction_integration
  linkStyle 302 stroke-dasharray: 4 2
  concept_session_auth -->|has abstraction| abstraction_security
  linkStyle 303 stroke-dasharray: 4 2
  concept_sharding -->|has abstraction| abstraction_data
  linkStyle 304 stroke-dasharray: 4 2
  concept_sharding -->|has abstraction| abstraction_infrastructure
  linkStyle 305 stroke-dasharray: 4 2
  concept_side_effect_hook -->|has abstraction| abstraction_frontend
  linkStyle 306 stroke-dasharray: 4 2
  concept_side_effect_hook -->|has abstraction| abstraction_lifecycle
  linkStyle 307 stroke-dasharray: 4 2
  concept_sidecar -->|has abstraction| abstraction_deployment
  linkStyle 308 stroke-dasharray: 4 2
  concept_sidecar -->|has abstraction| abstraction_infrastructure
  linkStyle 309 stroke-dasharray: 4 2
  concept_sidecar -->|has abstraction| abstraction_lifecycle
  linkStyle 310 stroke-dasharray: 4 2
  concept_sidecar_mesh -->|has abstraction| abstraction_deployment
  linkStyle 311 stroke-dasharray: 4 2
  concept_sidecar_mesh -->|has abstraction| abstraction_infrastructure
  linkStyle 312 stroke-dasharray: 4 2
  concept_singleton -->|has abstraction| abstraction_design
  linkStyle 313 stroke-dasharray: 4 2
  concept_snapshot_testing -->|has abstraction| abstraction_testing
  linkStyle 314 stroke-dasharray: 4 2
  concept_social_graph -->|has abstraction| abstraction_data
  linkStyle 315 stroke-dasharray: 4 2
  concept_social_graph -->|has abstraction| abstraction_social
  linkStyle 316 stroke-dasharray: 4 2
  concept_soft_delete -->|has abstraction| abstraction_data
  linkStyle 317 stroke-dasharray: 4 2
  concept_spatial -->|has abstraction| abstraction_data
  linkStyle 318 stroke-dasharray: 4 2
  concept_spatial -->|has abstraction| abstraction_geospatial
  linkStyle 319 stroke-dasharray: 4 2
  concept_spatial_partitioning -->|has abstraction| abstraction_data
  linkStyle 320 stroke-dasharray: 4 2
  concept_spatial_partitioning -->|has abstraction| abstraction_realtime
  linkStyle 321 stroke-dasharray: 4 2
  concept_specification -->|has abstraction| abstraction_design
  linkStyle 322 stroke-dasharray: 4 2
  concept_state_machine -->|has abstraction| abstraction_design
  linkStyle 323 stroke-dasharray: 4 2
  concept_state_machine -->|has abstraction| abstraction_lifecycle
  linkStyle 324 stroke-dasharray: 4 2
  concept_strangler_fig -->|has abstraction| abstraction_architectural
  linkStyle 325 stroke-dasharray: 4 2
  concept_strangler_fig -->|has abstraction| abstraction_lifecycle
  linkStyle 326 stroke-dasharray: 4 2
  concept_strategy -->|has abstraction| abstraction_design
  linkStyle 327 stroke-dasharray: 4 2
  concept_stream_to_store -->|has abstraction| abstraction_data
  linkStyle 328 stroke-dasharray: 4 2
  concept_stream_to_store -->|has abstraction| abstraction_integration
  linkStyle 329 stroke-dasharray: 4 2
  concept_streaming_flow -->|has abstraction| abstraction_data
  linkStyle 330 stroke-dasharray: 4 2
  concept_streaming_flow -->|has abstraction| abstraction_messaging
  linkStyle 331 stroke-dasharray: 4 2
  concept_streaming_flow -->|has abstraction| abstraction_realtime
  linkStyle 332 stroke-dasharray: 4 2
  concept_structured_logging -->|has abstraction| abstraction_observability
  linkStyle 333 stroke-dasharray: 4 2
  concept_subscription -->|has abstraction| abstraction_data
  linkStyle 334 stroke-dasharray: 4 2
  concept_subscription -->|has abstraction| abstraction_financial
  linkStyle 335 stroke-dasharray: 4 2
  concept_suspense_boundary -->|has abstraction| abstraction_frontend
  linkStyle 336 stroke-dasharray: 4 2
  concept_suspense_boundary -->|has abstraction| abstraction_lifecycle
  linkStyle 337 stroke-dasharray: 4 2
  concept_template_method -->|has abstraction| abstraction_design
  linkStyle 338 stroke-dasharray: 4 2
  concept_tenant_isolation -->|has abstraction| abstraction_data
  linkStyle 339 stroke-dasharray: 4 2
  concept_tenant_isolation -->|has abstraction| abstraction_security
  linkStyle 340 stroke-dasharray: 4 2
  concept_tenant_routing -->|has abstraction| abstraction_integration
  linkStyle 341 stroke-dasharray: 4 2
  concept_tenant_routing -->|has abstraction| abstraction_security
  linkStyle 342 stroke-dasharray: 4 2
  concept_tensor -->|has abstraction| abstraction_compute
  linkStyle 343 stroke-dasharray: 4 2
  concept_tensor -->|has abstraction| abstraction_data
  linkStyle 344 stroke-dasharray: 4 2
  concept_test_doubles -->|has abstraction| abstraction_testing
  linkStyle 345 stroke-dasharray: 4 2
  concept_tick_simulation -->|has abstraction| abstraction_lifecycle
  linkStyle 346 stroke-dasharray: 4 2
  concept_tick_simulation -->|has abstraction| abstraction_realtime
  linkStyle 347 stroke-dasharray: 4 2
  concept_time_series -->|has abstraction| abstraction_data
  linkStyle 348 stroke-dasharray: 4 2
  concept_time_series -->|has abstraction| abstraction_temporal
  linkStyle 349 stroke-dasharray: 4 2
  concept_timeout -->|has abstraction| abstraction_integration
  linkStyle 350 stroke-dasharray: 4 2
  concept_timeout -->|has abstraction| abstraction_resilience
  linkStyle 351 stroke-dasharray: 4 2
  concept_token_auth -->|has abstraction| abstraction_security
  linkStyle 352 stroke-dasharray: 4 2
  concept_training_pipeline -->|has abstraction| abstraction_data
  linkStyle 353 stroke-dasharray: 4 2
  concept_training_pipeline -->|has abstraction| abstraction_ml
  linkStyle 354 stroke-dasharray: 4 2
  concept_trie -->|has abstraction| abstraction_data
  linkStyle 355 stroke-dasharray: 4 2
  concept_unit_of_work -->|has abstraction| abstraction_data
  linkStyle 356 stroke-dasharray: 4 2
  concept_unit_of_work -->|has abstraction| abstraction_design
  linkStyle 357 stroke-dasharray: 4 2
  concept_value_object -->|has abstraction| abstraction_design
  linkStyle 358 stroke-dasharray: 4 2
  concept_versioned_document -->|has abstraction| abstraction_collaboration
  linkStyle 359 stroke-dasharray: 4 2
  concept_versioned_document -->|has abstraction| abstraction_data
  linkStyle 360 stroke-dasharray: 4 2
  concept_visitor -->|has abstraction| abstraction_design
  linkStyle 361 stroke-dasharray: 4 2
  concept_webhook -->|has abstraction| abstraction_integration
  linkStyle 362 stroke-dasharray: 4 2
  concept_websocket -->|has abstraction| abstraction_infrastructure
  linkStyle 363 stroke-dasharray: 4 2
  concept_websocket -->|has abstraction| abstraction_integration
  linkStyle 364 stroke-dasharray: 4 2
  concept_worker_pool -->|has abstraction| abstraction_concurrency
  linkStyle 365 stroke-dasharray: 4 2
  concept_worker_pool -->|has abstraction| abstraction_infrastructure
  linkStyle 366 stroke-dasharray: 4 2
  concept_workflow_engine -->|has abstraction| abstraction_integration
  linkStyle 367 stroke-dasharray: 4 2
  concept_workflow_engine -->|has abstraction| abstraction_lifecycle
  linkStyle 368 stroke-dasharray: 4 2
  concept_workflow_state_machine -->|has abstraction| abstraction_data
  linkStyle 369 stroke-dasharray: 4 2
  concept_workflow_state_machine -->|has abstraction| abstraction_lifecycle
  linkStyle 370 stroke-dasharray: 4 2
  concept_write_behind -->|has abstraction| abstraction_data
  linkStyle 371 stroke-dasharray: 4 2
  concept_abstract_factory -->|has type| type_pattern
  linkStyle 372 stroke-dasharray: 4 2
  concept_active_record -->|has type| type_pattern
  linkStyle 373 stroke-dasharray: 4 2
  concept_actor_model -->|has type| type_pattern
  linkStyle 374 stroke-dasharray: 4 2
  concept_adapter -->|has type| type_pattern
  linkStyle 375 stroke-dasharray: 4 2
  concept_aggregate -->|has type| type_pattern
  linkStyle 376 stroke-dasharray: 4 2
  concept_anemic_domain_model -->|has type| type_anti_pattern
  linkStyle 377 stroke-dasharray: 4 2
  concept_anti_corruption_layer -->|has type| type_pattern
  linkStyle 378 stroke-dasharray: 4 2
  concept_api_gateway -->|has type| type_pattern
  linkStyle 379 stroke-dasharray: 4 2
  concept_api_key_auth -->|has type| type_pattern
  linkStyle 380 stroke-dasharray: 4 2
  concept_ast -->|has type| type_pattern
  linkStyle 381 stroke-dasharray: 4 2
  concept_audit_logging -->|has type| type_pattern
  linkStyle 382 stroke-dasharray: 4 2
  concept_backpressure -->|has type| type_pattern
  linkStyle 383 stroke-dasharray: 4 2
  concept_batch_loader -->|has type| type_pattern
  linkStyle 384 stroke-dasharray: 4 2
  concept_batch_processing -->|has type| type_flow_shape
  linkStyle 385 stroke-dasharray: 4 2
  concept_bff -->|has type| type_pattern
  linkStyle 386 stroke-dasharray: 4 2
  concept_big_ball_of_mud -->|has type| type_anti_pattern
  linkStyle 387 stroke-dasharray: 4 2
  concept_block_content -->|has type| type_pattern
  linkStyle 388 stroke-dasharray: 4 2
  concept_bloom_filter -->|has type| type_pattern
  linkStyle 389 stroke-dasharray: 4 2
  concept_blue_green -->|has type| type_pattern
  linkStyle 390 stroke-dasharray: 4 2
  concept_boolean_blindness -->|has type| type_anti_pattern
  linkStyle 391 stroke-dasharray: 4 2
  concept_breaking_changes -->|has type| type_anti_pattern
  linkStyle 392 stroke-dasharray: 4 2
  concept_bridge -->|has type| type_pattern
  linkStyle 393 stroke-dasharray: 4 2
  concept_builder -->|has type| type_pattern
  linkStyle 394 stroke-dasharray: 4 2
  concept_bulkhead -->|has type| type_pattern
  linkStyle 395 stroke-dasharray: 4 2
  concept_busy_waiting -->|has type| type_anti_pattern
  linkStyle 396 stroke-dasharray: 4 2
  concept_cache_aside -->|has type| type_pattern
  linkStyle 397 stroke-dasharray: 4 2
  concept_cache_stampede_prevention -->|has type| type_pattern
  linkStyle 398 stroke-dasharray: 4 2
  concept_callback_hell -->|has type| type_anti_pattern
  linkStyle 399 stroke-dasharray: 4 2
  concept_canary -->|has type| type_pattern
  linkStyle 400 stroke-dasharray: 4 2
  concept_cargo_cult -->|has type| type_anti_pattern
  linkStyle 401 stroke-dasharray: 4 2
  concept_catalog -->|has type| type_pattern
  linkStyle 402 stroke-dasharray: 4 2
  concept_cell_based -->|has type| type_structure_shape
  linkStyle 403 stroke-dasharray: 4 2
  concept_chain_of_responsibility -->|has type| type_pattern
  linkStyle 404 stroke-dasharray: 4 2
  concept_change_data_capture -->|has type| type_pattern
  linkStyle 405 stroke-dasharray: 4 2
  concept_chatty_api -->|has type| type_anti_pattern
  linkStyle 406 stroke-dasharray: 4 2
  concept_choreography -->|has type| type_pattern
  linkStyle 407 stroke-dasharray: 4 2
  concept_circuit_breaker -->|has type| type_pattern
  linkStyle 408 stroke-dasharray: 4 2
  concept_circular_dependency -->|has type| type_anti_pattern
  linkStyle 409 stroke-dasharray: 4 2
  concept_claim_check -->|has type| type_pattern
  linkStyle 410 stroke-dasharray: 4 2
  concept_command -->|has type| type_pattern
  linkStyle 411 stroke-dasharray: 4 2
  concept_competing_consumers -->|has type| type_pattern
  linkStyle 412 stroke-dasharray: 4 2
  concept_component -->|has type| type_pattern
  linkStyle 413 stroke-dasharray: 4 2
  concept_component_slot -->|has type| type_pattern
  linkStyle 414 stroke-dasharray: 4 2
  concept_composite -->|has type| type_pattern
  linkStyle 415 stroke-dasharray: 4 2
  concept_config_management -->|has type| type_pattern
  linkStyle 416 stroke-dasharray: 4 2
  concept_config_sprawl -->|has type| type_anti_pattern
  linkStyle 417 stroke-dasharray: 4 2
  concept_connection_pooling -->|has type| type_pattern
  linkStyle 418 stroke-dasharray: 4 2
  concept_content_negotiation -->|has type| type_pattern
  linkStyle 419 stroke-dasharray: 4 2
  concept_contract_testing -->|has type| type_pattern
  linkStyle 420 stroke-dasharray: 4 2
  concept_conversation_thread -->|has type| type_pattern
  linkStyle 421 stroke-dasharray: 4 2
  concept_copy_paste_programming -->|has type| type_anti_pattern
  linkStyle 422 stroke-dasharray: 4 2
  concept_correlation_id -->|has type| type_pattern
  linkStyle 423 stroke-dasharray: 4 2
  concept_cors -->|has type| type_pattern
  linkStyle 424 stroke-dasharray: 4 2
  concept_cqrs -->|has type| type_pattern
  linkStyle 425 stroke-dasharray: 4 2
  concept_data_mapper -->|has type| type_pattern
  linkStyle 426 stroke-dasharray: 4 2
  concept_data_pipeline -->|has type| type_flow_shape
  linkStyle 427 stroke-dasharray: 4 2
  concept_database_migration -->|has type| type_pattern
  linkStyle 428 stroke-dasharray: 4 2
  concept_ddd -->|has type| type_pattern
  linkStyle 429 stroke-dasharray: 4 2
  concept_dead_letter -->|has type| type_pattern
  linkStyle 430 stroke-dasharray: 4 2
  concept_deadlock -->|has type| type_anti_pattern
  linkStyle 431 stroke-dasharray: 4 2
  concept_decorator -->|has type| type_pattern
  linkStyle 432 stroke-dasharray: 4 2
  concept_deep_nesting -->|has type| type_anti_pattern
  linkStyle 433 stroke-dasharray: 4 2
  concept_dependency_injection -->|has type| type_pattern
  linkStyle 434 stroke-dasharray: 4 2
  concept_distributed_lock -->|has type| type_pattern
  linkStyle 435 stroke-dasharray: 4 2
  concept_distributed_monolith -->|has type| type_anti_pattern
  linkStyle 436 stroke-dasharray: 4 2
  concept_distributed_tracing -->|has type| type_pattern
  linkStyle 437 stroke-dasharray: 4 2
  concept_dual_writes -->|has type| type_anti_pattern
  linkStyle 438 stroke-dasharray: 4 2
  concept_entity_component_system -->|has type| type_pattern
  linkStyle 439 stroke-dasharray: 4 2
  concept_environment_parity_gap -->|has type| type_anti_pattern
  linkStyle 440 stroke-dasharray: 4 2
  concept_error_boundary -->|has type| type_pattern
  linkStyle 441 stroke-dasharray: 4 2
  concept_error_code_returns -->|has type| type_anti_pattern
  linkStyle 442 stroke-dasharray: 4 2
  concept_etl -->|has type| type_pattern
  linkStyle 443 stroke-dasharray: 4 2
  concept_event_carried_state -->|has type| type_flow_shape
  linkStyle 444 stroke-dasharray: 4 2
  concept_event_driven -->|has type| type_pattern
  linkStyle 445 stroke-dasharray: 4 2
  concept_event_log -->|has type| type_domain_model
  linkStyle 446 stroke-dasharray: 4 2
  concept_event_notification -->|has type| type_flow_shape
  linkStyle 447 stroke-dasharray: 4 2
  concept_event_sourcing -->|has type| type_pattern
  linkStyle 448 stroke-dasharray: 4 2
  concept_experiment_framework -->|has type| type_pattern
  linkStyle 449 stroke-dasharray: 4 2
  concept_facade -->|has type| type_pattern
  linkStyle 450 stroke-dasharray: 4 2
  concept_factory -->|has type| type_pattern
  linkStyle 451 stroke-dasharray: 4 2
  concept_failure_cascade -->|has type| type_flow_shape
  linkStyle 452 stroke-dasharray: 4 2
  concept_fan_in -->|has type| type_flow_shape
  linkStyle 453 stroke-dasharray: 4 2
  concept_fan_out -->|has type| type_flow_shape
  linkStyle 454 stroke-dasharray: 4 2
  concept_feature_envy -->|has type| type_anti_pattern
  linkStyle 455 stroke-dasharray: 4 2
  concept_feature_flag -->|has type| type_pattern
  linkStyle 456 stroke-dasharray: 4 2
  concept_feature_store -->|has type| type_pattern
  linkStyle 457 stroke-dasharray: 4 2
  concept_fire_and_forget -->|has type| type_anti_pattern
  linkStyle 458 stroke-dasharray: 4 2
  concept_fixture_builder -->|has type| type_pattern
  linkStyle 459 stroke-dasharray: 4 2
  concept_flaky_tests -->|has type| type_anti_pattern
  linkStyle 460 stroke-dasharray: 4 2
  concept_flux -->|has type| type_pattern
  linkStyle 461 stroke-dasharray: 4 2
  concept_flyweight -->|has type| type_pattern
  linkStyle 462 stroke-dasharray: 4 2
  concept_form_binding -->|has type| type_pattern
  linkStyle 463 stroke-dasharray: 4 2
  concept_future_promise -->|has type| type_pattern
  linkStyle 464 stroke-dasharray: 4 2
  concept_game_loop -->|has type| type_pattern
  linkStyle 465 stroke-dasharray: 4 2
  concept_gateway_backends -->|has type| type_structure_shape
  linkStyle 466 stroke-dasharray: 4 2
  concept_gitops -->|has type| type_pattern
  linkStyle 467 stroke-dasharray: 4 2
  concept_god_endpoint -->|has type| type_anti_pattern
  linkStyle 468 stroke-dasharray: 4 2
  concept_god_object -->|has type| type_anti_pattern
  linkStyle 469 stroke-dasharray: 4 2
  concept_golden_hammer -->|has type| type_anti_pattern
  linkStyle 470 stroke-dasharray: 4 2
  concept_graceful_degradation -->|has type| type_pattern
  linkStyle 471 stroke-dasharray: 4 2
  concept_graph -->|has type| type_pattern
  linkStyle 472 stroke-dasharray: 4 2
  concept_graphql -->|has type| type_pattern
  linkStyle 473 stroke-dasharray: 4 2
  concept_grpc -->|has type| type_pattern
  linkStyle 474 stroke-dasharray: 4 2
  concept_hardcoded_credentials -->|has type| type_anti_pattern
  linkStyle 475 stroke-dasharray: 4 2
  concept_hardcoded_urls -->|has type| type_anti_pattern
  linkStyle 476 stroke-dasharray: 4 2
  concept_health_check -->|has type| type_pattern
  linkStyle 477 stroke-dasharray: 4 2
  concept_hexagonal -->|has type| type_pattern
  linkStyle 478 stroke-dasharray: 4 2
  concept_hidden_side_effects -->|has type| type_anti_pattern
  linkStyle 479 stroke-dasharray: 4 2
  concept_hydration -->|has type| type_pattern
  linkStyle 480 stroke-dasharray: 4 2
  concept_ice_cream_cone -->|has type| type_anti_pattern
  linkStyle 481 stroke-dasharray: 4 2
  concept_idempotent_consumer -->|has type| type_pattern
  linkStyle 482 stroke-dasharray: 4 2
  concept_immutable_infra -->|has type| type_pattern
  linkStyle 483 stroke-dasharray: 4 2
  concept_inbox -->|has type| type_unknown
  linkStyle 484 stroke-dasharray: 4 2
  concept_inconsistent_naming -->|has type| type_anti_pattern
  linkStyle 485 stroke-dasharray: 4 2
  concept_infrastructure_as_code -->|has type| type_pattern
  linkStyle 486 stroke-dasharray: 4 2
  concept_input_validation -->|has type| type_pattern
  linkStyle 487 stroke-dasharray: 4 2
  concept_insecure_deserialization -->|has type| type_anti_pattern
  linkStyle 488 stroke-dasharray: 4 2
  concept_intermediate_representation -->|has type| type_pattern
  linkStyle 489 stroke-dasharray: 4 2
  concept_iterator -->|has type| type_pattern
  linkStyle 490 stroke-dasharray: 4 2
  concept_key_value_model -->|has type| type_domain_model
  linkStyle 491 stroke-dasharray: 4 2
  concept_lava_flow -->|has type| type_anti_pattern
  linkStyle 492 stroke-dasharray: 4 2
  concept_layered -->|has type| type_structure_shape
  linkStyle 493 stroke-dasharray: 4 2
  concept_lazy_loading -->|has type| type_pattern
  linkStyle 494 stroke-dasharray: 4 2
  concept_leader_election -->|has type| type_pattern
  linkStyle 495 stroke-dasharray: 4 2
  concept_leaky_abstraction -->|has type| type_anti_pattern
  linkStyle 496 stroke-dasharray: 4 2
  concept_ledger -->|has type| type_pattern
  linkStyle 497 stroke-dasharray: 4 2
  concept_lexer_parser -->|has type| type_pattern
  linkStyle 498 stroke-dasharray: 4 2
  concept_log_and_throw -->|has type| type_anti_pattern
  linkStyle 499 stroke-dasharray: 4 2
  concept_log_spam -->|has type| type_anti_pattern
  linkStyle 500 stroke-dasharray: 4 2
  concept_long_polling -->|has type| type_pattern
  linkStyle 501 stroke-dasharray: 4 2
  concept_long_transactions -->|has type| type_anti_pattern
  linkStyle 502 stroke-dasharray: 4 2
  concept_lru_cache -->|has type| type_pattern
  linkStyle 503 stroke-dasharray: 4 2
  concept_magic_numbers -->|has type| type_anti_pattern
  linkStyle 504 stroke-dasharray: 4 2
  concept_mapreduce -->|has type| type_pattern
  linkStyle 505 stroke-dasharray: 4 2
  concept_materialized_view -->|has type| type_pattern
  linkStyle 506 stroke-dasharray: 4 2
  concept_mediator -->|has type| type_pattern
  linkStyle 507 stroke-dasharray: 4 2
  concept_memento -->|has type| type_pattern
  linkStyle 508 stroke-dasharray: 4 2
  concept_memory_leak -->|has type| type_anti_pattern
  linkStyle 509 stroke-dasharray: 4 2
  concept_message_queue -->|has type| type_pattern
  linkStyle 510 stroke-dasharray: 4 2
  concept_metric_cardinality_explosion -->|has type| type_anti_pattern
  linkStyle 511 stroke-dasharray: 4 2
  concept_metrics_instrumentation -->|has type| type_pattern
  linkStyle 512 stroke-dasharray: 4 2
  concept_micro_frontend -->|has type| type_pattern
  linkStyle 513 stroke-dasharray: 4 2
  concept_microservices -->|has type| type_pattern
  linkStyle 514 stroke-dasharray: 4 2
  concept_middleware -->|has type| type_pattern
  linkStyle 515 stroke-dasharray: 4 2
  concept_misleading_names -->|has type| type_anti_pattern
  linkStyle 516 stroke-dasharray: 4 2
  concept_missing_log_context -->|has type| type_anti_pattern
  linkStyle 517 stroke-dasharray: 4 2
  concept_model_registry -->|has type| type_pattern
  linkStyle 518 stroke-dasharray: 4 2
  concept_modular_monolith -->|has type| type_pattern
  linkStyle 519 stroke-dasharray: 4 2
  concept_monad -->|has type| type_pattern
  linkStyle 520 stroke-dasharray: 4 2
  concept_mtls -->|has type| type_pattern
  linkStyle 521 stroke-dasharray: 4 2
  concept_multi_tenant -->|has type| type_pattern
  linkStyle 522 stroke-dasharray: 4 2
  concept_mvc -->|has type| type_pattern
  linkStyle 523 stroke-dasharray: 4 2
  concept_mvvm -->|has type| type_pattern
  linkStyle 524 stroke-dasharray: 4 2
  concept_n_plus_one -->|has type| type_anti_pattern
  linkStyle 525 stroke-dasharray: 4 2
  concept_null_object -->|has type| type_pattern
  linkStyle 526 stroke-dasharray: 4 2
  concept_oauth_oidc -->|has type| type_pattern
  linkStyle 527 stroke-dasharray: 4 2
  concept_object_pool -->|has type| type_pattern
  linkStyle 528 stroke-dasharray: 4 2
  concept_observer -->|has type| type_pattern
  linkStyle 529 stroke-dasharray: 4 2
  concept_optimistic_locking -->|has type| type_pattern
  linkStyle 530 stroke-dasharray: 4 2
  concept_optimistic_update -->|has type| type_pattern
  linkStyle 531 stroke-dasharray: 4 2
  concept_outbox -->|has type| type_pattern
  linkStyle 532 stroke-dasharray: 4 2
  concept_over_under_fetching -->|has type| type_anti_pattern
  linkStyle 533 stroke-dasharray: 4 2
  concept_pagination -->|has type| type_pattern
  linkStyle 534 stroke-dasharray: 4 2
  concept_pipeline_filter -->|has type| type_pattern
  linkStyle 535 stroke-dasharray: 4 2
  concept_pipeline_stages -->|has type| type_structure_shape
  linkStyle 536 stroke-dasharray: 4 2
  concept_plugin -->|has type| type_pattern
  linkStyle 537 stroke-dasharray: 4 2
  concept_plugin_host -->|has type| type_structure_shape
  linkStyle 538 stroke-dasharray: 4 2
  concept_pokemon_exception -->|has type| type_anti_pattern
  linkStyle 539 stroke-dasharray: 4 2
  concept_polling_flow -->|has type| type_flow_shape
  linkStyle 540 stroke-dasharray: 4 2
  concept_premature_optimization -->|has type| type_anti_pattern
  linkStyle 541 stroke-dasharray: 4 2
  concept_primitive_obsession -->|has type| type_anti_pattern
  linkStyle 542 stroke-dasharray: 4 2
  concept_producer_consumer -->|has type| type_pattern
  linkStyle 543 stroke-dasharray: 4 2
  concept_prop_drilling -->|has type| type_anti_pattern
  linkStyle 544 stroke-dasharray: 4 2
  concept_property_graph -->|has type| type_domain_model
  linkStyle 545 stroke-dasharray: 4 2
  concept_property_testing -->|has type| type_pattern
  linkStyle 546 stroke-dasharray: 4 2
  concept_prototype -->|has type| type_pattern
  linkStyle 547 stroke-dasharray: 4 2
  concept_proxy -->|has type| type_pattern
  linkStyle 548 stroke-dasharray: 4 2
  concept_pub_sub -->|has type| type_pattern
  linkStyle 549 stroke-dasharray: 4 2
  concept_race_condition -->|has type| type_anti_pattern
  linkStyle 550 stroke-dasharray: 4 2
  concept_rate_limiting -->|has type| type_pattern
  linkStyle 551 stroke-dasharray: 4 2
  concept_rbac -->|has type| type_pattern
  linkStyle 552 stroke-dasharray: 4 2
  concept_reactive_store -->|has type| type_pattern
  linkStyle 553 stroke-dasharray: 4 2
  concept_reactor -->|has type| type_pattern
  linkStyle 554 stroke-dasharray: 4 2
  concept_read_through -->|has type| type_pattern
  linkStyle 555 stroke-dasharray: 4 2
  concept_read_write_lock -->|has type| type_pattern
  linkStyle 556 stroke-dasharray: 4 2
  concept_refresh_ahead -->|has type| type_pattern
  linkStyle 557 stroke-dasharray: 4 2
  concept_registry_model -->|has type| type_domain_model
  linkStyle 558 stroke-dasharray: 4 2
  concept_reinventing_the_wheel -->|has type| type_anti_pattern
  linkStyle 559 stroke-dasharray: 4 2
  concept_repository -->|has type| type_pattern
  linkStyle 560 stroke-dasharray: 4 2
  concept_request_path -->|has type| type_flow_shape
  linkStyle 561 stroke-dasharray: 4 2
  concept_request_reply -->|has type| type_pattern
  linkStyle 562 stroke-dasharray: 4 2
  concept_rest -->|has type| type_pattern
  linkStyle 563 stroke-dasharray: 4 2
  concept_result_type -->|has type| type_pattern
  linkStyle 564 stroke-dasharray: 4 2
  concept_retry -->|has type| type_pattern
  linkStyle 565 stroke-dasharray: 4 2
  concept_ring_buffer -->|has type| type_pattern
  linkStyle 566 stroke-dasharray: 4 2
  concept_route_guard -->|has type| type_pattern
  linkStyle 567 stroke-dasharray: 4 2
  concept_router -->|has type| type_pattern
  linkStyle 568 stroke-dasharray: 4 2
  concept_rule_engine -->|has type| type_pattern
  linkStyle 569 stroke-dasharray: 4 2
  concept_saga -->|has type| type_pattern
  linkStyle 570 stroke-dasharray: 4 2
  concept_saga_orchestrator -->|has type| type_unknown
  linkStyle 571 stroke-dasharray: 4 2
  concept_scatter_gather -->|has type| type_flow_shape
  linkStyle 572 stroke-dasharray: 4 2
  concept_scheduler -->|has type| type_pattern
  linkStyle 573 stroke-dasharray: 4 2
  concept_schema_on_read -->|has type| type_anti_pattern
  linkStyle 574 stroke-dasharray: 4 2
  concept_search_index -->|has type| type_pattern
  linkStyle 575 stroke-dasharray: 4 2
  concept_secret_management -->|has type| type_pattern
  linkStyle 576 stroke-dasharray: 4 2
  concept_select_star -->|has type| type_anti_pattern
  linkStyle 577 stroke-dasharray: 4 2
  concept_server_prefetch -->|has type| type_pattern
  linkStyle 578 stroke-dasharray: 4 2
  concept_server_route_registration -->|has type| type_pattern
  linkStyle 579 stroke-dasharray: 4 2
  concept_server_sent_events -->|has type| type_pattern
  linkStyle 580 stroke-dasharray: 4 2
  concept_serverless -->|has type| type_pattern
  linkStyle 581 stroke-dasharray: 4 2
  concept_service_discovery -->|has type| type_pattern
  linkStyle 582 stroke-dasharray: 4 2
  concept_service_manager -->|has type| type_pattern
  linkStyle 583 stroke-dasharray: 4 2
  concept_service_mesh -->|has type| type_pattern
  linkStyle 584 stroke-dasharray: 4 2
  concept_session_auth -->|has type| type_pattern
  linkStyle 585 stroke-dasharray: 4 2
  concept_sharding -->|has type| type_pattern
  linkStyle 586 stroke-dasharray: 4 2
  concept_shotgun_surgery -->|has type| type_anti_pattern
  linkStyle 587 stroke-dasharray: 4 2
  concept_side_effect_hook -->|has type| type_pattern
  linkStyle 588 stroke-dasharray: 4 2
  concept_sidecar -->|has type| type_pattern
  linkStyle 589 stroke-dasharray: 4 2
  concept_sidecar_mesh -->|has type| type_structure_shape
  linkStyle 590 stroke-dasharray: 4 2
  concept_singleton -->|has type| type_pattern
  linkStyle 591 stroke-dasharray: 4 2
  concept_snapshot_testing -->|has type| type_pattern
  linkStyle 592 stroke-dasharray: 4 2
  concept_snowflake_server -->|has type| type_anti_pattern
  linkStyle 593 stroke-dasharray: 4 2
  concept_social_graph -->|has type| type_domain_model
  linkStyle 594 stroke-dasharray: 4 2
  concept_soft_delete -->|has type| type_pattern
  linkStyle 595 stroke-dasharray: 4 2
  concept_spaghetti_code -->|has type| type_anti_pattern
  linkStyle 596 stroke-dasharray: 4 2
  concept_spatial -->|has type| type_pattern
  linkStyle 597 stroke-dasharray: 4 2
  concept_spatial_partitioning -->|has type| type_pattern
  linkStyle 598 stroke-dasharray: 4 2
  concept_specification -->|has type| type_pattern
  linkStyle 599 stroke-dasharray: 4 2
  concept_sql_injection -->|has type| type_anti_pattern
  linkStyle 600 stroke-dasharray: 4 2
  concept_state_machine -->|has type| type_pattern
  linkStyle 601 stroke-dasharray: 4 2
  concept_strangler_fig -->|has type| type_pattern
  linkStyle 602 stroke-dasharray: 4 2
  concept_strategy -->|has type| type_pattern
  linkStyle 603 stroke-dasharray: 4 2
  concept_stream_to_store -->|has type| type_pattern
  linkStyle 604 stroke-dasharray: 4 2
  concept_streaming_flow -->|has type| type_flow_shape
  linkStyle 605 stroke-dasharray: 4 2
  concept_stringly_typed -->|has type| type_anti_pattern
  linkStyle 606 stroke-dasharray: 4 2
  concept_structured_logging -->|has type| type_pattern
  linkStyle 607 stroke-dasharray: 4 2
  concept_subscription -->|has type| type_pattern
  linkStyle 608 stroke-dasharray: 4 2
  concept_suspense_boundary -->|has type| type_pattern
  linkStyle 609 stroke-dasharray: 4 2
  concept_swallowed_exception -->|has type| type_anti_pattern
  linkStyle 610 stroke-dasharray: 4 2
  concept_sync_in_async -->|has type| type_anti_pattern
  linkStyle 611 stroke-dasharray: 4 2
  concept_template_method -->|has type| type_pattern
  linkStyle 612 stroke-dasharray: 4 2
  concept_temporal_coupling -->|has type| type_anti_pattern
  linkStyle 613 stroke-dasharray: 4 2
  concept_tenant_isolation -->|has type| type_pattern
  linkStyle 614 stroke-dasharray: 4 2
  concept_tenant_routing -->|has type| type_pattern
  linkStyle 615 stroke-dasharray: 4 2
  concept_tensor -->|has type| type_pattern
  linkStyle 616 stroke-dasharray: 4 2
  concept_test_doubles -->|has type| type_pattern
  linkStyle 617 stroke-dasharray: 4 2
  concept_test_pollution -->|has type| type_anti_pattern
  linkStyle 618 stroke-dasharray: 4 2
  concept_tick_simulation -->|has type| type_pattern
  linkStyle 619 stroke-dasharray: 4 2
  concept_tight_coupling -->|has type| type_anti_pattern
  linkStyle 620 stroke-dasharray: 4 2
  concept_time_series -->|has type| type_pattern
  linkStyle 621 stroke-dasharray: 4 2
  concept_timeout -->|has type| type_pattern
  linkStyle 622 stroke-dasharray: 4 2
  concept_token_auth -->|has type| type_pattern
  linkStyle 623 stroke-dasharray: 4 2
  concept_train_wreck -->|has type| type_anti_pattern
  linkStyle 624 stroke-dasharray: 4 2
  concept_training_pipeline -->|has type| type_pattern
  linkStyle 625 stroke-dasharray: 4 2
  concept_trie -->|has type| type_pattern
  linkStyle 626 stroke-dasharray: 4 2
  concept_unbounded_growth -->|has type| type_anti_pattern
  linkStyle 627 stroke-dasharray: 4 2
  concept_unit_of_work -->|has type| type_pattern
  linkStyle 628 stroke-dasharray: 4 2
  concept_value_object -->|has type| type_pattern
  linkStyle 629 stroke-dasharray: 4 2
  concept_versioned_document -->|has type| type_pattern
  linkStyle 630 stroke-dasharray: 4 2
  concept_visitor -->|has type| type_pattern
  linkStyle 631 stroke-dasharray: 4 2
  concept_webhook -->|has type| type_pattern
  linkStyle 632 stroke-dasharray: 4 2
  concept_websocket -->|has type| type_pattern
  linkStyle 633 stroke-dasharray: 4 2
  concept_worker_pool -->|has type| type_pattern
  linkStyle 634 stroke-dasharray: 4 2
  concept_workflow_engine -->|has type| type_pattern
  linkStyle 635 stroke-dasharray: 4 2
  concept_workflow_state_machine -->|has type| type_domain_model
  linkStyle 636 stroke-dasharray: 4 2
  concept_write_behind -->|has type| type_pattern
  linkStyle 637 stroke-dasharray: 4 2
  framework_fastapi -->|implements| concept_rest
  concept_property_graph -->|is a| concept_graph
  concept_social_graph -->|is a| concept_graph
  concept_component_slot -->|part of| concept_component
  concept_event_carried_state -->|part of| concept_event_driven
  concept_event_notification -->|part of| concept_event_driven
  concept_workflow_engine -->|preferred over| concept_workflow_state_machine
  concept_block_content -->|references| concept_component
  linkStyle 645 stroke-dasharray: 4 2
  concept_block_content -->|references| concept_search_index
  linkStyle 646 stroke-dasharray: 4 2
  concept_block_content -->|references| concept_versioned_document
  linkStyle 647 stroke-dasharray: 4 2
  concept_catalog -->|references| concept_rule_engine
  linkStyle 648 stroke-dasharray: 4 2
  concept_catalog -->|references| concept_search_index
  linkStyle 649 stroke-dasharray: 4 2
  concept_catalog -->|references| concept_subscription
  linkStyle 650 stroke-dasharray: 4 2
  concept_conversation_thread -->|references| concept_pagination
  linkStyle 651 stroke-dasharray: 4 2
  concept_conversation_thread -->|references| concept_pub_sub
  linkStyle 652 stroke-dasharray: 4 2
  concept_conversation_thread -->|references| concept_websocket
  linkStyle 653 stroke-dasharray: 4 2
  concept_ledger -->|references| concept_audit_logging
  linkStyle 654 stroke-dasharray: 4 2
  concept_ledger -->|references| concept_event_sourcing
  linkStyle 655 stroke-dasharray: 4 2
  concept_ledger -->|references| concept_saga
  linkStyle 656 stroke-dasharray: 4 2
  concept_multi_tenant -->|references| concept_rate_limiting
  linkStyle 657 stroke-dasharray: 4 2
  concept_multi_tenant -->|references| concept_rbac
  linkStyle 658 stroke-dasharray: 4 2
  concept_multi_tenant -->|references| concept_sharding
  linkStyle 659 stroke-dasharray: 4 2
  concept_request_path -->|references| concept_router
  linkStyle 660 stroke-dasharray: 4 2
  concept_rule_engine -->|references| concept_feature_flag
  linkStyle 661 stroke-dasharray: 4 2
  concept_rule_engine -->|references| concept_specification
  linkStyle 662 stroke-dasharray: 4 2
  concept_rule_engine -->|references| concept_strategy
  linkStyle 663 stroke-dasharray: 4 2
  concept_search_index -->|references| concept_change_data_capture
  linkStyle 664 stroke-dasharray: 4 2
  concept_search_index -->|references| concept_cqrs
  linkStyle 665 stroke-dasharray: 4 2
  concept_search_index -->|references| concept_pagination
  linkStyle 666 stroke-dasharray: 4 2
  concept_spatial -->|references| concept_cache_aside
  linkStyle 667 stroke-dasharray: 4 2
  concept_spatial -->|references| concept_pagination
  linkStyle 668 stroke-dasharray: 4 2
  concept_spatial -->|references| concept_search_index
  linkStyle 669 stroke-dasharray: 4 2
  concept_subscription -->|references| concept_multi_tenant
  linkStyle 670 stroke-dasharray: 4 2
  concept_subscription -->|references| concept_state_machine
  linkStyle 671 stroke-dasharray: 4 2
  concept_subscription -->|references| concept_webhook
  linkStyle 672 stroke-dasharray: 4 2
  concept_tensor -->|references| concept_feature_store
  linkStyle 673 stroke-dasharray: 4 2
  concept_tensor -->|references| concept_model_registry
  linkStyle 674 stroke-dasharray: 4 2
  concept_tensor -->|references| concept_training_pipeline
  linkStyle 675 stroke-dasharray: 4 2
  concept_time_series -->|references| concept_materialized_view
  linkStyle 676 stroke-dasharray: 4 2
  concept_time_series -->|references| concept_metrics_instrumentation
  linkStyle 677 stroke-dasharray: 4 2
  concept_time_series -->|references| concept_stream_to_store
  linkStyle 678 stroke-dasharray: 4 2
  concept_versioned_document -->|references| concept_block_content
  linkStyle 679 stroke-dasharray: 4 2
  concept_versioned_document -->|references| concept_event_sourcing
  linkStyle 680 stroke-dasharray: 4 2
  concept_versioned_document -->|references| concept_optimistic_locking
  linkStyle 681 stroke-dasharray: 4 2
  concept_api_key_auth -->|related to| concept_rate_limiting
  concept_component -->|related to| concept_mvc
  concept_component -->|related to| concept_mvvm
  concept_event_driven -->|related to| concept_pub_sub
  concept_graph -->|related to| concept_pipeline_filter
  concept_graph -->|related to| concept_workflow_engine
  concept_layered -->|related to| concept_middleware
  concept_layered -->|related to| concept_mvc
  concept_layered -->|related to| concept_mvvm
  concept_middleware -->|related to| concept_graphql
  concept_middleware -->|related to| concept_layered
  concept_middleware -->|related to| concept_request_path
  concept_middleware -->|related to| concept_rest
  concept_middleware -->|related to| concept_server_route_registration
  concept_mvc -->|related to| concept_component
  concept_mvc -->|related to| concept_layered
  concept_mvvm -->|related to| concept_component
  concept_mvvm -->|related to| concept_layered
  concept_oauth_oidc -->|related to| concept_rbac
  concept_oauth_oidc -->|related to| concept_session_auth
  concept_oauth_oidc -->|related to| concept_token_auth
  concept_plugin -->|related to| concept_plugin_host
  concept_plugin_host -->|related to| concept_plugin
  concept_property_graph -->|related to| concept_search_index
  concept_request_path -->|related to| concept_middleware
  concept_request_path -->|related to| concept_server_route_registration
  concept_route_guard -->|related to| concept_oauth_oidc
  concept_route_guard -->|related to| concept_rbac
  concept_route_guard -->|related to| concept_router
  concept_route_guard -->|related to| concept_session_auth
  concept_route_guard -->|related to| concept_token_auth
  concept_router -->|related to| concept_route_guard
  concept_router -->|related to| concept_server_route_registration
  concept_server_route_registration -->|related to| concept_graphql
  concept_server_route_registration -->|related to| concept_grpc
  concept_server_route_registration -->|related to| concept_middleware
  concept_server_route_registration -->|related to| concept_request_path
  concept_server_route_registration -->|related to| concept_rest
  concept_session_auth -->|related to| concept_rbac
  concept_session_auth -->|related to| concept_route_guard
  concept_social_graph -->|related to| concept_cache_aside
  concept_social_graph -->|related to| concept_pub_sub
  concept_state_machine -->|related to| concept_workflow_engine
  concept_token_auth -->|related to| concept_oauth_oidc
  concept_token_auth -->|related to| concept_rbac
  concept_token_auth -->|related to| concept_route_guard
  concept_workflow_engine -->|related to| concept_saga
  concept_workflow_engine -->|related to| concept_state_machine
  concept_workflow_state_machine -->|related to| concept_state_machine
  concept_workflow_state_machine -->|related to| concept_workflow_engine
  framework_fastapi -->|related to| concept_hexagonal
  framework_fastapi -->|related to| concept_layered
  framework_fastapi -->|supports| concept_dependency_injection
  framework_fastapi -->|supports| concept_input_validation
  framework_fastapi -->|uses| concept_server_route_registration
  framework_fastapi -->|uses language| language_python
  linkStyle 737 stroke-dasharray: 4 2
```
