---
description: Generated ontology graph index for Augur concepts and frameworks
---
# Ontology Graph

Generated from `memory/concepts/**/*.md`.

Authored relationship metadata comes from concept frontmatter and framework semantics.
Framework-authored edges take precedence over inferred framework hints, and concept-authored edges take precedence over prose-link references.
Plain prose links are kept as low-confidence inferred `references` edges for maintenance rather than treated as equal authority.

## Maintenance

- Authored edges: `108`
- Inferred edges: `1468`
- Low-confidence inferred references needing review: `762`

Top low-confidence inferred references:
- `framework:django` `commonly_implies` `concept:active-record`
- `framework:fastapi` `commonly_implies` `concept:repository`
- `framework:laravel` `commonly_implies` `concept:active-record`
- `framework:rails` `commonly_implies` `concept:active-record`
- `concept:abstract-factory` `references` `concept:bridge`
- `concept:abstract-factory` `references` `concept:builder`
- `concept:abstract-factory` `references` `concept:factory`
- `concept:active-record` `references` `concept:data-mapper`
- `concept:active-record` `references` `concept:repository`
- `concept:actor-model` `references` `concept:pub-sub`
- `concept:actor-model` `references` `concept:state-machine`
- `concept:actor-model` `references` `concept:worker-pool`

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
  abstraction_networking["networking"]
  abstraction_observability["observability"]
  abstraction_realtime["realtime"]
  abstraction_resilience["resilience"]
  abstraction_search["search"]
  abstraction_security["security"]
  abstraction_social["social"]
  abstraction_temporal["temporal"]
  abstraction_testing["testing"]
  concept_abstract_factory["Explanation"]
  concept_active_record["Explanation"]
  concept_actor_model["Explanation"]
  concept_adapter["Explanation"]
  concept_aggregate["Explanation"]
  concept_anemic_domain_model["Explanation"]
  concept_anti_corruption_layer["Explanation"]
  concept_api_gateway["Explanation"]
  concept_api_key_auth["Explanation"]
  concept_ast["Explanation"]
  concept_at_least_once_delivery["Explanation"]
  concept_audit_logging["Explanation"]
  concept_backpressure["Explanation"]
  concept_batch_loader["Explanation"]
  concept_batch_processing["Explanation"]
  concept_bff["Explanation"]
  concept_big_ball_of_mud["Explanation"]
  concept_block_content["Explanation"]
  concept_bloom_filter["Explanation"]
  concept_blue_green["Explanation"]
  concept_boolean_blindness["Explanation"]
  concept_bounded_context["Explanation"]
  concept_breaking_changes["Explanation"]
  concept_bridge["Explanation"]
  concept_builder["Explanation"]
  concept_bulkhead["Explanation"]
  concept_busy_waiting["Explanation"]
  concept_cache_aside["Explanation"]
  concept_cache_stampede_prevention["Explanation"]
  concept_callback_hell["Explanation"]
  concept_canary["Explanation"]
  concept_cargo_cult["Explanation"]
  concept_catalog["Explanation"]
  concept_cell_based["Explanation"]
  concept_chain_of_responsibility["Explanation"]
  concept_change_data_capture["Explanation"]
  concept_chatty_api["Explanation"]
  concept_choreography["Explanation"]
  concept_circuit_breaker["Explanation"]
  concept_circular_dependency["Explanation"]
  concept_claim_check["Explanation"]
  concept_command["Explanation"]
  concept_competing_consumers["Explanation"]
  concept_component["Explanation"]
  concept_component_slot["Explanation"]
  concept_composite["Explanation"]
  concept_config_management["Explanation"]
  concept_config_sprawl["Explanation"]
  concept_connection_pooling["Explanation"]
  concept_content_negotiation["Explanation"]
  concept_contract_testing["Explanation"]
  concept_control_plane["Explanation"]
  concept_conversation_thread["Explanation"]
  concept_copy_paste_programming["Explanation"]
  concept_correlation_id["Explanation"]
  concept_cors["Explanation"]
  concept_cqrs["Explanation"]
  concept_data_mapper["Explanation"]
  concept_data_pipeline["Explanation"]
  concept_data_plane["Explanation"]
  concept_database_migration["Explanation"]
  concept_database_per_service["Explanation"]
  concept_ddd["Explanation"]
  concept_dead_letter["Explanation"]
  concept_deadlock["Explanation"]
  concept_decorator["Explanation"]
  concept_deep_nesting["Explanation"]
  concept_dependency_injection["Explanation"]
  concept_distributed_lock["Explanation"]
  concept_distributed_monolith["Explanation"]
  concept_distributed_tracing["Explanation"]
  concept_dual_writes["Explanation"]
  concept_entity_component_system["Explanation"]
  concept_environment_parity_gap["Explanation"]
  concept_error_boundary["Explanation"]
  concept_error_code_returns["Explanation"]
  concept_etl["Explanation"]
  concept_event_carried_state["Explanation"]
  concept_event_driven["Explanation"]
  concept_event_log["Explanation"]
  concept_event_notification["Explanation"]
  concept_event_sourcing["Explanation"]
  concept_eventual_consistency["Explanation"]
  concept_exactly_once_semantics["Explanation"]
  concept_experiment_framework["Explanation"]
  concept_facade["Explanation"]
  concept_factory["Explanation"]
  concept_failure_cascade["Explanation"]
  concept_fallback["Explanation"]
  concept_fan_in["Explanation"]
  concept_fan_out["Explanation"]
  concept_feature_envy["Explanation"]
  concept_feature_flag["Explanation"]
  concept_feature_store["Explanation"]
  concept_fire_and_forget["Explanation"]
  concept_fixture_builder["Explanation"]
  concept_flaky_tests["Explanation"]
  concept_flux["Explanation"]
  concept_flyweight["Explanation"]
  concept_form_binding["Explanation"]
  concept_future_promise["Explanation"]
  concept_game_loop["Explanation"]
  concept_gateway_backends["Explanation"]
  concept_gitops["Explanation"]
  concept_god_endpoint["Explanation"]
  concept_god_object["Explanation"]
  concept_golden_hammer["Explanation"]
  concept_graceful_degradation["Explanation"]
  concept_graph["Explanation"]
  concept_graphql["Explanation"]
  concept_grpc["Explanation"]
  concept_hardcoded_credentials["Explanation"]
  concept_hardcoded_urls["Explanation"]
  concept_health_check["Explanation"]
  concept_hexagonal["Explanation"]
  concept_hidden_side_effects["Explanation"]
  concept_hydration["Explanation"]
  concept_ice_cream_cone["Explanation"]
  concept_idempotent_consumer["Explanation"]
  concept_immutable_infra["Explanation"]
  concept_inbox["Explanation"]
  concept_inconsistent_naming["Explanation"]
  concept_infrastructure_as_code["Explanation"]
  concept_input_validation["Explanation"]
  concept_insecure_deserialization["Explanation"]
  concept_intermediate_representation["Explanation"]
  concept_iterator["Explanation"]
  concept_key_value_model["Explanation"]
  concept_lava_flow["Explanation"]
  concept_layered["Explanation"]
  concept_lazy_loading["Explanation"]
  concept_leader_election["Explanation"]
  concept_leaky_abstraction["Explanation"]
  concept_ledger["Explanation"]
  concept_lexer_parser["Explanation"]
  concept_load_balancer["Explanation"]
  concept_log_and_throw["Explanation"]
  concept_log_spam["Explanation"]
  concept_long_polling["Explanation"]
  concept_long_transactions["Explanation"]
  concept_lru_cache["Explanation"]
  concept_magic_numbers["Explanation"]
  concept_mapreduce["Explanation"]
  concept_materialized_view["Explanation"]
  concept_mediator["Explanation"]
  concept_memento["Explanation"]
  concept_memory_leak["Explanation"]
  concept_message_queue["Explanation"]
  concept_metric_cardinality_explosion["Explanation"]
  concept_metrics_instrumentation["Explanation"]
  concept_micro_frontend["Explanation"]
  concept_microservices["Explanation"]
  concept_middleware["Explanation"]
  concept_misleading_names["Explanation"]
  concept_missing_log_context["Explanation"]
  concept_model_registry["Explanation"]
  concept_modular_monolith["Explanation"]
  concept_monad["Explanation"]
  concept_mtls["Explanation"]
  concept_multi_tenant["Explanation"]
  concept_mvc["Explanation"]
  concept_mvvm["Explanation"]
  concept_n_plus_one["Explanation"]
  concept_null_object["Explanation"]
  concept_oauth_oidc["Explanation"]
  concept_object_pool["Explanation"]
  concept_observer["Explanation"]
  concept_optimistic_locking["Explanation"]
  concept_optimistic_update["Explanation"]
  concept_orchestration["Explanation"]
  concept_outbox["Explanation"]
  concept_over_under_fetching["Explanation"]
  concept_pagination["Explanation"]
  concept_pipeline_filter["Explanation"]
  concept_pipeline_stages["Explanation"]
  concept_plugin["Explanation"]
  concept_plugin_host["Explanation"]
  concept_pokemon_exception["Explanation"]
  concept_polling_flow["Explanation"]
  concept_premature_optimization["Explanation"]
  concept_primitive_obsession["Explanation"]
  concept_producer_consumer["Explanation"]
  concept_prop_drilling["Explanation"]
  concept_property_graph["Explanation"]
  concept_property_testing["Explanation"]
  concept_prototype["Explanation"]
  concept_proxy["Explanation"]
  concept_pub_sub["Explanation"]
  concept_query_object["Explanation"]
  concept_race_condition["Explanation"]
  concept_rate_limiting["Explanation"]
  concept_rbac["Explanation"]
  concept_reactive_store["Explanation"]
  concept_reactor["Explanation"]
  concept_read_through["Explanation"]
  concept_read_write_lock["Explanation"]
  concept_refresh_ahead["Explanation"]
  concept_registry_model["Explanation"]
  concept_reinventing_the_wheel["Explanation"]
  concept_repository["Explanation"]
  concept_request_path["Explanation"]
  concept_request_reply["Explanation"]
  concept_rest["Explanation"]
  concept_result_type["Explanation"]
  concept_retry["Explanation"]
  concept_ring_buffer["Explanation"]
  concept_route_guard["Explanation"]
  concept_router["Explanation"]
  concept_rule_engine["Explanation"]
  concept_saga["Explanation"]
  concept_saga_orchestrator["Explanation"]
  concept_scatter_gather["Explanation"]
  concept_scheduler["Explanation"]
  concept_schema_on_read["Explanation"]
  concept_schema_registry["Explanation"]
  concept_search_index["Explanation"]
  concept_secret_management["Explanation"]
  concept_select_star["Explanation"]
  concept_server_prefetch["Explanation"]
  concept_server_route_registration["Explanation"]
  concept_server_sent_events["Explanation"]
  concept_serverless["Explanation"]
  concept_service_discovery["Explanation"]
  concept_service_manager["Explanation"]
  concept_service_mesh["Explanation"]
  concept_session_auth["Explanation"]
  concept_sharding["Explanation"]
  concept_shared_database["Explanation"]
  concept_shotgun_surgery["Explanation"]
  concept_side_effect_hook["Explanation"]
  concept_sidecar["Explanation"]
  concept_sidecar_mesh["Explanation"]
  concept_singleton["Explanation"]
  concept_snapshot_testing["Explanation"]
  concept_snowflake_server["Explanation"]
  concept_social_graph["Explanation"]
  concept_soft_delete["Explanation"]
  concept_spaghetti_code["Explanation"]
  concept_spatial["Explanation"]
  concept_spatial_partitioning["Explanation"]
  concept_specification["Explanation"]
  concept_sql_injection["Explanation"]
  concept_state_machine["Explanation"]
  concept_strangler_fig["Explanation"]
  concept_strategy["Explanation"]
  concept_stream_processing["Explanation"]
  concept_stream_to_store["Explanation"]
  concept_streaming_flow["Explanation"]
  concept_stringly_typed["Explanation"]
  concept_structured_logging["Explanation"]
  concept_subscription["Explanation"]
  concept_suspense_boundary["Explanation"]
  concept_swallowed_exception["Explanation"]
  concept_sync_in_async["Explanation"]
  concept_template_method["Explanation"]
  concept_temporal_coupling["Explanation"]
  concept_tenant_isolation["Explanation"]
  concept_tenant_routing["Explanation"]
  concept_tensor["Explanation"]
  concept_test_doubles["Explanation"]
  concept_test_pollution["Explanation"]
  concept_tick_simulation["Explanation"]
  concept_tight_coupling["Explanation"]
  concept_time_series["Explanation"]
  concept_timeout["Explanation"]
  concept_token_auth["Explanation"]
  concept_train_wreck["Explanation"]
  concept_training_pipeline["Explanation"]
  concept_trie["Explanation"]
  concept_unbounded_growth["Explanation"]
  concept_unit_of_work["Explanation"]
  concept_value_object["Explanation"]
  concept_versioned_document["Explanation"]
  concept_visitor["Explanation"]
  concept_webhook["Explanation"]
  concept_websocket["Explanation"]
  concept_worker_pool["Explanation"]
  concept_workflow_engine["Explanation"]
  concept_workflow_state_machine["Explanation"]
  concept_write_behind["Explanation"]
  type_anti_pattern["anti-pattern"]
  type_domain_model["domain-model"]
  type_flow_shape["flow-shape"]
  type_pattern["pattern"]
  type_structure_shape["structure-shape"]
  type_unknown["unknown"]
  framework_actix_web["Explanation"]
  framework_aiohttp["Explanation"]
  framework_angular["Explanation"]
  framework_aspnet_controllers["Explanation"]
  framework_aspnet_minimal["Explanation"]
  framework_axum["Explanation"]
  framework_chi["Explanation"]
  framework_django["Explanation"]
  framework_echo["Explanation"]
  framework_elysia["Explanation"]
  framework_express["Explanation"]
  framework_fastapi["Explanation"]
  framework_fastify["Explanation"]
  framework_fiber["Explanation"]
  framework_flask["Explanation"]
  framework_gin["Explanation"]
  framework_grape["Explanation"]
  framework_hono["Explanation"]
  framework_koa["Explanation"]
  framework_ktor["Explanation"]
  framework_laravel["Explanation"]
  framework_nestjs["Explanation"]
  framework_net_http["Explanation"]
  framework_nextjs["Explanation"]
  framework_phoenix["Explanation"]
  framework_quarkus["Explanation"]
  framework_rails["Explanation"]
  framework_react["Explanation"]
  framework_sinatra["Explanation"]
  framework_slim["Explanation"]
  framework_spring["Explanation"]
  framework_starlette["Explanation"]
  framework_sveltekit["Explanation"]
  framework_symfony["Explanation"]
  framework_vapor["Explanation"]
  framework_vue["Explanation"]
  language_csharp["csharp"]
  language_elixir["elixir"]
  language_go["go"]
  language_java["java"]
  language_kotlin["kotlin"]
  language_php["php"]
  language_python["python"]
  language_ruby["ruby"]
  language_rust["rust"]
  language_swift["swift"]
  language_typescript["typescript"]
  classDef status_0 fill:#d7f5d1,stroke:#2f6b2f,stroke-width:2px
  classDef status_1 fill:#e7f0ff,stroke:#315c99,stroke-width:1px
  classDef status_2 fill:#fff1cf,stroke:#9b6a00,stroke-width:1px
  classDef status_3 fill:#f5e1f7,stroke:#7d3c8c,stroke-width:1px,stroke-dasharray: 4 2
  classDef status_4 fill:#eeeeee,stroke:#777777,stroke-width:1px
  class concept_abstract_factory status_0
  class concept_active_record status_0
  class concept_actor_model status_0
  class concept_adapter status_0
  class concept_aggregate status_0
  class concept_anemic_domain_model status_2
  class concept_anti_corruption_layer status_0
  class concept_api_gateway status_0
  class concept_api_key_auth status_0
  class concept_ast status_0
  class concept_at_least_once_delivery status_0
  class concept_audit_logging status_0
  class concept_backpressure status_0
  class concept_batch_loader status_0
  class concept_batch_processing status_0
  class concept_bff status_0
  class concept_big_ball_of_mud status_2
  class concept_block_content status_0
  class concept_bloom_filter status_0
  class concept_blue_green status_0
  class concept_boolean_blindness status_2
  class concept_bounded_context status_0
  class concept_breaking_changes status_2
  class concept_bridge status_0
  class concept_builder status_0
  class concept_bulkhead status_0
  class concept_busy_waiting status_2
  class concept_cache_aside status_0
  class concept_cache_stampede_prevention status_0
  class concept_callback_hell status_2
  class concept_canary status_0
  class concept_cargo_cult status_2
  class concept_catalog status_0
  class concept_cell_based status_0
  class concept_chain_of_responsibility status_0
  class concept_change_data_capture status_0
  class concept_chatty_api status_2
  class concept_choreography status_0
  class concept_circuit_breaker status_0
  class concept_circular_dependency status_2
  class concept_claim_check status_0
  class concept_command status_0
  class concept_competing_consumers status_0
  class concept_component status_0
  class concept_component_slot status_1
  class concept_composite status_0
  class concept_config_management status_0
  class concept_config_sprawl status_2
  class concept_connection_pooling status_0
  class concept_content_negotiation status_0
  class concept_contract_testing status_0
  class concept_control_plane status_0
  class concept_conversation_thread status_0
  class concept_copy_paste_programming status_2
  class concept_correlation_id status_0
  class concept_cors status_0
  class concept_cqrs status_0
  class concept_data_mapper status_0
  class concept_data_pipeline status_0
  class concept_data_plane status_0
  class concept_database_migration status_0
  class concept_database_per_service status_0
  class concept_ddd status_0
  class concept_dead_letter status_0
  class concept_deadlock status_2
  class concept_decorator status_0
  class concept_deep_nesting status_2
  class concept_dependency_injection status_0
  class concept_distributed_lock status_0
  class concept_distributed_monolith status_2
  class concept_distributed_tracing status_0
  class concept_dual_writes status_2
  class concept_entity_component_system status_0
  class concept_environment_parity_gap status_2
  class concept_error_boundary status_0
  class concept_error_code_returns status_2
  class concept_etl status_0
  class concept_event_carried_state status_1
  class concept_event_driven status_0
  class concept_event_log status_0
  class concept_event_notification status_1
  class concept_event_sourcing status_0
  class concept_eventual_consistency status_0
  class concept_exactly_once_semantics status_2
  class concept_experiment_framework status_0
  class concept_facade status_0
  class concept_factory status_0
  class concept_failure_cascade status_0
  class concept_fallback status_2
  class concept_fan_in status_0
  class concept_fan_out status_0
  class concept_feature_envy status_2
  class concept_feature_flag status_0
  class concept_feature_store status_0
  class concept_fire_and_forget status_2
  class concept_fixture_builder status_0
  class concept_flaky_tests status_2
  class concept_flux status_0
  class concept_flyweight status_0
  class concept_form_binding status_0
  class concept_future_promise status_0
  class concept_game_loop status_0
  class concept_gateway_backends status_0
  class concept_gitops status_0
  class concept_god_endpoint status_2
  class concept_god_object status_2
  class concept_golden_hammer status_2
  class concept_graceful_degradation status_0
  class concept_graph status_0
  class concept_graphql status_0
  class concept_grpc status_0
  class concept_hardcoded_credentials status_2
  class concept_hardcoded_urls status_2
  class concept_health_check status_0
  class concept_hexagonal status_0
  class concept_hidden_side_effects status_2
  class concept_hydration status_0
  class concept_ice_cream_cone status_2
  class concept_idempotent_consumer status_0
  class concept_immutable_infra status_0
  class concept_inbox status_0
  class concept_inconsistent_naming status_2
  class concept_infrastructure_as_code status_0
  class concept_input_validation status_0
  class concept_insecure_deserialization status_2
  class concept_intermediate_representation status_0
  class concept_iterator status_0
  class concept_key_value_model status_0
  class concept_lava_flow status_2
  class concept_layered status_0
  class concept_lazy_loading status_0
  class concept_leader_election status_0
  class concept_leaky_abstraction status_2
  class concept_ledger status_0
  class concept_lexer_parser status_0
  class concept_load_balancer status_0
  class concept_log_and_throw status_2
  class concept_log_spam status_2
  class concept_long_polling status_0
  class concept_long_transactions status_2
  class concept_lru_cache status_0
  class concept_magic_numbers status_2
  class concept_mapreduce status_0
  class concept_materialized_view status_0
  class concept_mediator status_0
  class concept_memento status_0
  class concept_memory_leak status_2
  class concept_message_queue status_0
  class concept_metric_cardinality_explosion status_2
  class concept_metrics_instrumentation status_0
  class concept_micro_frontend status_0
  class concept_microservices status_0
  class concept_middleware status_0
  class concept_misleading_names status_2
  class concept_missing_log_context status_2
  class concept_model_registry status_0
  class concept_modular_monolith status_0
  class concept_monad status_0
  class concept_mtls status_0
  class concept_multi_tenant status_0
  class concept_mvc status_1
  class concept_mvvm status_1
  class concept_n_plus_one status_2
  class concept_null_object status_0
  class concept_oauth_oidc status_0
  class concept_object_pool status_0
  class concept_observer status_0
  class concept_optimistic_locking status_0
  class concept_optimistic_update status_0
  class concept_orchestration status_0
  class concept_outbox status_0
  class concept_over_under_fetching status_2
  class concept_pagination status_0
  class concept_pipeline_filter status_0
  class concept_pipeline_stages status_0
  class concept_plugin status_0
  class concept_plugin_host status_1
  class concept_pokemon_exception status_2
  class concept_polling_flow status_0
  class concept_premature_optimization status_2
  class concept_primitive_obsession status_2
  class concept_producer_consumer status_0
  class concept_prop_drilling status_2
  class concept_property_graph status_1
  class concept_property_testing status_0
  class concept_prototype status_0
  class concept_proxy status_0
  class concept_pub_sub status_0
  class concept_query_object status_0
  class concept_race_condition status_2
  class concept_rate_limiting status_0
  class concept_rbac status_0
  class concept_reactive_store status_0
  class concept_reactor status_0
  class concept_read_through status_0
  class concept_read_write_lock status_0
  class concept_refresh_ahead status_0
  class concept_registry_model status_0
  class concept_reinventing_the_wheel status_2
  class concept_repository status_0
  class concept_request_path status_2
  class concept_request_reply status_0
  class concept_rest status_0
  class concept_result_type status_0
  class concept_retry status_0
  class concept_ring_buffer status_0
  class concept_route_guard status_1
  class concept_router status_0
  class concept_rule_engine status_0
  class concept_saga status_0
  class concept_saga_orchestrator status_0
  class concept_scatter_gather status_0
  class concept_scheduler status_0
  class concept_schema_on_read status_2
  class concept_schema_registry status_0
  class concept_search_index status_0
  class concept_secret_management status_0
  class concept_select_star status_2
  class concept_server_prefetch status_0
  class concept_server_route_registration status_0
  class concept_server_sent_events status_0
  class concept_serverless status_0
  class concept_service_discovery status_0
  class concept_service_manager status_0
  class concept_service_mesh status_0
  class concept_session_auth status_0
  class concept_sharding status_0
  class concept_shared_database status_0
  class concept_shotgun_surgery status_2
  class concept_side_effect_hook status_0
  class concept_sidecar status_0
  class concept_sidecar_mesh status_0
  class concept_singleton status_0
  class concept_snapshot_testing status_0
  class concept_snowflake_server status_2
  class concept_social_graph status_1
  class concept_soft_delete status_0
  class concept_spaghetti_code status_2
  class concept_spatial status_0
  class concept_spatial_partitioning status_0
  class concept_specification status_0
  class concept_sql_injection status_2
  class concept_state_machine status_0
  class concept_strangler_fig status_0
  class concept_strategy status_0
  class concept_stream_processing status_0
  class concept_stream_to_store status_0
  class concept_streaming_flow status_0
  class concept_stringly_typed status_2
  class concept_structured_logging status_0
  class concept_subscription status_0
  class concept_suspense_boundary status_0
  class concept_swallowed_exception status_2
  class concept_sync_in_async status_2
  class concept_template_method status_0
  class concept_temporal_coupling status_2
  class concept_tenant_isolation status_0
  class concept_tenant_routing status_0
  class concept_tensor status_0
  class concept_test_doubles status_0
  class concept_test_pollution status_2
  class concept_tick_simulation status_0
  class concept_tight_coupling status_2
  class concept_time_series status_0
  class concept_timeout status_0
  class concept_token_auth status_0
  class concept_train_wreck status_2
  class concept_training_pipeline status_0
  class concept_trie status_0
  class concept_unbounded_growth status_2
  class concept_unit_of_work status_0
  class concept_value_object status_0
  class concept_versioned_document status_0
  class concept_visitor status_0
  class concept_webhook status_0
  class concept_websocket status_0
  class concept_worker_pool status_0
  class concept_workflow_engine status_0
  class concept_workflow_state_machine status_3
  class concept_write_behind status_0
  class framework_actix_web status_1
  class framework_aiohttp status_1
  class framework_angular status_0
  class framework_aspnet_controllers status_0
  class framework_aspnet_minimal status_0
  class framework_axum status_0
  class framework_chi status_1
  class framework_django status_0
  class framework_echo status_0
  class framework_elysia status_1
  class framework_express status_0
  class framework_fastapi status_0
  class framework_fastify status_0
  class framework_fiber status_1
  class framework_flask status_0
  class framework_gin status_0
  class framework_grape status_1
  class framework_hono status_1
  class framework_koa status_1
  class framework_ktor status_1
  class framework_laravel status_0
  class framework_nestjs status_0
  class framework_net_http status_2
  class framework_nextjs status_0
  class framework_phoenix status_0
  class framework_quarkus status_1
  class framework_rails status_0
  class framework_react status_2
  class framework_sinatra status_1
  class framework_slim status_1
  class framework_spring status_0
  class framework_starlette status_1
  class framework_sveltekit status_0
  class framework_symfony status_0
  class framework_vapor status_1
  class framework_vue status_2
  framework_django -->|commonly implies| concept_active_record
  linkStyle 0 stroke-dasharray: 4 2
  framework_fastapi -->|commonly implies| concept_repository
  linkStyle 1 stroke-dasharray: 4 2
  framework_laravel -->|commonly implies| concept_active_record
  linkStyle 2 stroke-dasharray: 4 2
  framework_rails -->|commonly implies| concept_active_record
  linkStyle 3 stroke-dasharray: 4 2
  concept_abstract_factory -->|has abstraction| abstraction_design
  linkStyle 4 stroke-dasharray: 4 2
  concept_active_record -->|has abstraction| abstraction_data
  linkStyle 5 stroke-dasharray: 4 2
  concept_active_record -->|has abstraction| abstraction_design
  linkStyle 6 stroke-dasharray: 4 2
  concept_actor_model -->|has abstraction| abstraction_architectural
  linkStyle 7 stroke-dasharray: 4 2
  concept_actor_model -->|has abstraction| abstraction_concurrency
  linkStyle 8 stroke-dasharray: 4 2
  concept_adapter -->|has abstraction| abstraction_design
  linkStyle 9 stroke-dasharray: 4 2
  concept_adapter -->|has abstraction| abstraction_integration
  linkStyle 10 stroke-dasharray: 4 2
  concept_aggregate -->|has abstraction| abstraction_data
  linkStyle 11 stroke-dasharray: 4 2
  concept_aggregate -->|has abstraction| abstraction_design
  linkStyle 12 stroke-dasharray: 4 2
  concept_anti_corruption_layer -->|has abstraction| abstraction_design
  linkStyle 13 stroke-dasharray: 4 2
  concept_anti_corruption_layer -->|has abstraction| abstraction_integration
  linkStyle 14 stroke-dasharray: 4 2
  concept_api_gateway -->|has abstraction| abstraction_infrastructure
  linkStyle 15 stroke-dasharray: 4 2
  concept_api_gateway -->|has abstraction| abstraction_integration
  linkStyle 16 stroke-dasharray: 4 2
  concept_api_gateway -->|has abstraction| abstraction_security
  linkStyle 17 stroke-dasharray: 4 2
  concept_api_key_auth -->|has abstraction| abstraction_security
  linkStyle 18 stroke-dasharray: 4 2
  concept_ast -->|has abstraction| abstraction_compiler
  linkStyle 19 stroke-dasharray: 4 2
  concept_ast -->|has abstraction| abstraction_data
  linkStyle 20 stroke-dasharray: 4 2
  concept_at_least_once_delivery -->|has abstraction| abstraction_messaging
  linkStyle 21 stroke-dasharray: 4 2
  concept_at_least_once_delivery -->|has abstraction| abstraction_resilience
  linkStyle 22 stroke-dasharray: 4 2
  concept_audit_logging -->|has abstraction| abstraction_observability
  linkStyle 23 stroke-dasharray: 4 2
  concept_audit_logging -->|has abstraction| abstraction_security
  linkStyle 24 stroke-dasharray: 4 2
  concept_backpressure -->|has abstraction| abstraction_concurrency
  linkStyle 25 stroke-dasharray: 4 2
  concept_backpressure -->|has abstraction| abstraction_resilience
  linkStyle 26 stroke-dasharray: 4 2
  concept_batch_loader -->|has abstraction| abstraction_data
  linkStyle 27 stroke-dasharray: 4 2
  concept_batch_processing -->|has abstraction| abstraction_data
  linkStyle 28 stroke-dasharray: 4 2
  concept_batch_processing -->|has abstraction| abstraction_lifecycle
  linkStyle 29 stroke-dasharray: 4 2
  concept_bff -->|has abstraction| abstraction_api
  linkStyle 30 stroke-dasharray: 4 2
  concept_bff -->|has abstraction| abstraction_architectural
  linkStyle 31 stroke-dasharray: 4 2
  concept_block_content -->|has abstraction| abstraction_content
  linkStyle 32 stroke-dasharray: 4 2
  concept_block_content -->|has abstraction| abstraction_data
  linkStyle 33 stroke-dasharray: 4 2
  concept_bloom_filter -->|has abstraction| abstraction_data
  linkStyle 34 stroke-dasharray: 4 2
  concept_blue_green -->|has abstraction| abstraction_deployment
  linkStyle 35 stroke-dasharray: 4 2
  concept_bounded_context -->|has abstraction| abstraction_architectural
  linkStyle 36 stroke-dasharray: 4 2
  concept_bounded_context -->|has abstraction| abstraction_design
  linkStyle 37 stroke-dasharray: 4 2
  concept_bridge -->|has abstraction| abstraction_design
  linkStyle 38 stroke-dasharray: 4 2
  concept_builder -->|has abstraction| abstraction_design
  linkStyle 39 stroke-dasharray: 4 2
  concept_bulkhead -->|has abstraction| abstraction_resilience
  linkStyle 40 stroke-dasharray: 4 2
  concept_cache_aside -->|has abstraction| abstraction_data
  linkStyle 41 stroke-dasharray: 4 2
  concept_cache_aside -->|has abstraction| abstraction_resilience
  linkStyle 42 stroke-dasharray: 4 2
  concept_cache_stampede_prevention -->|has abstraction| abstraction_concurrency
  linkStyle 43 stroke-dasharray: 4 2
  concept_cache_stampede_prevention -->|has abstraction| abstraction_data
  linkStyle 44 stroke-dasharray: 4 2
  concept_cache_stampede_prevention -->|has abstraction| abstraction_resilience
  linkStyle 45 stroke-dasharray: 4 2
  concept_canary -->|has abstraction| abstraction_deployment
  linkStyle 46 stroke-dasharray: 4 2
  concept_catalog -->|has abstraction| abstraction_commerce
  linkStyle 47 stroke-dasharray: 4 2
  concept_catalog -->|has abstraction| abstraction_data
  linkStyle 48 stroke-dasharray: 4 2
  concept_cell_based -->|has abstraction| abstraction_architectural
  linkStyle 49 stroke-dasharray: 4 2
  concept_cell_based -->|has abstraction| abstraction_deployment
  linkStyle 50 stroke-dasharray: 4 2
  concept_chain_of_responsibility -->|has abstraction| abstraction_design
  linkStyle 51 stroke-dasharray: 4 2
  concept_change_data_capture -->|has abstraction| abstraction_data
  linkStyle 52 stroke-dasharray: 4 2
  concept_change_data_capture -->|has abstraction| abstraction_integration
  linkStyle 53 stroke-dasharray: 4 2
  concept_choreography -->|has abstraction| abstraction_architectural
  linkStyle 54 stroke-dasharray: 4 2
  concept_choreography -->|has abstraction| abstraction_integration
  linkStyle 55 stroke-dasharray: 4 2
  concept_circuit_breaker -->|has abstraction| abstraction_integration
  linkStyle 56 stroke-dasharray: 4 2
  concept_circuit_breaker -->|has abstraction| abstraction_resilience
  linkStyle 57 stroke-dasharray: 4 2
  concept_claim_check -->|has abstraction| abstraction_integration
  linkStyle 58 stroke-dasharray: 4 2
  concept_claim_check -->|has abstraction| abstraction_messaging
  linkStyle 59 stroke-dasharray: 4 2
  concept_command -->|has abstraction| abstraction_design
  linkStyle 60 stroke-dasharray: 4 2
  concept_competing_consumers -->|has abstraction| abstraction_concurrency
  linkStyle 61 stroke-dasharray: 4 2
  concept_competing_consumers -->|has abstraction| abstraction_messaging
  linkStyle 62 stroke-dasharray: 4 2
  concept_component -->|has abstraction| abstraction_design
  linkStyle 63 stroke-dasharray: 4 2
  concept_component -->|has abstraction| abstraction_frontend
  linkStyle 64 stroke-dasharray: 4 2
  concept_component_slot -->|has abstraction| abstraction_design
  linkStyle 65 stroke-dasharray: 4 2
  concept_component_slot -->|has abstraction| abstraction_frontend
  linkStyle 66 stroke-dasharray: 4 2
  concept_composite -->|has abstraction| abstraction_design
  linkStyle 67 stroke-dasharray: 4 2
  concept_config_management -->|has abstraction| abstraction_infrastructure
  linkStyle 68 stroke-dasharray: 4 2
  concept_config_management -->|has abstraction| abstraction_lifecycle
  linkStyle 69 stroke-dasharray: 4 2
  concept_connection_pooling -->|has abstraction| abstraction_infrastructure
  linkStyle 70 stroke-dasharray: 4 2
  concept_content_negotiation -->|has abstraction| abstraction_api
  linkStyle 71 stroke-dasharray: 4 2
  concept_contract_testing -->|has abstraction| abstraction_integration
  linkStyle 72 stroke-dasharray: 4 2
  concept_contract_testing -->|has abstraction| abstraction_testing
  linkStyle 73 stroke-dasharray: 4 2
  concept_control_plane -->|has abstraction| abstraction_architectural
  linkStyle 74 stroke-dasharray: 4 2
  concept_control_plane -->|has abstraction| abstraction_infrastructure
  linkStyle 75 stroke-dasharray: 4 2
  concept_conversation_thread -->|has abstraction| abstraction_communication
  linkStyle 76 stroke-dasharray: 4 2
  concept_conversation_thread -->|has abstraction| abstraction_data
  linkStyle 77 stroke-dasharray: 4 2
  concept_correlation_id -->|has abstraction| abstraction_integration
  linkStyle 78 stroke-dasharray: 4 2
  concept_correlation_id -->|has abstraction| abstraction_observability
  linkStyle 79 stroke-dasharray: 4 2
  concept_cors -->|has abstraction| abstraction_api
  linkStyle 80 stroke-dasharray: 4 2
  concept_cors -->|has abstraction| abstraction_security
  linkStyle 81 stroke-dasharray: 4 2
  concept_cqrs -->|has abstraction| abstraction_architectural
  linkStyle 82 stroke-dasharray: 4 2
  concept_cqrs -->|has abstraction| abstraction_data
  linkStyle 83 stroke-dasharray: 4 2
  concept_data_mapper -->|has abstraction| abstraction_data
  linkStyle 84 stroke-dasharray: 4 2
  concept_data_mapper -->|has abstraction| abstraction_design
  linkStyle 85 stroke-dasharray: 4 2
  concept_data_pipeline -->|has abstraction| abstraction_data
  linkStyle 86 stroke-dasharray: 4 2
  concept_data_pipeline -->|has abstraction| abstraction_integration
  linkStyle 87 stroke-dasharray: 4 2
  concept_data_plane -->|has abstraction| abstraction_infrastructure
  linkStyle 88 stroke-dasharray: 4 2
  concept_data_plane -->|has abstraction| abstraction_networking
  linkStyle 89 stroke-dasharray: 4 2
  concept_database_migration -->|has abstraction| abstraction_data
  linkStyle 90 stroke-dasharray: 4 2
  concept_database_migration -->|has abstraction| abstraction_lifecycle
  linkStyle 91 stroke-dasharray: 4 2
  concept_database_per_service -->|has abstraction| abstraction_architectural
  linkStyle 92 stroke-dasharray: 4 2
  concept_database_per_service -->|has abstraction| abstraction_data
  linkStyle 93 stroke-dasharray: 4 2
  concept_ddd -->|has abstraction| abstraction_architectural
  linkStyle 94 stroke-dasharray: 4 2
  concept_ddd -->|has abstraction| abstraction_design
  linkStyle 95 stroke-dasharray: 4 2
  concept_dead_letter -->|has abstraction| abstraction_messaging
  linkStyle 96 stroke-dasharray: 4 2
  concept_dead_letter -->|has abstraction| abstraction_resilience
  linkStyle 97 stroke-dasharray: 4 2
  concept_decorator -->|has abstraction| abstraction_design
  linkStyle 98 stroke-dasharray: 4 2
  concept_dependency_injection -->|has abstraction| abstraction_architectural
  linkStyle 99 stroke-dasharray: 4 2
  concept_dependency_injection -->|has abstraction| abstraction_design
  linkStyle 100 stroke-dasharray: 4 2
  concept_distributed_lock -->|has abstraction| abstraction_concurrency
  linkStyle 101 stroke-dasharray: 4 2
  concept_distributed_lock -->|has abstraction| abstraction_resilience
  linkStyle 102 stroke-dasharray: 4 2
  concept_distributed_tracing -->|has abstraction| abstraction_integration
  linkStyle 103 stroke-dasharray: 4 2
  concept_distributed_tracing -->|has abstraction| abstraction_observability
  linkStyle 104 stroke-dasharray: 4 2
  concept_entity_component_system -->|has abstraction| abstraction_architectural
  linkStyle 105 stroke-dasharray: 4 2
  concept_entity_component_system -->|has abstraction| abstraction_realtime
  linkStyle 106 stroke-dasharray: 4 2
  concept_error_boundary -->|has abstraction| abstraction_error_handling
  linkStyle 107 stroke-dasharray: 4 2
  concept_error_boundary -->|has abstraction| abstraction_frontend
  linkStyle 108 stroke-dasharray: 4 2
  concept_etl -->|has abstraction| abstraction_data
  linkStyle 109 stroke-dasharray: 4 2
  concept_event_carried_state -->|has abstraction| abstraction_data
  linkStyle 110 stroke-dasharray: 4 2
  concept_event_carried_state -->|has abstraction| abstraction_messaging
  linkStyle 111 stroke-dasharray: 4 2
  concept_event_driven -->|has abstraction| abstraction_architectural
  linkStyle 112 stroke-dasharray: 4 2
  concept_event_driven -->|has abstraction| abstraction_messaging
  linkStyle 113 stroke-dasharray: 4 2
  concept_event_log -->|has abstraction| abstraction_data
  linkStyle 114 stroke-dasharray: 4 2
  concept_event_log -->|has abstraction| abstraction_messaging
  linkStyle 115 stroke-dasharray: 4 2
  concept_event_notification -->|has abstraction| abstraction_integration
  linkStyle 116 stroke-dasharray: 4 2
  concept_event_notification -->|has abstraction| abstraction_messaging
  linkStyle 117 stroke-dasharray: 4 2
  concept_event_sourcing -->|has abstraction| abstraction_architectural
  linkStyle 118 stroke-dasharray: 4 2
  concept_event_sourcing -->|has abstraction| abstraction_data
  linkStyle 119 stroke-dasharray: 4 2
  concept_eventual_consistency -->|has abstraction| abstraction_data
  linkStyle 120 stroke-dasharray: 4 2
  concept_eventual_consistency -->|has abstraction| abstraction_integration
  linkStyle 121 stroke-dasharray: 4 2
  concept_eventual_consistency -->|has abstraction| abstraction_resilience
  linkStyle 122 stroke-dasharray: 4 2
  concept_exactly_once_semantics -->|has abstraction| abstraction_data
  linkStyle 123 stroke-dasharray: 4 2
  concept_exactly_once_semantics -->|has abstraction| abstraction_messaging
  linkStyle 124 stroke-dasharray: 4 2
  concept_experiment_framework -->|has abstraction| abstraction_deployment
  linkStyle 125 stroke-dasharray: 4 2
  concept_experiment_framework -->|has abstraction| abstraction_ml
  linkStyle 126 stroke-dasharray: 4 2
  concept_facade -->|has abstraction| abstraction_design
  linkStyle 127 stroke-dasharray: 4 2
  concept_factory -->|has abstraction| abstraction_design
  linkStyle 128 stroke-dasharray: 4 2
  concept_failure_cascade -->|has abstraction| abstraction_integration
  linkStyle 129 stroke-dasharray: 4 2
  concept_failure_cascade -->|has abstraction| abstraction_resilience
  linkStyle 130 stroke-dasharray: 4 2
  concept_fallback -->|has abstraction| abstraction_resilience
  linkStyle 131 stroke-dasharray: 4 2
  concept_fan_in -->|has abstraction| abstraction_data
  linkStyle 132 stroke-dasharray: 4 2
  concept_fan_in -->|has abstraction| abstraction_integration
  linkStyle 133 stroke-dasharray: 4 2
  concept_fan_out -->|has abstraction| abstraction_integration
  linkStyle 134 stroke-dasharray: 4 2
  concept_fan_out -->|has abstraction| abstraction_messaging
  linkStyle 135 stroke-dasharray: 4 2
  concept_feature_flag -->|has abstraction| abstraction_deployment
  linkStyle 136 stroke-dasharray: 4 2
  concept_feature_flag -->|has abstraction| abstraction_design
  linkStyle 137 stroke-dasharray: 4 2
  concept_feature_store -->|has abstraction| abstraction_data
  linkStyle 138 stroke-dasharray: 4 2
  concept_feature_store -->|has abstraction| abstraction_ml
  linkStyle 139 stroke-dasharray: 4 2
  concept_fixture_builder -->|has abstraction| abstraction_testing
  linkStyle 140 stroke-dasharray: 4 2
  concept_flux -->|has abstraction| abstraction_architectural
  linkStyle 141 stroke-dasharray: 4 2
  concept_flux -->|has abstraction| abstraction_data
  linkStyle 142 stroke-dasharray: 4 2
  concept_flux -->|has abstraction| abstraction_frontend
  linkStyle 143 stroke-dasharray: 4 2
  concept_flyweight -->|has abstraction| abstraction_design
  linkStyle 144 stroke-dasharray: 4 2
  concept_form_binding -->|has abstraction| abstraction_data
  linkStyle 145 stroke-dasharray: 4 2
  concept_form_binding -->|has abstraction| abstraction_frontend
  linkStyle 146 stroke-dasharray: 4 2
  concept_future_promise -->|has abstraction| abstraction_concurrency
  linkStyle 147 stroke-dasharray: 4 2
  concept_future_promise -->|has abstraction| abstraction_design
  linkStyle 148 stroke-dasharray: 4 2
  concept_game_loop -->|has abstraction| abstraction_lifecycle
  linkStyle 149 stroke-dasharray: 4 2
  concept_game_loop -->|has abstraction| abstraction_realtime
  linkStyle 150 stroke-dasharray: 4 2
  concept_gateway_backends -->|has abstraction| abstraction_api
  linkStyle 151 stroke-dasharray: 4 2
  concept_gateway_backends -->|has abstraction| abstraction_architectural
  linkStyle 152 stroke-dasharray: 4 2
  concept_gitops -->|has abstraction| abstraction_deployment
  linkStyle 153 stroke-dasharray: 4 2
  concept_graceful_degradation -->|has abstraction| abstraction_lifecycle
  linkStyle 154 stroke-dasharray: 4 2
  concept_graceful_degradation -->|has abstraction| abstraction_resilience
  linkStyle 155 stroke-dasharray: 4 2
  concept_graph -->|has abstraction| abstraction_algorithmic
  linkStyle 156 stroke-dasharray: 4 2
  concept_graph -->|has abstraction| abstraction_data
  linkStyle 157 stroke-dasharray: 4 2
  concept_graphql -->|has abstraction| abstraction_api
  linkStyle 158 stroke-dasharray: 4 2
  concept_graphql -->|has abstraction| abstraction_integration
  linkStyle 159 stroke-dasharray: 4 2
  concept_grpc -->|has abstraction| abstraction_api
  linkStyle 160 stroke-dasharray: 4 2
  concept_grpc -->|has abstraction| abstraction_integration
  linkStyle 161 stroke-dasharray: 4 2
  concept_health_check -->|has abstraction| abstraction_lifecycle
  linkStyle 162 stroke-dasharray: 4 2
  concept_health_check -->|has abstraction| abstraction_observability
  linkStyle 163 stroke-dasharray: 4 2
  concept_hexagonal -->|has abstraction| abstraction_architectural
  linkStyle 164 stroke-dasharray: 4 2
  concept_hydration -->|has abstraction| abstraction_data
  linkStyle 165 stroke-dasharray: 4 2
  concept_hydration -->|has abstraction| abstraction_frontend
  linkStyle 166 stroke-dasharray: 4 2
  concept_idempotent_consumer -->|has abstraction| abstraction_data
  linkStyle 167 stroke-dasharray: 4 2
  concept_idempotent_consumer -->|has abstraction| abstraction_messaging
  linkStyle 168 stroke-dasharray: 4 2
  concept_idempotent_consumer -->|has abstraction| abstraction_resilience
  linkStyle 169 stroke-dasharray: 4 2
  concept_immutable_infra -->|has abstraction| abstraction_deployment
  linkStyle 170 stroke-dasharray: 4 2
  concept_immutable_infra -->|has abstraction| abstraction_infrastructure
  linkStyle 171 stroke-dasharray: 4 2
  concept_inbox -->|has abstraction| abstraction_data
  linkStyle 172 stroke-dasharray: 4 2
  concept_inbox -->|has abstraction| abstraction_messaging
  linkStyle 173 stroke-dasharray: 4 2
  concept_inbox -->|has abstraction| abstraction_resilience
  linkStyle 174 stroke-dasharray: 4 2
  concept_infrastructure_as_code -->|has abstraction| abstraction_deployment
  linkStyle 175 stroke-dasharray: 4 2
  concept_infrastructure_as_code -->|has abstraction| abstraction_infrastructure
  linkStyle 176 stroke-dasharray: 4 2
  concept_input_validation -->|has abstraction| abstraction_api
  linkStyle 177 stroke-dasharray: 4 2
  concept_input_validation -->|has abstraction| abstraction_security
  linkStyle 178 stroke-dasharray: 4 2
  concept_intermediate_representation -->|has abstraction| abstraction_compiler
  linkStyle 179 stroke-dasharray: 4 2
  concept_intermediate_representation -->|has abstraction| abstraction_data
  linkStyle 180 stroke-dasharray: 4 2
  concept_iterator -->|has abstraction| abstraction_design
  linkStyle 181 stroke-dasharray: 4 2
  concept_key_value_model -->|has abstraction| abstraction_data
  linkStyle 182 stroke-dasharray: 4 2
  concept_layered -->|has abstraction| abstraction_architectural
  linkStyle 183 stroke-dasharray: 4 2
  concept_lazy_loading -->|has abstraction| abstraction_deployment
  linkStyle 184 stroke-dasharray: 4 2
  concept_lazy_loading -->|has abstraction| abstraction_frontend
  linkStyle 185 stroke-dasharray: 4 2
  concept_leader_election -->|has abstraction| abstraction_concurrency
  linkStyle 186 stroke-dasharray: 4 2
  concept_leader_election -->|has abstraction| abstraction_resilience
  linkStyle 187 stroke-dasharray: 4 2
  concept_ledger -->|has abstraction| abstraction_data
  linkStyle 188 stroke-dasharray: 4 2
  concept_ledger -->|has abstraction| abstraction_financial
  linkStyle 189 stroke-dasharray: 4 2
  concept_lexer_parser -->|has abstraction| abstraction_compiler
  linkStyle 190 stroke-dasharray: 4 2
  concept_lexer_parser -->|has abstraction| abstraction_design
  linkStyle 191 stroke-dasharray: 4 2
  concept_load_balancer -->|has abstraction| abstraction_infrastructure
  linkStyle 192 stroke-dasharray: 4 2
  concept_load_balancer -->|has abstraction| abstraction_networking
  linkStyle 193 stroke-dasharray: 4 2
  concept_long_polling -->|has abstraction| abstraction_integration
  linkStyle 194 stroke-dasharray: 4 2
  concept_lru_cache -->|has abstraction| abstraction_data
  linkStyle 195 stroke-dasharray: 4 2
  concept_lru_cache -->|has abstraction| abstraction_infrastructure
  linkStyle 196 stroke-dasharray: 4 2
  concept_mapreduce -->|has abstraction| abstraction_concurrency
  linkStyle 197 stroke-dasharray: 4 2
  concept_mapreduce -->|has abstraction| abstraction_data
  linkStyle 198 stroke-dasharray: 4 2
  concept_materialized_view -->|has abstraction| abstraction_data
  linkStyle 199 stroke-dasharray: 4 2
  concept_mediator -->|has abstraction| abstraction_design
  linkStyle 200 stroke-dasharray: 4 2
  concept_mediator -->|has abstraction| abstraction_integration
  linkStyle 201 stroke-dasharray: 4 2
  concept_memento -->|has abstraction| abstraction_design
  linkStyle 202 stroke-dasharray: 4 2
  concept_message_queue -->|has abstraction| abstraction_infrastructure
  linkStyle 203 stroke-dasharray: 4 2
  concept_message_queue -->|has abstraction| abstraction_messaging
  linkStyle 204 stroke-dasharray: 4 2
  concept_metrics_instrumentation -->|has abstraction| abstraction_observability
  linkStyle 205 stroke-dasharray: 4 2
  concept_micro_frontend -->|has abstraction| abstraction_architectural
  linkStyle 206 stroke-dasharray: 4 2
  concept_micro_frontend -->|has abstraction| abstraction_deployment
  linkStyle 207 stroke-dasharray: 4 2
  concept_micro_frontend -->|has abstraction| abstraction_frontend
  linkStyle 208 stroke-dasharray: 4 2
  concept_microservices -->|has abstraction| abstraction_architectural
  linkStyle 209 stroke-dasharray: 4 2
  concept_middleware -->|has abstraction| abstraction_integration
  linkStyle 210 stroke-dasharray: 4 2
  concept_middleware -->|has abstraction| abstraction_lifecycle
  linkStyle 211 stroke-dasharray: 4 2
  concept_model_registry -->|has abstraction| abstraction_lifecycle
  linkStyle 212 stroke-dasharray: 4 2
  concept_model_registry -->|has abstraction| abstraction_ml
  linkStyle 213 stroke-dasharray: 4 2
  concept_modular_monolith -->|has abstraction| abstraction_architectural
  linkStyle 214 stroke-dasharray: 4 2
  concept_monad -->|has abstraction| abstraction_design
  linkStyle 215 stroke-dasharray: 4 2
  concept_monad -->|has abstraction| abstraction_error_handling
  linkStyle 216 stroke-dasharray: 4 2
  concept_mtls -->|has abstraction| abstraction_infrastructure
  linkStyle 217 stroke-dasharray: 4 2
  concept_mtls -->|has abstraction| abstraction_security
  linkStyle 218 stroke-dasharray: 4 2
  concept_multi_tenant -->|has abstraction| abstraction_architectural
  linkStyle 219 stroke-dasharray: 4 2
  concept_multi_tenant -->|has abstraction| abstraction_data
  linkStyle 220 stroke-dasharray: 4 2
  concept_mvc -->|has abstraction| abstraction_architectural
  linkStyle 221 stroke-dasharray: 4 2
  concept_mvc -->|has abstraction| abstraction_frontend
  linkStyle 222 stroke-dasharray: 4 2
  concept_mvvm -->|has abstraction| abstraction_architectural
  linkStyle 223 stroke-dasharray: 4 2
  concept_mvvm -->|has abstraction| abstraction_frontend
  linkStyle 224 stroke-dasharray: 4 2
  concept_null_object -->|has abstraction| abstraction_design
  linkStyle 225 stroke-dasharray: 4 2
  concept_oauth_oidc -->|has abstraction| abstraction_security
  linkStyle 226 stroke-dasharray: 4 2
  concept_object_pool -->|has abstraction| abstraction_design
  linkStyle 227 stroke-dasharray: 4 2
  concept_object_pool -->|has abstraction| abstraction_infrastructure
  linkStyle 228 stroke-dasharray: 4 2
  concept_observer -->|has abstraction| abstraction_design
  linkStyle 229 stroke-dasharray: 4 2
  concept_observer -->|has abstraction| abstraction_messaging
  linkStyle 230 stroke-dasharray: 4 2
  concept_optimistic_locking -->|has abstraction| abstraction_concurrency
  linkStyle 231 stroke-dasharray: 4 2
  concept_optimistic_locking -->|has abstraction| abstraction_data
  linkStyle 232 stroke-dasharray: 4 2
  concept_optimistic_update -->|has abstraction| abstraction_data
  linkStyle 233 stroke-dasharray: 4 2
  concept_optimistic_update -->|has abstraction| abstraction_frontend
  linkStyle 234 stroke-dasharray: 4 2
  concept_optimistic_update -->|has abstraction| abstraction_resilience
  linkStyle 235 stroke-dasharray: 4 2
  concept_orchestration -->|has abstraction| abstraction_architectural
  linkStyle 236 stroke-dasharray: 4 2
  concept_orchestration -->|has abstraction| abstraction_integration
  linkStyle 237 stroke-dasharray: 4 2
  concept_outbox -->|has abstraction| abstraction_data
  linkStyle 238 stroke-dasharray: 4 2
  concept_outbox -->|has abstraction| abstraction_messaging
  linkStyle 239 stroke-dasharray: 4 2
  concept_outbox -->|has abstraction| abstraction_resilience
  linkStyle 240 stroke-dasharray: 4 2
  concept_pagination -->|has abstraction| abstraction_api
  linkStyle 241 stroke-dasharray: 4 2
  concept_pagination -->|has abstraction| abstraction_data
  linkStyle 242 stroke-dasharray: 4 2
  concept_pipeline_filter -->|has abstraction| abstraction_data
  linkStyle 243 stroke-dasharray: 4 2
  concept_pipeline_filter -->|has abstraction| abstraction_design
  linkStyle 244 stroke-dasharray: 4 2
  concept_pipeline_stages -->|has abstraction| abstraction_architectural
  linkStyle 245 stroke-dasharray: 4 2
  concept_pipeline_stages -->|has abstraction| abstraction_data
  linkStyle 246 stroke-dasharray: 4 2
  concept_plugin -->|has abstraction| abstraction_design
  linkStyle 247 stroke-dasharray: 4 2
  concept_plugin_host -->|has abstraction| abstraction_architectural
  linkStyle 248 stroke-dasharray: 4 2
  concept_plugin_host -->|has abstraction| abstraction_design
  linkStyle 249 stroke-dasharray: 4 2
  concept_polling_flow -->|has abstraction| abstraction_integration
  linkStyle 250 stroke-dasharray: 4 2
  concept_polling_flow -->|has abstraction| abstraction_lifecycle
  linkStyle 251 stroke-dasharray: 4 2
  concept_producer_consumer -->|has abstraction| abstraction_concurrency
  linkStyle 252 stroke-dasharray: 4 2
  concept_producer_consumer -->|has abstraction| abstraction_messaging
  linkStyle 253 stroke-dasharray: 4 2
  concept_property_graph -->|has abstraction| abstraction_data
  linkStyle 254 stroke-dasharray: 4 2
  concept_property_graph -->|has abstraction| abstraction_graph
  linkStyle 255 stroke-dasharray: 4 2
  concept_property_testing -->|has abstraction| abstraction_testing
  linkStyle 256 stroke-dasharray: 4 2
  concept_prototype -->|has abstraction| abstraction_design
  linkStyle 257 stroke-dasharray: 4 2
  concept_proxy -->|has abstraction| abstraction_design
  linkStyle 258 stroke-dasharray: 4 2
  concept_pub_sub -->|has abstraction| abstraction_integration
  linkStyle 259 stroke-dasharray: 4 2
  concept_pub_sub -->|has abstraction| abstraction_messaging
  linkStyle 260 stroke-dasharray: 4 2
  concept_query_object -->|has abstraction| abstraction_data
  linkStyle 261 stroke-dasharray: 4 2
  concept_query_object -->|has abstraction| abstraction_design
  linkStyle 262 stroke-dasharray: 4 2
  concept_rate_limiting -->|has abstraction| abstraction_resilience
  linkStyle 263 stroke-dasharray: 4 2
  concept_rate_limiting -->|has abstraction| abstraction_security
  linkStyle 264 stroke-dasharray: 4 2
  concept_rbac -->|has abstraction| abstraction_security
  linkStyle 265 stroke-dasharray: 4 2
  concept_reactive_store -->|has abstraction| abstraction_data
  linkStyle 266 stroke-dasharray: 4 2
  concept_reactive_store -->|has abstraction| abstraction_frontend
  linkStyle 267 stroke-dasharray: 4 2
  concept_reactor -->|has abstraction| abstraction_architectural
  linkStyle 268 stroke-dasharray: 4 2
  concept_reactor -->|has abstraction| abstraction_concurrency
  linkStyle 269 stroke-dasharray: 4 2
  concept_read_through -->|has abstraction| abstraction_data
  linkStyle 270 stroke-dasharray: 4 2
  concept_read_write_lock -->|has abstraction| abstraction_concurrency
  linkStyle 271 stroke-dasharray: 4 2
  concept_refresh_ahead -->|has abstraction| abstraction_data
  linkStyle 272 stroke-dasharray: 4 2
  concept_refresh_ahead -->|has abstraction| abstraction_resilience
  linkStyle 273 stroke-dasharray: 4 2
  concept_registry_model -->|has abstraction| abstraction_data
  linkStyle 274 stroke-dasharray: 4 2
  concept_repository -->|has abstraction| abstraction_data
  linkStyle 275 stroke-dasharray: 4 2
  concept_repository -->|has abstraction| abstraction_design
  linkStyle 276 stroke-dasharray: 4 2
  concept_request_path -->|has abstraction| abstraction_api
  linkStyle 277 stroke-dasharray: 4 2
  concept_request_path -->|has abstraction| abstraction_integration
  linkStyle 278 stroke-dasharray: 4 2
  concept_request_reply -->|has abstraction| abstraction_integration
  linkStyle 279 stroke-dasharray: 4 2
  concept_request_reply -->|has abstraction| abstraction_messaging
  linkStyle 280 stroke-dasharray: 4 2
  concept_rest -->|has abstraction| abstraction_api
  linkStyle 281 stroke-dasharray: 4 2
  concept_rest -->|has abstraction| abstraction_integration
  linkStyle 282 stroke-dasharray: 4 2
  concept_result_type -->|has abstraction| abstraction_design
  linkStyle 283 stroke-dasharray: 4 2
  concept_result_type -->|has abstraction| abstraction_error_handling
  linkStyle 284 stroke-dasharray: 4 2
  concept_retry -->|has abstraction| abstraction_integration
  linkStyle 285 stroke-dasharray: 4 2
  concept_retry -->|has abstraction| abstraction_resilience
  linkStyle 286 stroke-dasharray: 4 2
  concept_ring_buffer -->|has abstraction| abstraction_concurrency
  linkStyle 287 stroke-dasharray: 4 2
  concept_ring_buffer -->|has abstraction| abstraction_data
  linkStyle 288 stroke-dasharray: 4 2
  concept_route_guard -->|has abstraction| abstraction_frontend
  linkStyle 289 stroke-dasharray: 4 2
  concept_route_guard -->|has abstraction| abstraction_security
  linkStyle 290 stroke-dasharray: 4 2
  concept_router -->|has abstraction| abstraction_frontend
  linkStyle 291 stroke-dasharray: 4 2
  concept_router -->|has abstraction| abstraction_integration
  linkStyle 292 stroke-dasharray: 4 2
  concept_rule_engine -->|has abstraction| abstraction_design
  linkStyle 293 stroke-dasharray: 4 2
  concept_rule_engine -->|has abstraction| abstraction_logic
  linkStyle 294 stroke-dasharray: 4 2
  concept_saga -->|has abstraction| abstraction_integration
  linkStyle 295 stroke-dasharray: 4 2
  concept_saga -->|has abstraction| abstraction_resilience
  linkStyle 296 stroke-dasharray: 4 2
  concept_saga_orchestrator -->|has abstraction| abstraction_integration
  linkStyle 297 stroke-dasharray: 4 2
  concept_saga_orchestrator -->|has abstraction| abstraction_messaging
  linkStyle 298 stroke-dasharray: 4 2
  concept_scatter_gather -->|has abstraction| abstraction_integration
  linkStyle 299 stroke-dasharray: 4 2
  concept_scheduler -->|has abstraction| abstraction_lifecycle
  linkStyle 300 stroke-dasharray: 4 2
  concept_schema_registry -->|has abstraction| abstraction_data
  linkStyle 301 stroke-dasharray: 4 2
  concept_schema_registry -->|has abstraction| abstraction_integration
  linkStyle 302 stroke-dasharray: 4 2
  concept_search_index -->|has abstraction| abstraction_data
  linkStyle 303 stroke-dasharray: 4 2
  concept_search_index -->|has abstraction| abstraction_search
  linkStyle 304 stroke-dasharray: 4 2
  concept_secret_management -->|has abstraction| abstraction_infrastructure
  linkStyle 305 stroke-dasharray: 4 2
  concept_secret_management -->|has abstraction| abstraction_security
  linkStyle 306 stroke-dasharray: 4 2
  concept_server_prefetch -->|has abstraction| abstraction_data
  linkStyle 307 stroke-dasharray: 4 2
  concept_server_prefetch -->|has abstraction| abstraction_frontend
  linkStyle 308 stroke-dasharray: 4 2
  concept_server_route_registration -->|has abstraction| abstraction_api
  linkStyle 309 stroke-dasharray: 4 2
  concept_server_route_registration -->|has abstraction| abstraction_integration
  linkStyle 310 stroke-dasharray: 4 2
  concept_server_sent_events -->|has abstraction| abstraction_infrastructure
  linkStyle 311 stroke-dasharray: 4 2
  concept_server_sent_events -->|has abstraction| abstraction_integration
  linkStyle 312 stroke-dasharray: 4 2
  concept_serverless -->|has abstraction| abstraction_architectural
  linkStyle 313 stroke-dasharray: 4 2
  concept_serverless -->|has abstraction| abstraction_deployment
  linkStyle 314 stroke-dasharray: 4 2
  concept_service_discovery -->|has abstraction| abstraction_infrastructure
  linkStyle 315 stroke-dasharray: 4 2
  concept_service_discovery -->|has abstraction| abstraction_integration
  linkStyle 316 stroke-dasharray: 4 2
  concept_service_manager -->|has abstraction| abstraction_lifecycle
  linkStyle 317 stroke-dasharray: 4 2
  concept_service_mesh -->|has abstraction| abstraction_infrastructure
  linkStyle 318 stroke-dasharray: 4 2
  concept_service_mesh -->|has abstraction| abstraction_integration
  linkStyle 319 stroke-dasharray: 4 2
  concept_session_auth -->|has abstraction| abstraction_security
  linkStyle 320 stroke-dasharray: 4 2
  concept_sharding -->|has abstraction| abstraction_data
  linkStyle 321 stroke-dasharray: 4 2
  concept_sharding -->|has abstraction| abstraction_infrastructure
  linkStyle 322 stroke-dasharray: 4 2
  concept_shared_database -->|has abstraction| abstraction_data
  linkStyle 323 stroke-dasharray: 4 2
  concept_shared_database -->|has abstraction| abstraction_integration
  linkStyle 324 stroke-dasharray: 4 2
  concept_side_effect_hook -->|has abstraction| abstraction_frontend
  linkStyle 325 stroke-dasharray: 4 2
  concept_side_effect_hook -->|has abstraction| abstraction_lifecycle
  linkStyle 326 stroke-dasharray: 4 2
  concept_sidecar -->|has abstraction| abstraction_deployment
  linkStyle 327 stroke-dasharray: 4 2
  concept_sidecar -->|has abstraction| abstraction_infrastructure
  linkStyle 328 stroke-dasharray: 4 2
  concept_sidecar -->|has abstraction| abstraction_lifecycle
  linkStyle 329 stroke-dasharray: 4 2
  concept_sidecar_mesh -->|has abstraction| abstraction_deployment
  linkStyle 330 stroke-dasharray: 4 2
  concept_sidecar_mesh -->|has abstraction| abstraction_infrastructure
  linkStyle 331 stroke-dasharray: 4 2
  concept_singleton -->|has abstraction| abstraction_design
  linkStyle 332 stroke-dasharray: 4 2
  concept_snapshot_testing -->|has abstraction| abstraction_testing
  linkStyle 333 stroke-dasharray: 4 2
  concept_social_graph -->|has abstraction| abstraction_data
  linkStyle 334 stroke-dasharray: 4 2
  concept_social_graph -->|has abstraction| abstraction_social
  linkStyle 335 stroke-dasharray: 4 2
  concept_soft_delete -->|has abstraction| abstraction_data
  linkStyle 336 stroke-dasharray: 4 2
  concept_spatial -->|has abstraction| abstraction_data
  linkStyle 337 stroke-dasharray: 4 2
  concept_spatial -->|has abstraction| abstraction_geospatial
  linkStyle 338 stroke-dasharray: 4 2
  concept_spatial_partitioning -->|has abstraction| abstraction_data
  linkStyle 339 stroke-dasharray: 4 2
  concept_spatial_partitioning -->|has abstraction| abstraction_realtime
  linkStyle 340 stroke-dasharray: 4 2
  concept_specification -->|has abstraction| abstraction_design
  linkStyle 341 stroke-dasharray: 4 2
  concept_state_machine -->|has abstraction| abstraction_design
  linkStyle 342 stroke-dasharray: 4 2
  concept_state_machine -->|has abstraction| abstraction_lifecycle
  linkStyle 343 stroke-dasharray: 4 2
  concept_strangler_fig -->|has abstraction| abstraction_architectural
  linkStyle 344 stroke-dasharray: 4 2
  concept_strangler_fig -->|has abstraction| abstraction_lifecycle
  linkStyle 345 stroke-dasharray: 4 2
  concept_strategy -->|has abstraction| abstraction_design
  linkStyle 346 stroke-dasharray: 4 2
  concept_stream_processing -->|has abstraction| abstraction_data
  linkStyle 347 stroke-dasharray: 4 2
  concept_stream_processing -->|has abstraction| abstraction_messaging
  linkStyle 348 stroke-dasharray: 4 2
  concept_stream_processing -->|has abstraction| abstraction_realtime
  linkStyle 349 stroke-dasharray: 4 2
  concept_stream_to_store -->|has abstraction| abstraction_data
  linkStyle 350 stroke-dasharray: 4 2
  concept_stream_to_store -->|has abstraction| abstraction_integration
  linkStyle 351 stroke-dasharray: 4 2
  concept_streaming_flow -->|has abstraction| abstraction_data
  linkStyle 352 stroke-dasharray: 4 2
  concept_streaming_flow -->|has abstraction| abstraction_messaging
  linkStyle 353 stroke-dasharray: 4 2
  concept_streaming_flow -->|has abstraction| abstraction_realtime
  linkStyle 354 stroke-dasharray: 4 2
  concept_structured_logging -->|has abstraction| abstraction_observability
  linkStyle 355 stroke-dasharray: 4 2
  concept_subscription -->|has abstraction| abstraction_data
  linkStyle 356 stroke-dasharray: 4 2
  concept_subscription -->|has abstraction| abstraction_financial
  linkStyle 357 stroke-dasharray: 4 2
  concept_suspense_boundary -->|has abstraction| abstraction_frontend
  linkStyle 358 stroke-dasharray: 4 2
  concept_suspense_boundary -->|has abstraction| abstraction_lifecycle
  linkStyle 359 stroke-dasharray: 4 2
  concept_template_method -->|has abstraction| abstraction_design
  linkStyle 360 stroke-dasharray: 4 2
  concept_tenant_isolation -->|has abstraction| abstraction_data
  linkStyle 361 stroke-dasharray: 4 2
  concept_tenant_isolation -->|has abstraction| abstraction_security
  linkStyle 362 stroke-dasharray: 4 2
  concept_tenant_routing -->|has abstraction| abstraction_integration
  linkStyle 363 stroke-dasharray: 4 2
  concept_tenant_routing -->|has abstraction| abstraction_security
  linkStyle 364 stroke-dasharray: 4 2
  concept_tensor -->|has abstraction| abstraction_compute
  linkStyle 365 stroke-dasharray: 4 2
  concept_tensor -->|has abstraction| abstraction_data
  linkStyle 366 stroke-dasharray: 4 2
  concept_test_doubles -->|has abstraction| abstraction_testing
  linkStyle 367 stroke-dasharray: 4 2
  concept_tick_simulation -->|has abstraction| abstraction_lifecycle
  linkStyle 368 stroke-dasharray: 4 2
  concept_tick_simulation -->|has abstraction| abstraction_realtime
  linkStyle 369 stroke-dasharray: 4 2
  concept_time_series -->|has abstraction| abstraction_data
  linkStyle 370 stroke-dasharray: 4 2
  concept_time_series -->|has abstraction| abstraction_temporal
  linkStyle 371 stroke-dasharray: 4 2
  concept_timeout -->|has abstraction| abstraction_integration
  linkStyle 372 stroke-dasharray: 4 2
  concept_timeout -->|has abstraction| abstraction_resilience
  linkStyle 373 stroke-dasharray: 4 2
  concept_token_auth -->|has abstraction| abstraction_security
  linkStyle 374 stroke-dasharray: 4 2
  concept_training_pipeline -->|has abstraction| abstraction_data
  linkStyle 375 stroke-dasharray: 4 2
  concept_training_pipeline -->|has abstraction| abstraction_ml
  linkStyle 376 stroke-dasharray: 4 2
  concept_trie -->|has abstraction| abstraction_data
  linkStyle 377 stroke-dasharray: 4 2
  concept_unit_of_work -->|has abstraction| abstraction_data
  linkStyle 378 stroke-dasharray: 4 2
  concept_unit_of_work -->|has abstraction| abstraction_design
  linkStyle 379 stroke-dasharray: 4 2
  concept_value_object -->|has abstraction| abstraction_design
  linkStyle 380 stroke-dasharray: 4 2
  concept_versioned_document -->|has abstraction| abstraction_collaboration
  linkStyle 381 stroke-dasharray: 4 2
  concept_versioned_document -->|has abstraction| abstraction_data
  linkStyle 382 stroke-dasharray: 4 2
  concept_visitor -->|has abstraction| abstraction_design
  linkStyle 383 stroke-dasharray: 4 2
  concept_webhook -->|has abstraction| abstraction_integration
  linkStyle 384 stroke-dasharray: 4 2
  concept_websocket -->|has abstraction| abstraction_infrastructure
  linkStyle 385 stroke-dasharray: 4 2
  concept_websocket -->|has abstraction| abstraction_integration
  linkStyle 386 stroke-dasharray: 4 2
  concept_worker_pool -->|has abstraction| abstraction_concurrency
  linkStyle 387 stroke-dasharray: 4 2
  concept_worker_pool -->|has abstraction| abstraction_infrastructure
  linkStyle 388 stroke-dasharray: 4 2
  concept_workflow_engine -->|has abstraction| abstraction_integration
  linkStyle 389 stroke-dasharray: 4 2
  concept_workflow_engine -->|has abstraction| abstraction_lifecycle
  linkStyle 390 stroke-dasharray: 4 2
  concept_workflow_state_machine -->|has abstraction| abstraction_data
  linkStyle 391 stroke-dasharray: 4 2
  concept_workflow_state_machine -->|has abstraction| abstraction_lifecycle
  linkStyle 392 stroke-dasharray: 4 2
  concept_write_behind -->|has abstraction| abstraction_data
  linkStyle 393 stroke-dasharray: 4 2
  concept_abstract_factory -->|has type| type_pattern
  linkStyle 394 stroke-dasharray: 4 2
  concept_active_record -->|has type| type_pattern
  linkStyle 395 stroke-dasharray: 4 2
  concept_actor_model -->|has type| type_pattern
  linkStyle 396 stroke-dasharray: 4 2
  concept_adapter -->|has type| type_pattern
  linkStyle 397 stroke-dasharray: 4 2
  concept_aggregate -->|has type| type_pattern
  linkStyle 398 stroke-dasharray: 4 2
  concept_anemic_domain_model -->|has type| type_anti_pattern
  linkStyle 399 stroke-dasharray: 4 2
  concept_anti_corruption_layer -->|has type| type_pattern
  linkStyle 400 stroke-dasharray: 4 2
  concept_api_gateway -->|has type| type_pattern
  linkStyle 401 stroke-dasharray: 4 2
  concept_api_key_auth -->|has type| type_pattern
  linkStyle 402 stroke-dasharray: 4 2
  concept_ast -->|has type| type_pattern
  linkStyle 403 stroke-dasharray: 4 2
  concept_at_least_once_delivery -->|has type| type_pattern
  linkStyle 404 stroke-dasharray: 4 2
  concept_audit_logging -->|has type| type_pattern
  linkStyle 405 stroke-dasharray: 4 2
  concept_backpressure -->|has type| type_pattern
  linkStyle 406 stroke-dasharray: 4 2
  concept_batch_loader -->|has type| type_pattern
  linkStyle 407 stroke-dasharray: 4 2
  concept_batch_processing -->|has type| type_flow_shape
  linkStyle 408 stroke-dasharray: 4 2
  concept_bff -->|has type| type_pattern
  linkStyle 409 stroke-dasharray: 4 2
  concept_big_ball_of_mud -->|has type| type_anti_pattern
  linkStyle 410 stroke-dasharray: 4 2
  concept_block_content -->|has type| type_pattern
  linkStyle 411 stroke-dasharray: 4 2
  concept_bloom_filter -->|has type| type_pattern
  linkStyle 412 stroke-dasharray: 4 2
  concept_blue_green -->|has type| type_pattern
  linkStyle 413 stroke-dasharray: 4 2
  concept_boolean_blindness -->|has type| type_anti_pattern
  linkStyle 414 stroke-dasharray: 4 2
  concept_bounded_context -->|has type| type_pattern
  linkStyle 415 stroke-dasharray: 4 2
  concept_breaking_changes -->|has type| type_anti_pattern
  linkStyle 416 stroke-dasharray: 4 2
  concept_bridge -->|has type| type_pattern
  linkStyle 417 stroke-dasharray: 4 2
  concept_builder -->|has type| type_pattern
  linkStyle 418 stroke-dasharray: 4 2
  concept_bulkhead -->|has type| type_pattern
  linkStyle 419 stroke-dasharray: 4 2
  concept_busy_waiting -->|has type| type_anti_pattern
  linkStyle 420 stroke-dasharray: 4 2
  concept_cache_aside -->|has type| type_pattern
  linkStyle 421 stroke-dasharray: 4 2
  concept_cache_stampede_prevention -->|has type| type_pattern
  linkStyle 422 stroke-dasharray: 4 2
  concept_callback_hell -->|has type| type_anti_pattern
  linkStyle 423 stroke-dasharray: 4 2
  concept_canary -->|has type| type_pattern
  linkStyle 424 stroke-dasharray: 4 2
  concept_cargo_cult -->|has type| type_anti_pattern
  linkStyle 425 stroke-dasharray: 4 2
  concept_catalog -->|has type| type_pattern
  linkStyle 426 stroke-dasharray: 4 2
  concept_cell_based -->|has type| type_structure_shape
  linkStyle 427 stroke-dasharray: 4 2
  concept_chain_of_responsibility -->|has type| type_pattern
  linkStyle 428 stroke-dasharray: 4 2
  concept_change_data_capture -->|has type| type_pattern
  linkStyle 429 stroke-dasharray: 4 2
  concept_chatty_api -->|has type| type_anti_pattern
  linkStyle 430 stroke-dasharray: 4 2
  concept_choreography -->|has type| type_pattern
  linkStyle 431 stroke-dasharray: 4 2
  concept_circuit_breaker -->|has type| type_pattern
  linkStyle 432 stroke-dasharray: 4 2
  concept_circular_dependency -->|has type| type_anti_pattern
  linkStyle 433 stroke-dasharray: 4 2
  concept_claim_check -->|has type| type_pattern
  linkStyle 434 stroke-dasharray: 4 2
  concept_command -->|has type| type_pattern
  linkStyle 435 stroke-dasharray: 4 2
  concept_competing_consumers -->|has type| type_pattern
  linkStyle 436 stroke-dasharray: 4 2
  concept_component -->|has type| type_pattern
  linkStyle 437 stroke-dasharray: 4 2
  concept_component_slot -->|has type| type_pattern
  linkStyle 438 stroke-dasharray: 4 2
  concept_composite -->|has type| type_pattern
  linkStyle 439 stroke-dasharray: 4 2
  concept_config_management -->|has type| type_pattern
  linkStyle 440 stroke-dasharray: 4 2
  concept_config_sprawl -->|has type| type_anti_pattern
  linkStyle 441 stroke-dasharray: 4 2
  concept_connection_pooling -->|has type| type_pattern
  linkStyle 442 stroke-dasharray: 4 2
  concept_content_negotiation -->|has type| type_pattern
  linkStyle 443 stroke-dasharray: 4 2
  concept_contract_testing -->|has type| type_pattern
  linkStyle 444 stroke-dasharray: 4 2
  concept_control_plane -->|has type| type_pattern
  linkStyle 445 stroke-dasharray: 4 2
  concept_conversation_thread -->|has type| type_pattern
  linkStyle 446 stroke-dasharray: 4 2
  concept_copy_paste_programming -->|has type| type_anti_pattern
  linkStyle 447 stroke-dasharray: 4 2
  concept_correlation_id -->|has type| type_pattern
  linkStyle 448 stroke-dasharray: 4 2
  concept_cors -->|has type| type_pattern
  linkStyle 449 stroke-dasharray: 4 2
  concept_cqrs -->|has type| type_pattern
  linkStyle 450 stroke-dasharray: 4 2
  concept_data_mapper -->|has type| type_pattern
  linkStyle 451 stroke-dasharray: 4 2
  concept_data_pipeline -->|has type| type_flow_shape
  linkStyle 452 stroke-dasharray: 4 2
  concept_data_plane -->|has type| type_pattern
  linkStyle 453 stroke-dasharray: 4 2
  concept_database_migration -->|has type| type_pattern
  linkStyle 454 stroke-dasharray: 4 2
  concept_database_per_service -->|has type| type_pattern
  linkStyle 455 stroke-dasharray: 4 2
  concept_ddd -->|has type| type_pattern
  linkStyle 456 stroke-dasharray: 4 2
  concept_dead_letter -->|has type| type_pattern
  linkStyle 457 stroke-dasharray: 4 2
  concept_deadlock -->|has type| type_anti_pattern
  linkStyle 458 stroke-dasharray: 4 2
  concept_decorator -->|has type| type_pattern
  linkStyle 459 stroke-dasharray: 4 2
  concept_deep_nesting -->|has type| type_anti_pattern
  linkStyle 460 stroke-dasharray: 4 2
  concept_dependency_injection -->|has type| type_pattern
  linkStyle 461 stroke-dasharray: 4 2
  concept_distributed_lock -->|has type| type_pattern
  linkStyle 462 stroke-dasharray: 4 2
  concept_distributed_monolith -->|has type| type_anti_pattern
  linkStyle 463 stroke-dasharray: 4 2
  concept_distributed_tracing -->|has type| type_pattern
  linkStyle 464 stroke-dasharray: 4 2
  concept_dual_writes -->|has type| type_anti_pattern
  linkStyle 465 stroke-dasharray: 4 2
  concept_entity_component_system -->|has type| type_pattern
  linkStyle 466 stroke-dasharray: 4 2
  concept_environment_parity_gap -->|has type| type_anti_pattern
  linkStyle 467 stroke-dasharray: 4 2
  concept_error_boundary -->|has type| type_pattern
  linkStyle 468 stroke-dasharray: 4 2
  concept_error_code_returns -->|has type| type_anti_pattern
  linkStyle 469 stroke-dasharray: 4 2
  concept_etl -->|has type| type_pattern
  linkStyle 470 stroke-dasharray: 4 2
  concept_event_carried_state -->|has type| type_flow_shape
  linkStyle 471 stroke-dasharray: 4 2
  concept_event_driven -->|has type| type_pattern
  linkStyle 472 stroke-dasharray: 4 2
  concept_event_log -->|has type| type_domain_model
  linkStyle 473 stroke-dasharray: 4 2
  concept_event_notification -->|has type| type_flow_shape
  linkStyle 474 stroke-dasharray: 4 2
  concept_event_sourcing -->|has type| type_pattern
  linkStyle 475 stroke-dasharray: 4 2
  concept_eventual_consistency -->|has type| type_pattern
  linkStyle 476 stroke-dasharray: 4 2
  concept_exactly_once_semantics -->|has type| type_pattern
  linkStyle 477 stroke-dasharray: 4 2
  concept_experiment_framework -->|has type| type_pattern
  linkStyle 478 stroke-dasharray: 4 2
  concept_facade -->|has type| type_pattern
  linkStyle 479 stroke-dasharray: 4 2
  concept_factory -->|has type| type_pattern
  linkStyle 480 stroke-dasharray: 4 2
  concept_failure_cascade -->|has type| type_flow_shape
  linkStyle 481 stroke-dasharray: 4 2
  concept_fallback -->|has type| type_pattern
  linkStyle 482 stroke-dasharray: 4 2
  concept_fan_in -->|has type| type_flow_shape
  linkStyle 483 stroke-dasharray: 4 2
  concept_fan_out -->|has type| type_flow_shape
  linkStyle 484 stroke-dasharray: 4 2
  concept_feature_envy -->|has type| type_anti_pattern
  linkStyle 485 stroke-dasharray: 4 2
  concept_feature_flag -->|has type| type_pattern
  linkStyle 486 stroke-dasharray: 4 2
  concept_feature_store -->|has type| type_pattern
  linkStyle 487 stroke-dasharray: 4 2
  concept_fire_and_forget -->|has type| type_anti_pattern
  linkStyle 488 stroke-dasharray: 4 2
  concept_fixture_builder -->|has type| type_pattern
  linkStyle 489 stroke-dasharray: 4 2
  concept_flaky_tests -->|has type| type_anti_pattern
  linkStyle 490 stroke-dasharray: 4 2
  concept_flux -->|has type| type_pattern
  linkStyle 491 stroke-dasharray: 4 2
  concept_flyweight -->|has type| type_pattern
  linkStyle 492 stroke-dasharray: 4 2
  concept_form_binding -->|has type| type_pattern
  linkStyle 493 stroke-dasharray: 4 2
  concept_future_promise -->|has type| type_pattern
  linkStyle 494 stroke-dasharray: 4 2
  concept_game_loop -->|has type| type_pattern
  linkStyle 495 stroke-dasharray: 4 2
  concept_gateway_backends -->|has type| type_structure_shape
  linkStyle 496 stroke-dasharray: 4 2
  concept_gitops -->|has type| type_pattern
  linkStyle 497 stroke-dasharray: 4 2
  concept_god_endpoint -->|has type| type_anti_pattern
  linkStyle 498 stroke-dasharray: 4 2
  concept_god_object -->|has type| type_anti_pattern
  linkStyle 499 stroke-dasharray: 4 2
  concept_golden_hammer -->|has type| type_anti_pattern
  linkStyle 500 stroke-dasharray: 4 2
  concept_graceful_degradation -->|has type| type_pattern
  linkStyle 501 stroke-dasharray: 4 2
  concept_graph -->|has type| type_pattern
  linkStyle 502 stroke-dasharray: 4 2
  concept_graphql -->|has type| type_pattern
  linkStyle 503 stroke-dasharray: 4 2
  concept_grpc -->|has type| type_pattern
  linkStyle 504 stroke-dasharray: 4 2
  concept_hardcoded_credentials -->|has type| type_anti_pattern
  linkStyle 505 stroke-dasharray: 4 2
  concept_hardcoded_urls -->|has type| type_anti_pattern
  linkStyle 506 stroke-dasharray: 4 2
  concept_health_check -->|has type| type_pattern
  linkStyle 507 stroke-dasharray: 4 2
  concept_hexagonal -->|has type| type_pattern
  linkStyle 508 stroke-dasharray: 4 2
  concept_hidden_side_effects -->|has type| type_anti_pattern
  linkStyle 509 stroke-dasharray: 4 2
  concept_hydration -->|has type| type_pattern
  linkStyle 510 stroke-dasharray: 4 2
  concept_ice_cream_cone -->|has type| type_anti_pattern
  linkStyle 511 stroke-dasharray: 4 2
  concept_idempotent_consumer -->|has type| type_pattern
  linkStyle 512 stroke-dasharray: 4 2
  concept_immutable_infra -->|has type| type_pattern
  linkStyle 513 stroke-dasharray: 4 2
  concept_inbox -->|has type| type_unknown
  linkStyle 514 stroke-dasharray: 4 2
  concept_inconsistent_naming -->|has type| type_anti_pattern
  linkStyle 515 stroke-dasharray: 4 2
  concept_infrastructure_as_code -->|has type| type_pattern
  linkStyle 516 stroke-dasharray: 4 2
  concept_input_validation -->|has type| type_pattern
  linkStyle 517 stroke-dasharray: 4 2
  concept_insecure_deserialization -->|has type| type_anti_pattern
  linkStyle 518 stroke-dasharray: 4 2
  concept_intermediate_representation -->|has type| type_pattern
  linkStyle 519 stroke-dasharray: 4 2
  concept_iterator -->|has type| type_pattern
  linkStyle 520 stroke-dasharray: 4 2
  concept_key_value_model -->|has type| type_domain_model
  linkStyle 521 stroke-dasharray: 4 2
  concept_lava_flow -->|has type| type_anti_pattern
  linkStyle 522 stroke-dasharray: 4 2
  concept_layered -->|has type| type_structure_shape
  linkStyle 523 stroke-dasharray: 4 2
  concept_lazy_loading -->|has type| type_pattern
  linkStyle 524 stroke-dasharray: 4 2
  concept_leader_election -->|has type| type_pattern
  linkStyle 525 stroke-dasharray: 4 2
  concept_leaky_abstraction -->|has type| type_anti_pattern
  linkStyle 526 stroke-dasharray: 4 2
  concept_ledger -->|has type| type_pattern
  linkStyle 527 stroke-dasharray: 4 2
  concept_lexer_parser -->|has type| type_pattern
  linkStyle 528 stroke-dasharray: 4 2
  concept_load_balancer -->|has type| type_pattern
  linkStyle 529 stroke-dasharray: 4 2
  concept_log_and_throw -->|has type| type_anti_pattern
  linkStyle 530 stroke-dasharray: 4 2
  concept_log_spam -->|has type| type_anti_pattern
  linkStyle 531 stroke-dasharray: 4 2
  concept_long_polling -->|has type| type_pattern
  linkStyle 532 stroke-dasharray: 4 2
  concept_long_transactions -->|has type| type_anti_pattern
  linkStyle 533 stroke-dasharray: 4 2
  concept_lru_cache -->|has type| type_pattern
  linkStyle 534 stroke-dasharray: 4 2
  concept_magic_numbers -->|has type| type_anti_pattern
  linkStyle 535 stroke-dasharray: 4 2
  concept_mapreduce -->|has type| type_pattern
  linkStyle 536 stroke-dasharray: 4 2
  concept_materialized_view -->|has type| type_pattern
  linkStyle 537 stroke-dasharray: 4 2
  concept_mediator -->|has type| type_pattern
  linkStyle 538 stroke-dasharray: 4 2
  concept_memento -->|has type| type_pattern
  linkStyle 539 stroke-dasharray: 4 2
  concept_memory_leak -->|has type| type_anti_pattern
  linkStyle 540 stroke-dasharray: 4 2
  concept_message_queue -->|has type| type_pattern
  linkStyle 541 stroke-dasharray: 4 2
  concept_metric_cardinality_explosion -->|has type| type_anti_pattern
  linkStyle 542 stroke-dasharray: 4 2
  concept_metrics_instrumentation -->|has type| type_pattern
  linkStyle 543 stroke-dasharray: 4 2
  concept_micro_frontend -->|has type| type_pattern
  linkStyle 544 stroke-dasharray: 4 2
  concept_microservices -->|has type| type_pattern
  linkStyle 545 stroke-dasharray: 4 2
  concept_middleware -->|has type| type_pattern
  linkStyle 546 stroke-dasharray: 4 2
  concept_misleading_names -->|has type| type_anti_pattern
  linkStyle 547 stroke-dasharray: 4 2
  concept_missing_log_context -->|has type| type_anti_pattern
  linkStyle 548 stroke-dasharray: 4 2
  concept_model_registry -->|has type| type_pattern
  linkStyle 549 stroke-dasharray: 4 2
  concept_modular_monolith -->|has type| type_pattern
  linkStyle 550 stroke-dasharray: 4 2
  concept_monad -->|has type| type_pattern
  linkStyle 551 stroke-dasharray: 4 2
  concept_mtls -->|has type| type_pattern
  linkStyle 552 stroke-dasharray: 4 2
  concept_multi_tenant -->|has type| type_pattern
  linkStyle 553 stroke-dasharray: 4 2
  concept_mvc -->|has type| type_pattern
  linkStyle 554 stroke-dasharray: 4 2
  concept_mvvm -->|has type| type_pattern
  linkStyle 555 stroke-dasharray: 4 2
  concept_n_plus_one -->|has type| type_anti_pattern
  linkStyle 556 stroke-dasharray: 4 2
  concept_null_object -->|has type| type_pattern
  linkStyle 557 stroke-dasharray: 4 2
  concept_oauth_oidc -->|has type| type_pattern
  linkStyle 558 stroke-dasharray: 4 2
  concept_object_pool -->|has type| type_pattern
  linkStyle 559 stroke-dasharray: 4 2
  concept_observer -->|has type| type_pattern
  linkStyle 560 stroke-dasharray: 4 2
  concept_optimistic_locking -->|has type| type_pattern
  linkStyle 561 stroke-dasharray: 4 2
  concept_optimistic_update -->|has type| type_pattern
  linkStyle 562 stroke-dasharray: 4 2
  concept_orchestration -->|has type| type_pattern
  linkStyle 563 stroke-dasharray: 4 2
  concept_outbox -->|has type| type_pattern
  linkStyle 564 stroke-dasharray: 4 2
  concept_over_under_fetching -->|has type| type_anti_pattern
  linkStyle 565 stroke-dasharray: 4 2
  concept_pagination -->|has type| type_pattern
  linkStyle 566 stroke-dasharray: 4 2
  concept_pipeline_filter -->|has type| type_pattern
  linkStyle 567 stroke-dasharray: 4 2
  concept_pipeline_stages -->|has type| type_structure_shape
  linkStyle 568 stroke-dasharray: 4 2
  concept_plugin -->|has type| type_pattern
  linkStyle 569 stroke-dasharray: 4 2
  concept_plugin_host -->|has type| type_structure_shape
  linkStyle 570 stroke-dasharray: 4 2
  concept_pokemon_exception -->|has type| type_anti_pattern
  linkStyle 571 stroke-dasharray: 4 2
  concept_polling_flow -->|has type| type_flow_shape
  linkStyle 572 stroke-dasharray: 4 2
  concept_premature_optimization -->|has type| type_anti_pattern
  linkStyle 573 stroke-dasharray: 4 2
  concept_primitive_obsession -->|has type| type_anti_pattern
  linkStyle 574 stroke-dasharray: 4 2
  concept_producer_consumer -->|has type| type_pattern
  linkStyle 575 stroke-dasharray: 4 2
  concept_prop_drilling -->|has type| type_anti_pattern
  linkStyle 576 stroke-dasharray: 4 2
  concept_property_graph -->|has type| type_domain_model
  linkStyle 577 stroke-dasharray: 4 2
  concept_property_testing -->|has type| type_pattern
  linkStyle 578 stroke-dasharray: 4 2
  concept_prototype -->|has type| type_pattern
  linkStyle 579 stroke-dasharray: 4 2
  concept_proxy -->|has type| type_pattern
  linkStyle 580 stroke-dasharray: 4 2
  concept_pub_sub -->|has type| type_pattern
  linkStyle 581 stroke-dasharray: 4 2
  concept_query_object -->|has type| type_pattern
  linkStyle 582 stroke-dasharray: 4 2
  concept_race_condition -->|has type| type_anti_pattern
  linkStyle 583 stroke-dasharray: 4 2
  concept_rate_limiting -->|has type| type_pattern
  linkStyle 584 stroke-dasharray: 4 2
  concept_rbac -->|has type| type_pattern
  linkStyle 585 stroke-dasharray: 4 2
  concept_reactive_store -->|has type| type_pattern
  linkStyle 586 stroke-dasharray: 4 2
  concept_reactor -->|has type| type_pattern
  linkStyle 587 stroke-dasharray: 4 2
  concept_read_through -->|has type| type_pattern
  linkStyle 588 stroke-dasharray: 4 2
  concept_read_write_lock -->|has type| type_pattern
  linkStyle 589 stroke-dasharray: 4 2
  concept_refresh_ahead -->|has type| type_pattern
  linkStyle 590 stroke-dasharray: 4 2
  concept_registry_model -->|has type| type_domain_model
  linkStyle 591 stroke-dasharray: 4 2
  concept_reinventing_the_wheel -->|has type| type_anti_pattern
  linkStyle 592 stroke-dasharray: 4 2
  concept_repository -->|has type| type_pattern
  linkStyle 593 stroke-dasharray: 4 2
  concept_request_path -->|has type| type_flow_shape
  linkStyle 594 stroke-dasharray: 4 2
  concept_request_reply -->|has type| type_pattern
  linkStyle 595 stroke-dasharray: 4 2
  concept_rest -->|has type| type_pattern
  linkStyle 596 stroke-dasharray: 4 2
  concept_result_type -->|has type| type_pattern
  linkStyle 597 stroke-dasharray: 4 2
  concept_retry -->|has type| type_pattern
  linkStyle 598 stroke-dasharray: 4 2
  concept_ring_buffer -->|has type| type_pattern
  linkStyle 599 stroke-dasharray: 4 2
  concept_route_guard -->|has type| type_pattern
  linkStyle 600 stroke-dasharray: 4 2
  concept_router -->|has type| type_pattern
  linkStyle 601 stroke-dasharray: 4 2
  concept_rule_engine -->|has type| type_pattern
  linkStyle 602 stroke-dasharray: 4 2
  concept_saga -->|has type| type_pattern
  linkStyle 603 stroke-dasharray: 4 2
  concept_saga_orchestrator -->|has type| type_unknown
  linkStyle 604 stroke-dasharray: 4 2
  concept_scatter_gather -->|has type| type_flow_shape
  linkStyle 605 stroke-dasharray: 4 2
  concept_scheduler -->|has type| type_pattern
  linkStyle 606 stroke-dasharray: 4 2
  concept_schema_on_read -->|has type| type_anti_pattern
  linkStyle 607 stroke-dasharray: 4 2
  concept_schema_registry -->|has type| type_pattern
  linkStyle 608 stroke-dasharray: 4 2
  concept_search_index -->|has type| type_pattern
  linkStyle 609 stroke-dasharray: 4 2
  concept_secret_management -->|has type| type_pattern
  linkStyle 610 stroke-dasharray: 4 2
  concept_select_star -->|has type| type_anti_pattern
  linkStyle 611 stroke-dasharray: 4 2
  concept_server_prefetch -->|has type| type_pattern
  linkStyle 612 stroke-dasharray: 4 2
  concept_server_route_registration -->|has type| type_pattern
  linkStyle 613 stroke-dasharray: 4 2
  concept_server_sent_events -->|has type| type_pattern
  linkStyle 614 stroke-dasharray: 4 2
  concept_serverless -->|has type| type_pattern
  linkStyle 615 stroke-dasharray: 4 2
  concept_service_discovery -->|has type| type_pattern
  linkStyle 616 stroke-dasharray: 4 2
  concept_service_manager -->|has type| type_pattern
  linkStyle 617 stroke-dasharray: 4 2
  concept_service_mesh -->|has type| type_pattern
  linkStyle 618 stroke-dasharray: 4 2
  concept_session_auth -->|has type| type_pattern
  linkStyle 619 stroke-dasharray: 4 2
  concept_sharding -->|has type| type_pattern
  linkStyle 620 stroke-dasharray: 4 2
  concept_shared_database -->|has type| type_pattern
  linkStyle 621 stroke-dasharray: 4 2
  concept_shotgun_surgery -->|has type| type_anti_pattern
  linkStyle 622 stroke-dasharray: 4 2
  concept_side_effect_hook -->|has type| type_pattern
  linkStyle 623 stroke-dasharray: 4 2
  concept_sidecar -->|has type| type_pattern
  linkStyle 624 stroke-dasharray: 4 2
  concept_sidecar_mesh -->|has type| type_structure_shape
  linkStyle 625 stroke-dasharray: 4 2
  concept_singleton -->|has type| type_pattern
  linkStyle 626 stroke-dasharray: 4 2
  concept_snapshot_testing -->|has type| type_pattern
  linkStyle 627 stroke-dasharray: 4 2
  concept_snowflake_server -->|has type| type_anti_pattern
  linkStyle 628 stroke-dasharray: 4 2
  concept_social_graph -->|has type| type_domain_model
  linkStyle 629 stroke-dasharray: 4 2
  concept_soft_delete -->|has type| type_pattern
  linkStyle 630 stroke-dasharray: 4 2
  concept_spaghetti_code -->|has type| type_anti_pattern
  linkStyle 631 stroke-dasharray: 4 2
  concept_spatial -->|has type| type_pattern
  linkStyle 632 stroke-dasharray: 4 2
  concept_spatial_partitioning -->|has type| type_pattern
  linkStyle 633 stroke-dasharray: 4 2
  concept_specification -->|has type| type_pattern
  linkStyle 634 stroke-dasharray: 4 2
  concept_sql_injection -->|has type| type_anti_pattern
  linkStyle 635 stroke-dasharray: 4 2
  concept_state_machine -->|has type| type_pattern
  linkStyle 636 stroke-dasharray: 4 2
  concept_strangler_fig -->|has type| type_pattern
  linkStyle 637 stroke-dasharray: 4 2
  concept_strategy -->|has type| type_pattern
  linkStyle 638 stroke-dasharray: 4 2
  concept_stream_processing -->|has type| type_pattern
  linkStyle 639 stroke-dasharray: 4 2
  concept_stream_to_store -->|has type| type_pattern
  linkStyle 640 stroke-dasharray: 4 2
  concept_streaming_flow -->|has type| type_flow_shape
  linkStyle 641 stroke-dasharray: 4 2
  concept_stringly_typed -->|has type| type_anti_pattern
  linkStyle 642 stroke-dasharray: 4 2
  concept_structured_logging -->|has type| type_pattern
  linkStyle 643 stroke-dasharray: 4 2
  concept_subscription -->|has type| type_pattern
  linkStyle 644 stroke-dasharray: 4 2
  concept_suspense_boundary -->|has type| type_pattern
  linkStyle 645 stroke-dasharray: 4 2
  concept_swallowed_exception -->|has type| type_anti_pattern
  linkStyle 646 stroke-dasharray: 4 2
  concept_sync_in_async -->|has type| type_anti_pattern
  linkStyle 647 stroke-dasharray: 4 2
  concept_template_method -->|has type| type_pattern
  linkStyle 648 stroke-dasharray: 4 2
  concept_temporal_coupling -->|has type| type_anti_pattern
  linkStyle 649 stroke-dasharray: 4 2
  concept_tenant_isolation -->|has type| type_pattern
  linkStyle 650 stroke-dasharray: 4 2
  concept_tenant_routing -->|has type| type_pattern
  linkStyle 651 stroke-dasharray: 4 2
  concept_tensor -->|has type| type_pattern
  linkStyle 652 stroke-dasharray: 4 2
  concept_test_doubles -->|has type| type_pattern
  linkStyle 653 stroke-dasharray: 4 2
  concept_test_pollution -->|has type| type_anti_pattern
  linkStyle 654 stroke-dasharray: 4 2
  concept_tick_simulation -->|has type| type_pattern
  linkStyle 655 stroke-dasharray: 4 2
  concept_tight_coupling -->|has type| type_anti_pattern
  linkStyle 656 stroke-dasharray: 4 2
  concept_time_series -->|has type| type_pattern
  linkStyle 657 stroke-dasharray: 4 2
  concept_timeout -->|has type| type_pattern
  linkStyle 658 stroke-dasharray: 4 2
  concept_token_auth -->|has type| type_pattern
  linkStyle 659 stroke-dasharray: 4 2
  concept_train_wreck -->|has type| type_anti_pattern
  linkStyle 660 stroke-dasharray: 4 2
  concept_training_pipeline -->|has type| type_pattern
  linkStyle 661 stroke-dasharray: 4 2
  concept_trie -->|has type| type_pattern
  linkStyle 662 stroke-dasharray: 4 2
  concept_unbounded_growth -->|has type| type_anti_pattern
  linkStyle 663 stroke-dasharray: 4 2
  concept_unit_of_work -->|has type| type_pattern
  linkStyle 664 stroke-dasharray: 4 2
  concept_value_object -->|has type| type_pattern
  linkStyle 665 stroke-dasharray: 4 2
  concept_versioned_document -->|has type| type_pattern
  linkStyle 666 stroke-dasharray: 4 2
  concept_visitor -->|has type| type_pattern
  linkStyle 667 stroke-dasharray: 4 2
  concept_webhook -->|has type| type_pattern
  linkStyle 668 stroke-dasharray: 4 2
  concept_websocket -->|has type| type_pattern
  linkStyle 669 stroke-dasharray: 4 2
  concept_worker_pool -->|has type| type_pattern
  linkStyle 670 stroke-dasharray: 4 2
  concept_workflow_engine -->|has type| type_pattern
  linkStyle 671 stroke-dasharray: 4 2
  concept_workflow_state_machine -->|has type| type_domain_model
  linkStyle 672 stroke-dasharray: 4 2
  concept_write_behind -->|has type| type_pattern
  linkStyle 673 stroke-dasharray: 4 2
  framework_actix_web -->|implements| concept_rest
  framework_aiohttp -->|implements| concept_rest
  framework_angular -->|implements| concept_component
  framework_aspnet_controllers -->|implements| concept_rest
  framework_aspnet_minimal -->|implements| concept_rest
  framework_axum -->|implements| concept_rest
  framework_chi -->|implements| concept_rest
  framework_django -->|implements| concept_rest
  framework_echo -->|implements| concept_rest
  framework_elysia -->|implements| concept_rest
  framework_express -->|implements| concept_rest
  framework_fastapi -->|implements| concept_rest
  framework_fastify -->|implements| concept_rest
  framework_fiber -->|implements| concept_rest
  framework_flask -->|implements| concept_rest
  framework_gin -->|implements| concept_rest
  framework_grape -->|implements| concept_rest
  framework_hono -->|implements| concept_rest
  framework_koa -->|implements| concept_rest
  framework_ktor -->|implements| concept_rest
  framework_laravel -->|implements| concept_rest
  framework_nestjs -->|implements| concept_rest
  framework_net_http -->|implements| concept_rest
  framework_phoenix -->|implements| concept_rest
  framework_quarkus -->|implements| concept_rest
  framework_rails -->|implements| concept_rest
  framework_react -->|implements| concept_component
  framework_sinatra -->|implements| concept_rest
  framework_slim -->|implements| concept_rest
  framework_spring -->|implements| concept_rest
  framework_starlette -->|implements| concept_rest
  framework_symfony -->|implements| concept_rest
  framework_vapor -->|implements| concept_rest
  framework_vue -->|implements| concept_component
  concept_abstract_factory -->|references| concept_bridge
  linkStyle 708 stroke-dasharray: 4 2
  concept_abstract_factory -->|references| concept_builder
  linkStyle 709 stroke-dasharray: 4 2
  concept_abstract_factory -->|references| concept_factory
  linkStyle 710 stroke-dasharray: 4 2
  concept_active_record -->|references| concept_data_mapper
  linkStyle 711 stroke-dasharray: 4 2
  concept_active_record -->|references| concept_repository
  linkStyle 712 stroke-dasharray: 4 2
  concept_actor_model -->|references| concept_pub_sub
  linkStyle 713 stroke-dasharray: 4 2
  concept_actor_model -->|references| concept_state_machine
  linkStyle 714 stroke-dasharray: 4 2
  concept_actor_model -->|references| concept_worker_pool
  linkStyle 715 stroke-dasharray: 4 2
  concept_adapter -->|references| concept_anti_corruption_layer
  linkStyle 716 stroke-dasharray: 4 2
  concept_adapter -->|references| concept_gateway_backends
  linkStyle 717 stroke-dasharray: 4 2
  concept_adapter -->|references| concept_hexagonal
  linkStyle 718 stroke-dasharray: 4 2
  concept_aggregate -->|references| concept_ddd
  linkStyle 719 stroke-dasharray: 4 2
  concept_aggregate -->|references| concept_repository
  linkStyle 720 stroke-dasharray: 4 2
  concept_aggregate -->|references| concept_value_object
  linkStyle 721 stroke-dasharray: 4 2
  concept_anemic_domain_model -->|references| concept_ddd
  linkStyle 722 stroke-dasharray: 4 2
  concept_anti_corruption_layer -->|references| concept_adapter
  linkStyle 723 stroke-dasharray: 4 2
  concept_anti_corruption_layer -->|references| concept_gateway_backends
  linkStyle 724 stroke-dasharray: 4 2
  concept_anti_corruption_layer -->|references| concept_hexagonal
  linkStyle 725 stroke-dasharray: 4 2
  concept_api_gateway -->|references| concept_bff
  linkStyle 726 stroke-dasharray: 4 2
  concept_api_gateway -->|references| concept_rate_limiting
  linkStyle 727 stroke-dasharray: 4 2
  concept_api_gateway -->|references| concept_server_route_registration
  linkStyle 728 stroke-dasharray: 4 2
  concept_ast -->|references| concept_command
  linkStyle 729 stroke-dasharray: 4 2
  concept_ast -->|references| concept_intermediate_representation
  linkStyle 730 stroke-dasharray: 4 2
  concept_ast -->|references| concept_visitor
  linkStyle 731 stroke-dasharray: 4 2
  concept_at_least_once_delivery -->|references| concept_exactly_once_semantics
  linkStyle 732 stroke-dasharray: 4 2
  concept_at_least_once_delivery -->|references| concept_idempotent_consumer
  linkStyle 733 stroke-dasharray: 4 2
  concept_at_least_once_delivery -->|references| concept_message_queue
  linkStyle 734 stroke-dasharray: 4 2
  concept_audit_logging -->|references| concept_event_sourcing
  linkStyle 735 stroke-dasharray: 4 2
  concept_audit_logging -->|references| concept_ledger
  linkStyle 736 stroke-dasharray: 4 2
  concept_audit_logging -->|references| concept_structured_logging
  linkStyle 737 stroke-dasharray: 4 2
  concept_backpressure -->|references| concept_bulkhead
  linkStyle 738 stroke-dasharray: 4 2
  concept_backpressure -->|references| concept_competing_consumers
  linkStyle 739 stroke-dasharray: 4 2
  concept_backpressure -->|references| concept_rate_limiting
  linkStyle 740 stroke-dasharray: 4 2
  concept_batch_loader -->|references| concept_cache_aside
  linkStyle 741 stroke-dasharray: 4 2
  concept_batch_loader -->|references| concept_graphql
  linkStyle 742 stroke-dasharray: 4 2
  concept_batch_loader -->|references| concept_n_plus_one
  linkStyle 743 stroke-dasharray: 4 2
  concept_batch_processing -->|references| concept_data_pipeline
  linkStyle 744 stroke-dasharray: 4 2
  concept_batch_processing -->|references| concept_etl
  linkStyle 745 stroke-dasharray: 4 2
  concept_batch_processing -->|references| concept_scheduler
  linkStyle 746 stroke-dasharray: 4 2
  concept_bff -->|references| concept_api_gateway
  linkStyle 747 stroke-dasharray: 4 2
  concept_bff -->|references| concept_component
  linkStyle 748 stroke-dasharray: 4 2
  concept_bff -->|references| concept_rest
  linkStyle 749 stroke-dasharray: 4 2
  concept_big_ball_of_mud -->|references| concept_distributed_monolith
  linkStyle 750 stroke-dasharray: 4 2
  concept_big_ball_of_mud -->|references| concept_hexagonal
  linkStyle 751 stroke-dasharray: 4 2
  concept_big_ball_of_mud -->|references| concept_layered
  linkStyle 752 stroke-dasharray: 4 2
  concept_block_content -->|references| concept_component
  linkStyle 753 stroke-dasharray: 4 2
  concept_block_content -->|references| concept_search_index
  linkStyle 754 stroke-dasharray: 4 2
  concept_block_content -->|references| concept_versioned_document
  linkStyle 755 stroke-dasharray: 4 2
  concept_bloom_filter -->|references| concept_cache_aside
  linkStyle 756 stroke-dasharray: 4 2
  concept_bloom_filter -->|references| concept_search_index
  linkStyle 757 stroke-dasharray: 4 2
  concept_bloom_filter -->|references| concept_sharding
  linkStyle 758 stroke-dasharray: 4 2
  concept_blue_green -->|references| concept_canary
  linkStyle 759 stroke-dasharray: 4 2
  concept_blue_green -->|references| concept_database_migration
  linkStyle 760 stroke-dasharray: 4 2
  concept_blue_green -->|references| concept_feature_flag
  linkStyle 761 stroke-dasharray: 4 2
  concept_boolean_blindness -->|references| concept_command
  linkStyle 762 stroke-dasharray: 4 2
  concept_boolean_blindness -->|references| concept_primitive_obsession
  linkStyle 763 stroke-dasharray: 4 2
  concept_boolean_blindness -->|references| concept_strategy
  linkStyle 764 stroke-dasharray: 4 2
  concept_bounded_context -->|references| concept_anti_corruption_layer
  linkStyle 765 stroke-dasharray: 4 2
  concept_bounded_context -->|references| concept_database_per_service
  linkStyle 766 stroke-dasharray: 4 2
  concept_bounded_context -->|references| concept_ddd
  linkStyle 767 stroke-dasharray: 4 2
  concept_breaking_changes -->|references| concept_contract_testing
  linkStyle 768 stroke-dasharray: 4 2
  concept_breaking_changes -->|references| concept_grpc
  linkStyle 769 stroke-dasharray: 4 2
  concept_breaking_changes -->|references| concept_rest
  linkStyle 770 stroke-dasharray: 4 2
  concept_bridge -->|references| concept_abstract_factory
  linkStyle 771 stroke-dasharray: 4 2
  concept_bridge -->|references| concept_adapter
  linkStyle 772 stroke-dasharray: 4 2
  concept_bridge -->|references| concept_strategy
  linkStyle 773 stroke-dasharray: 4 2
  concept_builder -->|references| concept_abstract_factory
  linkStyle 774 stroke-dasharray: 4 2
  concept_builder -->|references| concept_factory
  linkStyle 775 stroke-dasharray: 4 2
  concept_builder -->|references| concept_fixture_builder
  linkStyle 776 stroke-dasharray: 4 2
  concept_bulkhead -->|references| concept_backpressure
  linkStyle 777 stroke-dasharray: 4 2
  concept_bulkhead -->|references| concept_circuit_breaker
  linkStyle 778 stroke-dasharray: 4 2
  concept_bulkhead -->|references| concept_connection_pooling
  linkStyle 779 stroke-dasharray: 4 2
  concept_busy_waiting -->|references| concept_backpressure
  linkStyle 780 stroke-dasharray: 4 2
  concept_busy_waiting -->|references| concept_long_polling
  linkStyle 781 stroke-dasharray: 4 2
  concept_busy_waiting -->|references| concept_polling_flow
  linkStyle 782 stroke-dasharray: 4 2
  concept_cache_aside -->|references| concept_repository
  linkStyle 783 stroke-dasharray: 4 2
  concept_cache_aside -->|references| concept_search_index
  linkStyle 784 stroke-dasharray: 4 2
  concept_cache_aside -->|references| concept_write_behind
  linkStyle 785 stroke-dasharray: 4 2
  concept_cache_stampede_prevention -->|references| concept_backpressure
  linkStyle 786 stroke-dasharray: 4 2
  concept_cache_stampede_prevention -->|references| concept_bulkhead
  linkStyle 787 stroke-dasharray: 4 2
  concept_cache_stampede_prevention -->|references| concept_cache_aside
  linkStyle 788 stroke-dasharray: 4 2
  concept_callback_hell -->|references| concept_future_promise
  linkStyle 789 stroke-dasharray: 4 2
  concept_callback_hell -->|references| concept_mediator
  linkStyle 790 stroke-dasharray: 4 2
  concept_callback_hell -->|references| concept_reactor
  linkStyle 791 stroke-dasharray: 4 2
  concept_canary -->|references| concept_blue_green
  linkStyle 792 stroke-dasharray: 4 2
  concept_canary -->|references| concept_feature_flag
  linkStyle 793 stroke-dasharray: 4 2
  concept_canary -->|references| concept_health_check
  linkStyle 794 stroke-dasharray: 4 2
  concept_cargo_cult -->|references| concept_copy_paste_programming
  linkStyle 795 stroke-dasharray: 4 2
  concept_cargo_cult -->|references| concept_golden_hammer
  linkStyle 796 stroke-dasharray: 4 2
  concept_cargo_cult -->|references| concept_premature_optimization
  linkStyle 797 stroke-dasharray: 4 2
  concept_catalog -->|references| concept_rule_engine
  linkStyle 798 stroke-dasharray: 4 2
  concept_catalog -->|references| concept_search_index
  linkStyle 799 stroke-dasharray: 4 2
  concept_catalog -->|references| concept_subscription
  linkStyle 800 stroke-dasharray: 4 2
  concept_cell_based -->|references| concept_canary
  linkStyle 801 stroke-dasharray: 4 2
  concept_cell_based -->|references| concept_sharding
  linkStyle 802 stroke-dasharray: 4 2
  concept_cell_based -->|references| concept_tenant_isolation
  linkStyle 803 stroke-dasharray: 4 2
  concept_chain_of_responsibility -->|references| concept_command
  linkStyle 804 stroke-dasharray: 4 2
  concept_chain_of_responsibility -->|references| concept_middleware
  linkStyle 805 stroke-dasharray: 4 2
  concept_chain_of_responsibility -->|references| concept_rule_engine
  linkStyle 806 stroke-dasharray: 4 2
  concept_change_data_capture -->|references| concept_cqrs
  linkStyle 807 stroke-dasharray: 4 2
  concept_change_data_capture -->|references| concept_event_sourcing
  linkStyle 808 stroke-dasharray: 4 2
  concept_change_data_capture -->|references| concept_search_index
  linkStyle 809 stroke-dasharray: 4 2
  concept_chatty_api -->|references| concept_batch_loader
  linkStyle 810 stroke-dasharray: 4 2
  concept_chatty_api -->|references| concept_bff
  linkStyle 811 stroke-dasharray: 4 2
  concept_chatty_api -->|references| concept_graphql
  linkStyle 812 stroke-dasharray: 4 2
  concept_choreography -->|references| concept_event_driven
  linkStyle 813 stroke-dasharray: 4 2
  concept_choreography -->|references| concept_orchestration
  linkStyle 814 stroke-dasharray: 4 2
  concept_choreography -->|references| concept_saga
  linkStyle 815 stroke-dasharray: 4 2
  concept_circuit_breaker -->|references| concept_bulkhead
  linkStyle 816 stroke-dasharray: 4 2
  concept_circuit_breaker -->|references| concept_retry
  linkStyle 817 stroke-dasharray: 4 2
  concept_circuit_breaker -->|references| concept_timeout
  linkStyle 818 stroke-dasharray: 4 2
  concept_circular_dependency -->|references| concept_dependency_injection
  linkStyle 819 stroke-dasharray: 4 2
  concept_circular_dependency -->|references| concept_layered
  linkStyle 820 stroke-dasharray: 4 2
  concept_circular_dependency -->|references| concept_modular_monolith
  linkStyle 821 stroke-dasharray: 4 2
  concept_claim_check -->|references| concept_dead_letter
  linkStyle 822 stroke-dasharray: 4 2
  concept_claim_check -->|references| concept_message_queue
  linkStyle 823 stroke-dasharray: 4 2
  concept_claim_check -->|references| concept_webhook
  linkStyle 824 stroke-dasharray: 4 2
  concept_command -->|references| concept_cqrs
  linkStyle 825 stroke-dasharray: 4 2
  concept_command -->|references| concept_event_driven
  linkStyle 826 stroke-dasharray: 4 2
  concept_command -->|references| concept_workflow_engine
  linkStyle 827 stroke-dasharray: 4 2
  concept_competing_consumers -->|references| concept_dead_letter
  linkStyle 828 stroke-dasharray: 4 2
  concept_competing_consumers -->|references| concept_outbox
  linkStyle 829 stroke-dasharray: 4 2
  concept_competing_consumers -->|references| concept_worker_pool
  linkStyle 830 stroke-dasharray: 4 2
  concept_component_slot -->|references| concept_component
  linkStyle 831 stroke-dasharray: 4 2
  concept_composite -->|references| concept_component
  linkStyle 832 stroke-dasharray: 4 2
  concept_composite -->|references| concept_graph
  linkStyle 833 stroke-dasharray: 4 2
  concept_composite -->|references| concept_visitor
  linkStyle 834 stroke-dasharray: 4 2
  concept_config_management -->|references| concept_config_sprawl
  linkStyle 835 stroke-dasharray: 4 2
  concept_config_management -->|references| concept_feature_flag
  linkStyle 836 stroke-dasharray: 4 2
  concept_config_management -->|references| concept_secret_management
  linkStyle 837 stroke-dasharray: 4 2
  concept_config_sprawl -->|references| concept_config_management
  linkStyle 838 stroke-dasharray: 4 2
  concept_connection_pooling -->|references| concept_bulkhead
  linkStyle 839 stroke-dasharray: 4 2
  concept_connection_pooling -->|references| concept_distributed_lock
  linkStyle 840 stroke-dasharray: 4 2
  concept_connection_pooling -->|references| concept_health_check
  linkStyle 841 stroke-dasharray: 4 2
  concept_content_negotiation -->|references| concept_graphql
  linkStyle 842 stroke-dasharray: 4 2
  concept_content_negotiation -->|references| concept_rest
  linkStyle 843 stroke-dasharray: 4 2
  concept_content_negotiation -->|references| concept_server_route_registration
  linkStyle 844 stroke-dasharray: 4 2
  concept_contract_testing -->|references| concept_api_gateway
  linkStyle 845 stroke-dasharray: 4 2
  concept_contract_testing -->|references| concept_grpc
  linkStyle 846 stroke-dasharray: 4 2
  concept_contract_testing -->|references| concept_rest
  linkStyle 847 stroke-dasharray: 4 2
  concept_control_plane -->|references| concept_data_plane
  linkStyle 848 stroke-dasharray: 4 2
  concept_control_plane -->|references| concept_service_discovery
  linkStyle 849 stroke-dasharray: 4 2
  concept_control_plane -->|references| concept_service_mesh
  linkStyle 850 stroke-dasharray: 4 2
  concept_conversation_thread -->|references| concept_pagination
  linkStyle 851 stroke-dasharray: 4 2
  concept_conversation_thread -->|references| concept_pub_sub
  linkStyle 852 stroke-dasharray: 4 2
  concept_conversation_thread -->|references| concept_websocket
  linkStyle 853 stroke-dasharray: 4 2
  concept_copy_paste_programming -->|references| concept_cargo_cult
  linkStyle 854 stroke-dasharray: 4 2
  concept_copy_paste_programming -->|references| concept_fixture_builder
  linkStyle 855 stroke-dasharray: 4 2
  concept_copy_paste_programming -->|references| concept_shotgun_surgery
  linkStyle 856 stroke-dasharray: 4 2
  concept_correlation_id -->|references| concept_distributed_tracing
  linkStyle 857 stroke-dasharray: 4 2
  concept_cors -->|references| concept_api_gateway
  linkStyle 858 stroke-dasharray: 4 2
  concept_cors -->|references| concept_oauth_oidc
  linkStyle 859 stroke-dasharray: 4 2
  concept_cors -->|references| concept_token_auth
  linkStyle 860 stroke-dasharray: 4 2
  concept_cqrs -->|references| concept_change_data_capture
  linkStyle 861 stroke-dasharray: 4 2
  concept_cqrs -->|references| concept_event_sourcing
  linkStyle 862 stroke-dasharray: 4 2
  concept_cqrs -->|references| concept_search_index
  linkStyle 863 stroke-dasharray: 4 2
  concept_data_mapper -->|references| concept_active_record
  linkStyle 864 stroke-dasharray: 4 2
  concept_data_mapper -->|references| concept_repository
  linkStyle 865 stroke-dasharray: 4 2
  concept_data_mapper -->|references| concept_unit_of_work
  linkStyle 866 stroke-dasharray: 4 2
  concept_data_pipeline -->|references| concept_batch_processing
  linkStyle 867 stroke-dasharray: 4 2
  concept_data_pipeline -->|references| concept_etl
  linkStyle 868 stroke-dasharray: 4 2
  concept_data_pipeline -->|references| concept_stream_to_store
  linkStyle 869 stroke-dasharray: 4 2
  concept_data_plane -->|references| concept_control_plane
  linkStyle 870 stroke-dasharray: 4 2
  concept_data_plane -->|references| concept_service_mesh
  linkStyle 871 stroke-dasharray: 4 2
  concept_data_plane -->|references| concept_sidecar
  linkStyle 872 stroke-dasharray: 4 2
  concept_database_migration -->|references| concept_config_management
  linkStyle 873 stroke-dasharray: 4 2
  concept_database_migration -->|references| concept_database_per_service
  linkStyle 874 stroke-dasharray: 4 2
  concept_database_migration -->|references| concept_schema_registry
  linkStyle 875 stroke-dasharray: 4 2
  concept_database_per_service -->|references| concept_bounded_context
  linkStyle 876 stroke-dasharray: 4 2
  concept_database_per_service -->|references| concept_microservices
  linkStyle 877 stroke-dasharray: 4 2
  concept_database_per_service -->|references| concept_shared_database
  linkStyle 878 stroke-dasharray: 4 2
  concept_ddd -->|references| concept_aggregate
  linkStyle 879 stroke-dasharray: 4 2
  concept_ddd -->|references| concept_repository
  linkStyle 880 stroke-dasharray: 4 2
  concept_ddd -->|references| concept_value_object
  linkStyle 881 stroke-dasharray: 4 2
  concept_dead_letter -->|references| concept_claim_check
  linkStyle 882 stroke-dasharray: 4 2
  concept_dead_letter -->|references| concept_competing_consumers
  linkStyle 883 stroke-dasharray: 4 2
  concept_dead_letter -->|references| concept_retry
  linkStyle 884 stroke-dasharray: 4 2
  concept_deadlock -->|references| concept_distributed_lock
  linkStyle 885 stroke-dasharray: 4 2
  concept_deadlock -->|references| concept_race_condition
  linkStyle 886 stroke-dasharray: 4 2
  concept_deadlock -->|references| concept_read_write_lock
  linkStyle 887 stroke-dasharray: 4 2
  concept_decorator -->|references| concept_proxy
  linkStyle 888 stroke-dasharray: 4 2
  concept_deep_nesting -->|references| concept_callback_hell
  linkStyle 889 stroke-dasharray: 4 2
  concept_deep_nesting -->|references| concept_strategy
  linkStyle 890 stroke-dasharray: 4 2
  concept_deep_nesting -->|references| concept_train_wreck
  linkStyle 891 stroke-dasharray: 4 2
  concept_distributed_lock -->|references| concept_idempotent_consumer
  linkStyle 892 stroke-dasharray: 4 2
  concept_distributed_lock -->|references| concept_leader_election
  linkStyle 893 stroke-dasharray: 4 2
  concept_distributed_lock -->|references| concept_optimistic_locking
  linkStyle 894 stroke-dasharray: 4 2
  concept_distributed_monolith -->|references| concept_api_gateway
  linkStyle 895 stroke-dasharray: 4 2
  concept_distributed_monolith -->|references| concept_microservices
  linkStyle 896 stroke-dasharray: 4 2
  concept_distributed_monolith -->|references| concept_shared_database
  linkStyle 897 stroke-dasharray: 4 2
  concept_distributed_tracing -->|references| concept_correlation_id
  linkStyle 898 stroke-dasharray: 4 2
  concept_distributed_tracing -->|references| concept_metrics_instrumentation
  linkStyle 899 stroke-dasharray: 4 2
  concept_distributed_tracing -->|references| concept_structured_logging
  linkStyle 900 stroke-dasharray: 4 2
  concept_dual_writes -->|references| concept_change_data_capture
  linkStyle 901 stroke-dasharray: 4 2
  concept_dual_writes -->|references| concept_outbox
  linkStyle 902 stroke-dasharray: 4 2
  concept_entity_component_system -->|references| concept_component
  linkStyle 903 stroke-dasharray: 4 2
  concept_entity_component_system -->|references| concept_game_loop
  linkStyle 904 stroke-dasharray: 4 2
  concept_entity_component_system -->|references| concept_tick_simulation
  linkStyle 905 stroke-dasharray: 4 2
  concept_environment_parity_gap -->|references| concept_config_management
  linkStyle 906 stroke-dasharray: 4 2
  concept_environment_parity_gap -->|references| concept_flaky_tests
  linkStyle 907 stroke-dasharray: 4 2
  concept_environment_parity_gap -->|references| concept_infrastructure_as_code
  linkStyle 908 stroke-dasharray: 4 2
  concept_error_boundary -->|references| concept_component
  linkStyle 909 stroke-dasharray: 4 2
  concept_error_boundary -->|references| concept_graceful_degradation
  linkStyle 910 stroke-dasharray: 4 2
  concept_error_boundary -->|references| concept_suspense_boundary
  linkStyle 911 stroke-dasharray: 4 2
  concept_error_code_returns -->|references| concept_magic_numbers
  linkStyle 912 stroke-dasharray: 4 2
  concept_error_code_returns -->|references| concept_result_type
  linkStyle 913 stroke-dasharray: 4 2
  concept_error_code_returns -->|references| concept_swallowed_exception
  linkStyle 914 stroke-dasharray: 4 2
  concept_etl -->|references| concept_batch_processing
  linkStyle 915 stroke-dasharray: 4 2
  concept_etl -->|references| concept_data_pipeline
  linkStyle 916 stroke-dasharray: 4 2
  concept_etl -->|references| concept_schema_on_read
  linkStyle 917 stroke-dasharray: 4 2
  concept_event_carried_state -->|references| concept_change_data_capture
  linkStyle 918 stroke-dasharray: 4 2
  concept_event_carried_state -->|references| concept_event_driven
  linkStyle 919 stroke-dasharray: 4 2
  concept_event_carried_state -->|references| concept_event_notification
  linkStyle 920 stroke-dasharray: 4 2
  concept_event_driven -->|references| concept_choreography
  linkStyle 921 stroke-dasharray: 4 2
  concept_event_driven -->|references| concept_event_sourcing
  linkStyle 922 stroke-dasharray: 4 2
  concept_event_driven -->|references| concept_pub_sub
  linkStyle 923 stroke-dasharray: 4 2
  concept_event_log -->|references| concept_audit_logging
  linkStyle 924 stroke-dasharray: 4 2
  concept_event_log -->|references| concept_event_sourcing
  linkStyle 925 stroke-dasharray: 4 2
  concept_event_log -->|references| concept_ledger
  linkStyle 926 stroke-dasharray: 4 2
  concept_event_notification -->|references| concept_event_carried_state
  linkStyle 927 stroke-dasharray: 4 2
  concept_event_notification -->|references| concept_event_driven
  linkStyle 928 stroke-dasharray: 4 2
  concept_event_notification -->|references| concept_webhook
  linkStyle 929 stroke-dasharray: 4 2
  concept_event_sourcing -->|references| concept_event_driven
  linkStyle 930 stroke-dasharray: 4 2
  concept_event_sourcing -->|references| concept_ledger
  linkStyle 931 stroke-dasharray: 4 2
  concept_event_sourcing -->|references| concept_versioned_document
  linkStyle 932 stroke-dasharray: 4 2
  concept_eventual_consistency -->|references| concept_cqrs
  linkStyle 933 stroke-dasharray: 4 2
  concept_eventual_consistency -->|references| concept_dual_writes
  linkStyle 934 stroke-dasharray: 4 2
  concept_eventual_consistency -->|references| concept_optimistic_update
  linkStyle 935 stroke-dasharray: 4 2
  concept_exactly_once_semantics -->|references| concept_at_least_once_delivery
  linkStyle 936 stroke-dasharray: 4 2
  concept_exactly_once_semantics -->|references| concept_idempotent_consumer
  linkStyle 937 stroke-dasharray: 4 2
  concept_exactly_once_semantics -->|references| concept_outbox
  linkStyle 938 stroke-dasharray: 4 2
  concept_experiment_framework -->|references| concept_feature_flag
  linkStyle 939 stroke-dasharray: 4 2
  concept_experiment_framework -->|references| concept_metrics_instrumentation
  linkStyle 940 stroke-dasharray: 4 2
  concept_experiment_framework -->|references| concept_model_registry
  linkStyle 941 stroke-dasharray: 4 2
  concept_facade -->|references| concept_adapter
  linkStyle 942 stroke-dasharray: 4 2
  concept_facade -->|references| concept_anti_corruption_layer
  linkStyle 943 stroke-dasharray: 4 2
  concept_facade -->|references| concept_gateway_backends
  linkStyle 944 stroke-dasharray: 4 2
  concept_factory -->|references| concept_abstract_factory
  linkStyle 945 stroke-dasharray: 4 2
  concept_factory -->|references| concept_builder
  linkStyle 946 stroke-dasharray: 4 2
  concept_factory -->|references| concept_strategy
  linkStyle 947 stroke-dasharray: 4 2
  concept_failure_cascade -->|references| concept_bulkhead
  linkStyle 948 stroke-dasharray: 4 2
  concept_failure_cascade -->|references| concept_circuit_breaker
  linkStyle 949 stroke-dasharray: 4 2
  concept_failure_cascade -->|references| concept_graceful_degradation
  linkStyle 950 stroke-dasharray: 4 2
  concept_fallback -->|references| concept_cache_aside
  linkStyle 951 stroke-dasharray: 4 2
  concept_fallback -->|references| concept_circuit_breaker
  linkStyle 952 stroke-dasharray: 4 2
  concept_fallback -->|references| concept_graceful_degradation
  linkStyle 953 stroke-dasharray: 4 2
  concept_fan_in -->|references| concept_data_pipeline
  linkStyle 954 stroke-dasharray: 4 2
  concept_fan_in -->|references| concept_mapreduce
  linkStyle 955 stroke-dasharray: 4 2
  concept_fan_in -->|references| concept_scatter_gather
  linkStyle 956 stroke-dasharray: 4 2
  concept_fan_out -->|references| concept_pub_sub
  linkStyle 957 stroke-dasharray: 4 2
  concept_fan_out -->|references| concept_scatter_gather
  linkStyle 958 stroke-dasharray: 4 2
  concept_fan_out -->|references| concept_webhook
  linkStyle 959 stroke-dasharray: 4 2
  concept_feature_envy -->|references| concept_data_mapper
  linkStyle 960 stroke-dasharray: 4 2
  concept_feature_envy -->|references| concept_god_object
  linkStyle 961 stroke-dasharray: 4 2
  concept_feature_envy -->|references| concept_primitive_obsession
  linkStyle 962 stroke-dasharray: 4 2
  concept_feature_flag -->|references| concept_blue_green
  linkStyle 963 stroke-dasharray: 4 2
  concept_feature_flag -->|references| concept_canary
  linkStyle 964 stroke-dasharray: 4 2
  concept_feature_flag -->|references| concept_config_management
  linkStyle 965 stroke-dasharray: 4 2
  concept_feature_store -->|references| concept_model_registry
  linkStyle 966 stroke-dasharray: 4 2
  concept_feature_store -->|references| concept_stream_to_store
  linkStyle 967 stroke-dasharray: 4 2
  concept_feature_store -->|references| concept_training_pipeline
  linkStyle 968 stroke-dasharray: 4 2
  concept_fire_and_forget -->|references| concept_outbox
  linkStyle 969 stroke-dasharray: 4 2
  concept_fixture_builder -->|references| concept_builder
  linkStyle 970 stroke-dasharray: 4 2
  concept_fixture_builder -->|references| concept_property_testing
  linkStyle 971 stroke-dasharray: 4 2
  concept_fixture_builder -->|references| concept_test_doubles
  linkStyle 972 stroke-dasharray: 4 2
  concept_flaky_tests -->|references| concept_environment_parity_gap
  linkStyle 973 stroke-dasharray: 4 2
  concept_flaky_tests -->|references| concept_snapshot_testing
  linkStyle 974 stroke-dasharray: 4 2
  concept_flaky_tests -->|references| concept_test_pollution
  linkStyle 975 stroke-dasharray: 4 2
  concept_flux -->|references| concept_component
  linkStyle 976 stroke-dasharray: 4 2
  concept_flux -->|references| concept_prop_drilling
  linkStyle 977 stroke-dasharray: 4 2
  concept_flux -->|references| concept_reactive_store
  linkStyle 978 stroke-dasharray: 4 2
  concept_flyweight -->|references| concept_object_pool
  linkStyle 979 stroke-dasharray: 4 2
  concept_flyweight -->|references| concept_prototype
  linkStyle 980 stroke-dasharray: 4 2
  concept_flyweight -->|references| concept_value_object
  linkStyle 981 stroke-dasharray: 4 2
  concept_form_binding -->|references| concept_component
  linkStyle 982 stroke-dasharray: 4 2
  concept_form_binding -->|references| concept_input_validation
  linkStyle 983 stroke-dasharray: 4 2
  concept_form_binding -->|references| concept_reactive_store
  linkStyle 984 stroke-dasharray: 4 2
  concept_future_promise -->|references| concept_callback_hell
  linkStyle 985 stroke-dasharray: 4 2
  concept_future_promise -->|references| concept_reactor
  linkStyle 986 stroke-dasharray: 4 2
  concept_future_promise -->|references| concept_request_reply
  linkStyle 987 stroke-dasharray: 4 2
  concept_game_loop -->|references| concept_entity_component_system
  linkStyle 988 stroke-dasharray: 4 2
  concept_game_loop -->|references| concept_reactor
  linkStyle 989 stroke-dasharray: 4 2
  concept_game_loop -->|references| concept_tick_simulation
  linkStyle 990 stroke-dasharray: 4 2
  concept_gateway_backends -->|references| concept_api_gateway
  linkStyle 991 stroke-dasharray: 4 2
  concept_gateway_backends -->|references| concept_bff
  linkStyle 992 stroke-dasharray: 4 2
  concept_gateway_backends -->|references| concept_microservices
  linkStyle 993 stroke-dasharray: 4 2
  concept_gitops -->|references| concept_config_management
  linkStyle 994 stroke-dasharray: 4 2
  concept_gitops -->|references| concept_immutable_infra
  linkStyle 995 stroke-dasharray: 4 2
  concept_gitops -->|references| concept_infrastructure_as_code
  linkStyle 996 stroke-dasharray: 4 2
  concept_god_endpoint -->|references| concept_bff
  linkStyle 997 stroke-dasharray: 4 2
  concept_god_endpoint -->|references| concept_god_object
  linkStyle 998 stroke-dasharray: 4 2
  concept_god_endpoint -->|references| concept_rest
  linkStyle 999 stroke-dasharray: 4 2
  concept_god_object -->|references| concept_big_ball_of_mud
  linkStyle 1000 stroke-dasharray: 4 2
  concept_god_object -->|references| concept_feature_envy
  linkStyle 1001 stroke-dasharray: 4 2
  concept_god_object -->|references| concept_god_endpoint
  linkStyle 1002 stroke-dasharray: 4 2
  concept_golden_hammer -->|references| concept_cargo_cult
  linkStyle 1003 stroke-dasharray: 4 2
  concept_golden_hammer -->|references| concept_premature_optimization
  linkStyle 1004 stroke-dasharray: 4 2
  concept_golden_hammer -->|references| concept_reinventing_the_wheel
  linkStyle 1005 stroke-dasharray: 4 2
  concept_graceful_degradation -->|references| concept_circuit_breaker
  linkStyle 1006 stroke-dasharray: 4 2
  concept_graceful_degradation -->|references| concept_fallback
  linkStyle 1007 stroke-dasharray: 4 2
  concept_graceful_degradation -->|references| concept_health_check
  linkStyle 1008 stroke-dasharray: 4 2
  concept_graph -->|references| concept_pipeline_filter
  linkStyle 1009 stroke-dasharray: 4 2
  concept_graph -->|references| concept_workflow_engine
  linkStyle 1010 stroke-dasharray: 4 2
  concept_graphql -->|references| concept_pagination
  linkStyle 1011 stroke-dasharray: 4 2
  concept_graphql -->|references| concept_rest
  linkStyle 1012 stroke-dasharray: 4 2
  concept_grpc -->|references| concept_rest
  linkStyle 1013 stroke-dasharray: 4 2
  concept_grpc -->|references| concept_server_route_registration
  linkStyle 1014 stroke-dasharray: 4 2
  concept_hardcoded_credentials -->|references| concept_secret_management
  linkStyle 1015 stroke-dasharray: 4 2
  concept_hardcoded_urls -->|references| concept_config_management
  linkStyle 1016 stroke-dasharray: 4 2
  concept_health_check -->|references| concept_canary
  linkStyle 1017 stroke-dasharray: 4 2
  concept_health_check -->|references| concept_graceful_degradation
  linkStyle 1018 stroke-dasharray: 4 2
  concept_health_check -->|references| concept_leader_election
  linkStyle 1019 stroke-dasharray: 4 2
  concept_hexagonal -->|references| concept_adapter
  linkStyle 1020 stroke-dasharray: 4 2
  concept_hexagonal -->|references| concept_anti_corruption_layer
  linkStyle 1021 stroke-dasharray: 4 2
  concept_hexagonal -->|references| concept_layered
  linkStyle 1022 stroke-dasharray: 4 2
  concept_hidden_side_effects -->|references| concept_command
  linkStyle 1023 stroke-dasharray: 4 2
  concept_hidden_side_effects -->|references| concept_log_and_throw
  linkStyle 1024 stroke-dasharray: 4 2
  concept_hidden_side_effects -->|references| concept_query_object
  linkStyle 1025 stroke-dasharray: 4 2
  concept_hydration -->|references| concept_lazy_loading
  linkStyle 1026 stroke-dasharray: 4 2
  concept_hydration -->|references| concept_server_prefetch
  linkStyle 1027 stroke-dasharray: 4 2
  concept_hydration -->|references| concept_suspense_boundary
  linkStyle 1028 stroke-dasharray: 4 2
  concept_ice_cream_cone -->|references| concept_contract_testing
  linkStyle 1029 stroke-dasharray: 4 2
  concept_ice_cream_cone -->|references| concept_fixture_builder
  linkStyle 1030 stroke-dasharray: 4 2
  concept_ice_cream_cone -->|references| concept_flaky_tests
  linkStyle 1031 stroke-dasharray: 4 2
  concept_idempotent_consumer -->|references| concept_dead_letter
  linkStyle 1032 stroke-dasharray: 4 2
  concept_idempotent_consumer -->|references| concept_inbox
  linkStyle 1033 stroke-dasharray: 4 2
  concept_idempotent_consumer -->|references| concept_retry
  linkStyle 1034 stroke-dasharray: 4 2
  concept_immutable_infra -->|references| concept_blue_green
  linkStyle 1035 stroke-dasharray: 4 2
  concept_immutable_infra -->|references| concept_gitops
  linkStyle 1036 stroke-dasharray: 4 2
  concept_immutable_infra -->|references| concept_infrastructure_as_code
  linkStyle 1037 stroke-dasharray: 4 2
  concept_inbox -->|references| concept_dead_letter
  linkStyle 1038 stroke-dasharray: 4 2
  concept_inbox -->|references| concept_idempotent_consumer
  linkStyle 1039 stroke-dasharray: 4 2
  concept_inbox -->|references| concept_outbox
  linkStyle 1040 stroke-dasharray: 4 2
  concept_inconsistent_naming -->|references| concept_magic_numbers
  linkStyle 1041 stroke-dasharray: 4 2
  concept_inconsistent_naming -->|references| concept_misleading_names
  linkStyle 1042 stroke-dasharray: 4 2
  concept_inconsistent_naming -->|references| concept_stringly_typed
  linkStyle 1043 stroke-dasharray: 4 2
  concept_infrastructure_as_code -->|references| concept_config_management
  linkStyle 1044 stroke-dasharray: 4 2
  concept_infrastructure_as_code -->|references| concept_gitops
  linkStyle 1045 stroke-dasharray: 4 2
  concept_infrastructure_as_code -->|references| concept_immutable_infra
  linkStyle 1046 stroke-dasharray: 4 2
  concept_input_validation -->|references| concept_cors
  linkStyle 1047 stroke-dasharray: 4 2
  concept_input_validation -->|references| concept_insecure_deserialization
  linkStyle 1048 stroke-dasharray: 4 2
  concept_input_validation -->|references| concept_route_guard
  linkStyle 1049 stroke-dasharray: 4 2
  concept_insecure_deserialization -->|references| concept_input_validation
  linkStyle 1050 stroke-dasharray: 4 2
  concept_insecure_deserialization -->|references| concept_route_guard
  linkStyle 1051 stroke-dasharray: 4 2
  concept_insecure_deserialization -->|references| concept_sql_injection
  linkStyle 1052 stroke-dasharray: 4 2
  concept_intermediate_representation -->|references| concept_ast
  linkStyle 1053 stroke-dasharray: 4 2
  concept_intermediate_representation -->|references| concept_lexer_parser
  linkStyle 1054 stroke-dasharray: 4 2
  concept_intermediate_representation -->|references| concept_visitor
  linkStyle 1055 stroke-dasharray: 4 2
  concept_iterator -->|references| concept_composite
  linkStyle 1056 stroke-dasharray: 4 2
  concept_iterator -->|references| concept_stream_to_store
  linkStyle 1057 stroke-dasharray: 4 2
  concept_iterator -->|references| concept_visitor
  linkStyle 1058 stroke-dasharray: 4 2
  concept_key_value_model -->|references| concept_cache_aside
  linkStyle 1059 stroke-dasharray: 4 2
  concept_key_value_model -->|references| concept_lru_cache
  linkStyle 1060 stroke-dasharray: 4 2
  concept_key_value_model -->|references| concept_read_through
  linkStyle 1061 stroke-dasharray: 4 2
  concept_lava_flow -->|references| concept_copy_paste_programming
  linkStyle 1062 stroke-dasharray: 4 2
  concept_lava_flow -->|references| concept_feature_flag
  linkStyle 1063 stroke-dasharray: 4 2
  concept_lava_flow -->|references| concept_shotgun_surgery
  linkStyle 1064 stroke-dasharray: 4 2
  concept_layered -->|references| concept_middleware
  linkStyle 1065 stroke-dasharray: 4 2
  concept_layered -->|references| concept_mvc
  linkStyle 1066 stroke-dasharray: 4 2
  concept_layered -->|references| concept_mvvm
  linkStyle 1067 stroke-dasharray: 4 2
  concept_lazy_loading -->|references| concept_micro_frontend
  linkStyle 1068 stroke-dasharray: 4 2
  concept_lazy_loading -->|references| concept_server_prefetch
  linkStyle 1069 stroke-dasharray: 4 2
  concept_lazy_loading -->|references| concept_suspense_boundary
  linkStyle 1070 stroke-dasharray: 4 2
  concept_leader_election -->|references| concept_distributed_lock
  linkStyle 1071 stroke-dasharray: 4 2
  concept_leader_election -->|references| concept_health_check
  linkStyle 1072 stroke-dasharray: 4 2
  concept_leader_election -->|references| concept_scheduler
  linkStyle 1073 stroke-dasharray: 4 2
  concept_leaky_abstraction -->|references| concept_adapter
  linkStyle 1074 stroke-dasharray: 4 2
  concept_leaky_abstraction -->|references| concept_data_mapper
  linkStyle 1075 stroke-dasharray: 4 2
  concept_leaky_abstraction -->|references| concept_hexagonal
  linkStyle 1076 stroke-dasharray: 4 2
  concept_ledger -->|references| concept_audit_logging
  linkStyle 1077 stroke-dasharray: 4 2
  concept_ledger -->|references| concept_event_sourcing
  linkStyle 1078 stroke-dasharray: 4 2
  concept_ledger -->|references| concept_saga
  linkStyle 1079 stroke-dasharray: 4 2
  concept_lexer_parser -->|references| concept_ast
  linkStyle 1080 stroke-dasharray: 4 2
  concept_lexer_parser -->|references| concept_intermediate_representation
  linkStyle 1081 stroke-dasharray: 4 2
  concept_lexer_parser -->|references| concept_visitor
  linkStyle 1082 stroke-dasharray: 4 2
  concept_load_balancer -->|references| concept_api_gateway
  linkStyle 1083 stroke-dasharray: 4 2
  concept_load_balancer -->|references| concept_rate_limiting
  linkStyle 1084 stroke-dasharray: 4 2
  concept_load_balancer -->|references| concept_service_discovery
  linkStyle 1085 stroke-dasharray: 4 2
  concept_log_and_throw -->|references| concept_correlation_id
  linkStyle 1086 stroke-dasharray: 4 2
  concept_log_and_throw -->|references| concept_structured_logging
  linkStyle 1087 stroke-dasharray: 4 2
  concept_log_and_throw -->|references| concept_swallowed_exception
  linkStyle 1088 stroke-dasharray: 4 2
  concept_log_spam -->|references| concept_metrics_instrumentation
  linkStyle 1089 stroke-dasharray: 4 2
  concept_log_spam -->|references| concept_missing_log_context
  linkStyle 1090 stroke-dasharray: 4 2
  concept_log_spam -->|references| concept_structured_logging
  linkStyle 1091 stroke-dasharray: 4 2
  concept_long_polling -->|references| concept_polling_flow
  linkStyle 1092 stroke-dasharray: 4 2
  concept_long_polling -->|references| concept_server_sent_events
  linkStyle 1093 stroke-dasharray: 4 2
  concept_long_polling -->|references| concept_websocket
  linkStyle 1094 stroke-dasharray: 4 2
  concept_long_transactions -->|references| concept_distributed_lock
  linkStyle 1095 stroke-dasharray: 4 2
  concept_long_transactions -->|references| concept_outbox
  linkStyle 1096 stroke-dasharray: 4 2
  concept_long_transactions -->|references| concept_unit_of_work
  linkStyle 1097 stroke-dasharray: 4 2
  concept_lru_cache -->|references| concept_cache_aside
  linkStyle 1098 stroke-dasharray: 4 2
  concept_lru_cache -->|references| concept_key_value_model
  linkStyle 1099 stroke-dasharray: 4 2
  concept_lru_cache -->|references| concept_read_through
  linkStyle 1100 stroke-dasharray: 4 2
  concept_magic_numbers -->|references| concept_boolean_blindness
  linkStyle 1101 stroke-dasharray: 4 2
  concept_magic_numbers -->|references| concept_inconsistent_naming
  linkStyle 1102 stroke-dasharray: 4 2
  concept_magic_numbers -->|references| concept_stringly_typed
  linkStyle 1103 stroke-dasharray: 4 2
  concept_mapreduce -->|references| concept_data_pipeline
  linkStyle 1104 stroke-dasharray: 4 2
  concept_mapreduce -->|references| concept_fan_in
  linkStyle 1105 stroke-dasharray: 4 2
  concept_mapreduce -->|references| concept_fan_out
  linkStyle 1106 stroke-dasharray: 4 2
  concept_materialized_view -->|references| concept_cache_aside
  linkStyle 1107 stroke-dasharray: 4 2
  concept_materialized_view -->|references| concept_cqrs
  linkStyle 1108 stroke-dasharray: 4 2
  concept_materialized_view -->|references| concept_search_index
  linkStyle 1109 stroke-dasharray: 4 2
  concept_mediator -->|references| concept_command
  linkStyle 1110 stroke-dasharray: 4 2
  concept_mediator -->|references| concept_observer
  linkStyle 1111 stroke-dasharray: 4 2
  concept_mediator -->|references| concept_workflow_engine
  linkStyle 1112 stroke-dasharray: 4 2
  concept_memento -->|references| concept_command
  linkStyle 1113 stroke-dasharray: 4 2
  concept_memento -->|references| concept_event_sourcing
  linkStyle 1114 stroke-dasharray: 4 2
  concept_memento -->|references| concept_snapshot_testing
  linkStyle 1115 stroke-dasharray: 4 2
  concept_memory_leak -->|references| concept_bulkhead
  linkStyle 1116 stroke-dasharray: 4 2
  concept_memory_leak -->|references| concept_cache_aside
  linkStyle 1117 stroke-dasharray: 4 2
  concept_memory_leak -->|references| concept_event_driven
  linkStyle 1118 stroke-dasharray: 4 2
  concept_message_queue -->|references| concept_claim_check
  linkStyle 1119 stroke-dasharray: 4 2
  concept_message_queue -->|references| concept_competing_consumers
  linkStyle 1120 stroke-dasharray: 4 2
  concept_message_queue -->|references| concept_dead_letter
  linkStyle 1121 stroke-dasharray: 4 2
  concept_metric_cardinality_explosion -->|references| concept_distributed_tracing
  linkStyle 1122 stroke-dasharray: 4 2
  concept_metric_cardinality_explosion -->|references| concept_metrics_instrumentation
  linkStyle 1123 stroke-dasharray: 4 2
  concept_metric_cardinality_explosion -->|references| concept_structured_logging
  linkStyle 1124 stroke-dasharray: 4 2
  concept_metrics_instrumentation -->|references| concept_distributed_tracing
  linkStyle 1125 stroke-dasharray: 4 2
  concept_metrics_instrumentation -->|references| concept_health_check
  linkStyle 1126 stroke-dasharray: 4 2
  concept_metrics_instrumentation -->|references| concept_structured_logging
  linkStyle 1127 stroke-dasharray: 4 2
  concept_micro_frontend -->|references| concept_bff
  linkStyle 1128 stroke-dasharray: 4 2
  concept_micro_frontend -->|references| concept_component
  linkStyle 1129 stroke-dasharray: 4 2
  concept_micro_frontend -->|references| concept_modular_monolith
  linkStyle 1130 stroke-dasharray: 4 2
  concept_microservices -->|references| concept_api_gateway
  linkStyle 1131 stroke-dasharray: 4 2
  concept_microservices -->|references| concept_distributed_monolith
  linkStyle 1132 stroke-dasharray: 4 2
  concept_microservices -->|references| concept_event_driven
  linkStyle 1133 stroke-dasharray: 4 2
  concept_misleading_names -->|references| concept_hidden_side_effects
  linkStyle 1134 stroke-dasharray: 4 2
  concept_misleading_names -->|references| concept_inconsistent_naming
  linkStyle 1135 stroke-dasharray: 4 2
  concept_misleading_names -->|references| concept_leaky_abstraction
  linkStyle 1136 stroke-dasharray: 4 2
  concept_missing_log_context -->|references| concept_structured_logging
  linkStyle 1137 stroke-dasharray: 4 2
  concept_model_registry -->|references| concept_experiment_framework
  linkStyle 1138 stroke-dasharray: 4 2
  concept_model_registry -->|references| concept_feature_store
  linkStyle 1139 stroke-dasharray: 4 2
  concept_model_registry -->|references| concept_training_pipeline
  linkStyle 1140 stroke-dasharray: 4 2
  concept_modular_monolith -->|references| concept_hexagonal
  linkStyle 1141 stroke-dasharray: 4 2
  concept_modular_monolith -->|references| concept_layered
  linkStyle 1142 stroke-dasharray: 4 2
  concept_modular_monolith -->|references| concept_microservices
  linkStyle 1143 stroke-dasharray: 4 2
  concept_monad -->|references| concept_future_promise
  linkStyle 1144 stroke-dasharray: 4 2
  concept_monad -->|references| concept_pipeline_filter
  linkStyle 1145 stroke-dasharray: 4 2
  concept_monad -->|references| concept_result_type
  linkStyle 1146 stroke-dasharray: 4 2
  concept_mtls -->|references| concept_secret_management
  linkStyle 1147 stroke-dasharray: 4 2
  concept_mtls -->|references| concept_service_mesh
  linkStyle 1148 stroke-dasharray: 4 2
  concept_mtls -->|references| concept_sidecar_mesh
  linkStyle 1149 stroke-dasharray: 4 2
  concept_multi_tenant -->|references| concept_rate_limiting
  linkStyle 1150 stroke-dasharray: 4 2
  concept_multi_tenant -->|references| concept_rbac
  linkStyle 1151 stroke-dasharray: 4 2
  concept_multi_tenant -->|references| concept_sharding
  linkStyle 1152 stroke-dasharray: 4 2
  concept_n_plus_one -->|references| concept_batch_loader
  linkStyle 1153 stroke-dasharray: 4 2
  concept_null_object -->|references| concept_result_type
  linkStyle 1154 stroke-dasharray: 4 2
  concept_null_object -->|references| concept_singleton
  linkStyle 1155 stroke-dasharray: 4 2
  concept_null_object -->|references| concept_strategy
  linkStyle 1156 stroke-dasharray: 4 2
  concept_object_pool -->|references| concept_connection_pooling
  linkStyle 1157 stroke-dasharray: 4 2
  concept_object_pool -->|references| concept_flyweight
  linkStyle 1158 stroke-dasharray: 4 2
  concept_object_pool -->|references| concept_worker_pool
  linkStyle 1159 stroke-dasharray: 4 2
  concept_observer -->|references| concept_event_driven
  linkStyle 1160 stroke-dasharray: 4 2
  concept_observer -->|references| concept_pub_sub
  linkStyle 1161 stroke-dasharray: 4 2
  concept_optimistic_locking -->|references| concept_aggregate
  linkStyle 1162 stroke-dasharray: 4 2
  concept_optimistic_locking -->|references| concept_retry
  linkStyle 1163 stroke-dasharray: 4 2
  concept_optimistic_locking -->|references| concept_value_object
  linkStyle 1164 stroke-dasharray: 4 2
  concept_optimistic_update -->|references| concept_event_notification
  linkStyle 1165 stroke-dasharray: 4 2
  concept_optimistic_update -->|references| concept_optimistic_locking
  linkStyle 1166 stroke-dasharray: 4 2
  concept_optimistic_update -->|references| concept_reactive_store
  linkStyle 1167 stroke-dasharray: 4 2
  concept_orchestration -->|references| concept_choreography
  linkStyle 1168 stroke-dasharray: 4 2
  concept_orchestration -->|references| concept_saga_orchestrator
  linkStyle 1169 stroke-dasharray: 4 2
  concept_orchestration -->|references| concept_workflow_engine
  linkStyle 1170 stroke-dasharray: 4 2
  concept_outbox -->|references| concept_change_data_capture
  linkStyle 1171 stroke-dasharray: 4 2
  concept_outbox -->|references| concept_competing_consumers
  linkStyle 1172 stroke-dasharray: 4 2
  concept_outbox -->|references| concept_event_driven
  linkStyle 1173 stroke-dasharray: 4 2
  concept_over_under_fetching -->|references| concept_bff
  linkStyle 1174 stroke-dasharray: 4 2
  concept_over_under_fetching -->|references| concept_graphql
  linkStyle 1175 stroke-dasharray: 4 2
  concept_over_under_fetching -->|references| concept_rest
  linkStyle 1176 stroke-dasharray: 4 2
  concept_pipeline_filter -->|references| concept_batch_processing
  linkStyle 1177 stroke-dasharray: 4 2
  concept_pipeline_filter -->|references| concept_data_pipeline
  linkStyle 1178 stroke-dasharray: 4 2
  concept_pipeline_filter -->|references| concept_middleware
  linkStyle 1179 stroke-dasharray: 4 2
  concept_pipeline_stages -->|references| concept_data_pipeline
  linkStyle 1180 stroke-dasharray: 4 2
  concept_pipeline_stages -->|references| concept_mapreduce
  linkStyle 1181 stroke-dasharray: 4 2
  concept_pipeline_stages -->|references| concept_pipeline_filter
  linkStyle 1182 stroke-dasharray: 4 2
  concept_plugin_host -->|references| concept_plugin
  linkStyle 1183 stroke-dasharray: 4 2
  concept_pokemon_exception -->|references| concept_log_and_throw
  linkStyle 1184 stroke-dasharray: 4 2
  concept_pokemon_exception -->|references| concept_magic_numbers
  linkStyle 1185 stroke-dasharray: 4 2
  concept_pokemon_exception -->|references| concept_swallowed_exception
  linkStyle 1186 stroke-dasharray: 4 2
  concept_polling_flow -->|references| concept_long_polling
  linkStyle 1187 stroke-dasharray: 4 2
  concept_polling_flow -->|references| concept_scheduler
  linkStyle 1188 stroke-dasharray: 4 2
  concept_polling_flow -->|references| concept_webhook
  linkStyle 1189 stroke-dasharray: 4 2
  concept_premature_optimization -->|references| concept_golden_hammer
  linkStyle 1190 stroke-dasharray: 4 2
  concept_premature_optimization -->|references| concept_lru_cache
  linkStyle 1191 stroke-dasharray: 4 2
  concept_premature_optimization -->|references| concept_microservices
  linkStyle 1192 stroke-dasharray: 4 2
  concept_primitive_obsession -->|references| concept_boolean_blindness
  linkStyle 1193 stroke-dasharray: 4 2
  concept_primitive_obsession -->|references| concept_stringly_typed
  linkStyle 1194 stroke-dasharray: 4 2
  concept_primitive_obsession -->|references| concept_value_object
  linkStyle 1195 stroke-dasharray: 4 2
  concept_producer_consumer -->|references| concept_backpressure
  linkStyle 1196 stroke-dasharray: 4 2
  concept_producer_consumer -->|references| concept_competing_consumers
  linkStyle 1197 stroke-dasharray: 4 2
  concept_producer_consumer -->|references| concept_message_queue
  linkStyle 1198 stroke-dasharray: 4 2
  concept_prop_drilling -->|references| concept_component
  linkStyle 1199 stroke-dasharray: 4 2
  concept_prop_drilling -->|references| concept_flux
  linkStyle 1200 stroke-dasharray: 4 2
  concept_prop_drilling -->|references| concept_reactive_store
  linkStyle 1201 stroke-dasharray: 4 2
  concept_property_graph -->|references| concept_graph
  linkStyle 1202 stroke-dasharray: 4 2
  concept_property_graph -->|references| concept_search_index
  linkStyle 1203 stroke-dasharray: 4 2
  concept_property_testing -->|references| concept_fixture_builder
  linkStyle 1204 stroke-dasharray: 4 2
  concept_property_testing -->|references| concept_result_type
  linkStyle 1205 stroke-dasharray: 4 2
  concept_property_testing -->|references| concept_snapshot_testing
  linkStyle 1206 stroke-dasharray: 4 2
  concept_prototype -->|references| concept_builder
  linkStyle 1207 stroke-dasharray: 4 2
  concept_prototype -->|references| concept_factory
  linkStyle 1208 stroke-dasharray: 4 2
  concept_prototype -->|references| concept_fixture_builder
  linkStyle 1209 stroke-dasharray: 4 2
  concept_proxy -->|references| concept_decorator
  linkStyle 1210 stroke-dasharray: 4 2
  concept_pub_sub -->|references| concept_event_driven
  linkStyle 1211 stroke-dasharray: 4 2
  concept_pub_sub -->|references| concept_observer
  linkStyle 1212 stroke-dasharray: 4 2
  concept_pub_sub -->|references| concept_webhook
  linkStyle 1213 stroke-dasharray: 4 2
  concept_query_object -->|references| concept_cqrs
  linkStyle 1214 stroke-dasharray: 4 2
  concept_query_object -->|references| concept_repository
  linkStyle 1215 stroke-dasharray: 4 2
  concept_query_object -->|references| concept_specification
  linkStyle 1216 stroke-dasharray: 4 2
  concept_race_condition -->|references| concept_deadlock
  linkStyle 1217 stroke-dasharray: 4 2
  concept_race_condition -->|references| concept_optimistic_locking
  linkStyle 1218 stroke-dasharray: 4 2
  concept_race_condition -->|references| concept_read_write_lock
  linkStyle 1219 stroke-dasharray: 4 2
  concept_rate_limiting -->|references| concept_api_gateway
  linkStyle 1220 stroke-dasharray: 4 2
  concept_rate_limiting -->|references| concept_backpressure
  linkStyle 1221 stroke-dasharray: 4 2
  concept_rate_limiting -->|references| concept_circuit_breaker
  linkStyle 1222 stroke-dasharray: 4 2
  concept_rbac -->|references| concept_multi_tenant
  linkStyle 1223 stroke-dasharray: 4 2
  concept_rbac -->|references| concept_oauth_oidc
  linkStyle 1224 stroke-dasharray: 4 2
  concept_rbac -->|references| concept_route_guard
  linkStyle 1225 stroke-dasharray: 4 2
  concept_reactive_store -->|references| concept_component
  linkStyle 1226 stroke-dasharray: 4 2
  concept_reactive_store -->|references| concept_flux
  linkStyle 1227 stroke-dasharray: 4 2
  concept_reactive_store -->|references| concept_suspense_boundary
  linkStyle 1228 stroke-dasharray: 4 2
  concept_reactor -->|references| concept_event_driven
  linkStyle 1229 stroke-dasharray: 4 2
  concept_reactor -->|references| concept_future_promise
  linkStyle 1230 stroke-dasharray: 4 2
  concept_reactor -->|references| concept_server_sent_events
  linkStyle 1231 stroke-dasharray: 4 2
  concept_read_through -->|references| concept_cache_aside
  linkStyle 1232 stroke-dasharray: 4 2
  concept_read_through -->|references| concept_read_write_lock
  linkStyle 1233 stroke-dasharray: 4 2
  concept_read_through -->|references| concept_refresh_ahead
  linkStyle 1234 stroke-dasharray: 4 2
  concept_read_write_lock -->|references| concept_deadlock
  linkStyle 1235 stroke-dasharray: 4 2
  concept_read_write_lock -->|references| concept_optimistic_locking
  linkStyle 1236 stroke-dasharray: 4 2
  concept_read_write_lock -->|references| concept_race_condition
  linkStyle 1237 stroke-dasharray: 4 2
  concept_refresh_ahead -->|references| concept_cache_aside
  linkStyle 1238 stroke-dasharray: 4 2
  concept_refresh_ahead -->|references| concept_read_through
  linkStyle 1239 stroke-dasharray: 4 2
  concept_refresh_ahead -->|references| concept_scheduler
  linkStyle 1240 stroke-dasharray: 4 2
  concept_registry_model -->|references| concept_catalog
  linkStyle 1241 stroke-dasharray: 4 2
  concept_registry_model -->|references| concept_soft_delete
  linkStyle 1242 stroke-dasharray: 4 2
  concept_registry_model -->|references| concept_workflow_state_machine
  linkStyle 1243 stroke-dasharray: 4 2
  concept_reinventing_the_wheel -->|references| concept_cargo_cult
  linkStyle 1244 stroke-dasharray: 4 2
  concept_reinventing_the_wheel -->|references| concept_copy_paste_programming
  linkStyle 1245 stroke-dasharray: 4 2
  concept_reinventing_the_wheel -->|references| concept_golden_hammer
  linkStyle 1246 stroke-dasharray: 4 2
  concept_repository -->|references| concept_aggregate
  linkStyle 1247 stroke-dasharray: 4 2
  concept_repository -->|references| concept_data_mapper
  linkStyle 1248 stroke-dasharray: 4 2
  concept_repository -->|references| concept_unit_of_work
  linkStyle 1249 stroke-dasharray: 4 2
  concept_request_path -->|references| concept_router
  linkStyle 1250 stroke-dasharray: 4 2
  concept_request_path -->|references| concept_server_route_registration
  linkStyle 1251 stroke-dasharray: 4 2
  concept_request_reply -->|references| concept_correlation_id
  linkStyle 1252 stroke-dasharray: 4 2
  concept_request_reply -->|references| concept_message_queue
  linkStyle 1253 stroke-dasharray: 4 2
  concept_request_reply -->|references| concept_request_path
  linkStyle 1254 stroke-dasharray: 4 2
  concept_rest -->|references| concept_graphql
  linkStyle 1255 stroke-dasharray: 4 2
  concept_rest -->|references| concept_pagination
  linkStyle 1256 stroke-dasharray: 4 2
  concept_rest -->|references| concept_server_route_registration
  linkStyle 1257 stroke-dasharray: 4 2
  concept_result_type -->|references| concept_error_code_returns
  linkStyle 1258 stroke-dasharray: 4 2
  concept_result_type -->|references| concept_null_object
  linkStyle 1259 stroke-dasharray: 4 2
  concept_result_type -->|references| concept_property_testing
  linkStyle 1260 stroke-dasharray: 4 2
  concept_retry -->|references| concept_circuit_breaker
  linkStyle 1261 stroke-dasharray: 4 2
  concept_retry -->|references| concept_dead_letter
  linkStyle 1262 stroke-dasharray: 4 2
  concept_retry -->|references| concept_timeout
  linkStyle 1263 stroke-dasharray: 4 2
  concept_ring_buffer -->|references| concept_backpressure
  linkStyle 1264 stroke-dasharray: 4 2
  concept_ring_buffer -->|references| concept_stream_to_store
  linkStyle 1265 stroke-dasharray: 4 2
  concept_ring_buffer -->|references| concept_worker_pool
  linkStyle 1266 stroke-dasharray: 4 2
  concept_route_guard -->|references| concept_router
  linkStyle 1267 stroke-dasharray: 4 2
  concept_router -->|references| concept_route_guard
  linkStyle 1268 stroke-dasharray: 4 2
  concept_router -->|references| concept_server_route_registration
  linkStyle 1269 stroke-dasharray: 4 2
  concept_rule_engine -->|references| concept_feature_flag
  linkStyle 1270 stroke-dasharray: 4 2
  concept_rule_engine -->|references| concept_specification
  linkStyle 1271 stroke-dasharray: 4 2
  concept_rule_engine -->|references| concept_strategy
  linkStyle 1272 stroke-dasharray: 4 2
  concept_saga_orchestrator -->|references| concept_choreography
  linkStyle 1273 stroke-dasharray: 4 2
  concept_saga_orchestrator -->|references| concept_saga
  linkStyle 1274 stroke-dasharray: 4 2
  concept_saga_orchestrator -->|references| concept_workflow_engine
  linkStyle 1275 stroke-dasharray: 4 2
  concept_scatter_gather -->|references| concept_bff
  linkStyle 1276 stroke-dasharray: 4 2
  concept_scatter_gather -->|references| concept_fan_out
  linkStyle 1277 stroke-dasharray: 4 2
  concept_scatter_gather -->|references| concept_request_reply
  linkStyle 1278 stroke-dasharray: 4 2
  concept_scheduler -->|references| concept_batch_processing
  linkStyle 1279 stroke-dasharray: 4 2
  concept_scheduler -->|references| concept_leader_election
  linkStyle 1280 stroke-dasharray: 4 2
  concept_scheduler -->|references| concept_workflow_engine
  linkStyle 1281 stroke-dasharray: 4 2
  concept_schema_on_read -->|references| concept_input_validation
  linkStyle 1282 stroke-dasharray: 4 2
  concept_schema_on_read -->|references| concept_insecure_deserialization
  linkStyle 1283 stroke-dasharray: 4 2
  concept_schema_on_read -->|references| concept_stringly_typed
  linkStyle 1284 stroke-dasharray: 4 2
  concept_schema_registry -->|references| concept_database_migration
  linkStyle 1285 stroke-dasharray: 4 2
  concept_schema_registry -->|references| concept_event_driven
  linkStyle 1286 stroke-dasharray: 4 2
  concept_schema_registry -->|references| concept_schema_on_read
  linkStyle 1287 stroke-dasharray: 4 2
  concept_search_index -->|references| concept_change_data_capture
  linkStyle 1288 stroke-dasharray: 4 2
  concept_search_index -->|references| concept_cqrs
  linkStyle 1289 stroke-dasharray: 4 2
  concept_search_index -->|references| concept_pagination
  linkStyle 1290 stroke-dasharray: 4 2
  concept_secret_management -->|references| concept_config_management
  linkStyle 1291 stroke-dasharray: 4 2
  concept_secret_management -->|references| concept_immutable_infra
  linkStyle 1292 stroke-dasharray: 4 2
  concept_secret_management -->|references| concept_mtls
  linkStyle 1293 stroke-dasharray: 4 2
  concept_select_star -->|references| concept_materialized_view
  linkStyle 1294 stroke-dasharray: 4 2
  concept_select_star -->|references| concept_over_under_fetching
  linkStyle 1295 stroke-dasharray: 4 2
  concept_select_star -->|references| concept_repository
  linkStyle 1296 stroke-dasharray: 4 2
  concept_server_prefetch -->|references| concept_hydration
  linkStyle 1297 stroke-dasharray: 4 2
  concept_server_prefetch -->|references| concept_lazy_loading
  linkStyle 1298 stroke-dasharray: 4 2
  concept_server_prefetch -->|references| concept_suspense_boundary
  linkStyle 1299 stroke-dasharray: 4 2
  concept_server_route_registration -->|references| concept_graphql
  linkStyle 1300 stroke-dasharray: 4 2
  concept_server_route_registration -->|references| concept_grpc
  linkStyle 1301 stroke-dasharray: 4 2
  concept_server_route_registration -->|references| concept_middleware
  linkStyle 1302 stroke-dasharray: 4 2
  concept_server_route_registration -->|references| concept_rest
  linkStyle 1303 stroke-dasharray: 4 2
  concept_server_route_registration -->|references| concept_router
  linkStyle 1304 stroke-dasharray: 4 2
  concept_server_sent_events -->|references| concept_event_driven
  linkStyle 1305 stroke-dasharray: 4 2
  concept_server_sent_events -->|references| concept_long_polling
  linkStyle 1306 stroke-dasharray: 4 2
  concept_server_sent_events -->|references| concept_websocket
  linkStyle 1307 stroke-dasharray: 4 2
  concept_serverless -->|references| concept_event_driven
  linkStyle 1308 stroke-dasharray: 4 2
  concept_serverless -->|references| concept_scheduler
  linkStyle 1309 stroke-dasharray: 4 2
  concept_serverless -->|references| concept_service_manager
  linkStyle 1310 stroke-dasharray: 4 2
  concept_service_discovery -->|references| concept_api_gateway
  linkStyle 1311 stroke-dasharray: 4 2
  concept_service_discovery -->|references| concept_load_balancer
  linkStyle 1312 stroke-dasharray: 4 2
  concept_service_discovery -->|references| concept_service_mesh
  linkStyle 1313 stroke-dasharray: 4 2
  concept_service_manager -->|references| concept_graceful_degradation
  linkStyle 1314 stroke-dasharray: 4 2
  concept_service_manager -->|references| concept_health_check
  linkStyle 1315 stroke-dasharray: 4 2
  concept_service_manager -->|references| concept_scheduler
  linkStyle 1316 stroke-dasharray: 4 2
  concept_service_mesh -->|references| concept_mtls
  linkStyle 1317 stroke-dasharray: 4 2
  concept_service_mesh -->|references| concept_retry
  linkStyle 1318 stroke-dasharray: 4 2
  concept_service_mesh -->|references| concept_service_discovery
  linkStyle 1319 stroke-dasharray: 4 2
  concept_sharding -->|references| concept_key_value_model
  linkStyle 1320 stroke-dasharray: 4 2
  concept_sharding -->|references| concept_service_discovery
  linkStyle 1321 stroke-dasharray: 4 2
  concept_sharding -->|references| concept_tenant_routing
  linkStyle 1322 stroke-dasharray: 4 2
  concept_shared_database -->|references| concept_database_per_service
  linkStyle 1323 stroke-dasharray: 4 2
  concept_shared_database -->|references| concept_distributed_monolith
  linkStyle 1324 stroke-dasharray: 4 2
  concept_shared_database -->|references| concept_microservices
  linkStyle 1325 stroke-dasharray: 4 2
  concept_shotgun_surgery -->|references| concept_copy_paste_programming
  linkStyle 1326 stroke-dasharray: 4 2
  concept_shotgun_surgery -->|references| concept_god_object
  linkStyle 1327 stroke-dasharray: 4 2
  concept_shotgun_surgery -->|references| concept_tight_coupling
  linkStyle 1328 stroke-dasharray: 4 2
  concept_side_effect_hook -->|references| concept_component
  linkStyle 1329 stroke-dasharray: 4 2
  concept_side_effect_hook -->|references| concept_hidden_side_effects
  linkStyle 1330 stroke-dasharray: 4 2
  concept_side_effect_hook -->|references| concept_reactive_store
  linkStyle 1331 stroke-dasharray: 4 2
  concept_sidecar -->|references| concept_service_manager
  linkStyle 1332 stroke-dasharray: 4 2
  concept_sidecar -->|references| concept_service_mesh
  linkStyle 1333 stroke-dasharray: 4 2
  concept_sidecar -->|references| concept_sidecar_mesh
  linkStyle 1334 stroke-dasharray: 4 2
  concept_sidecar_mesh -->|references| concept_mtls
  linkStyle 1335 stroke-dasharray: 4 2
  concept_sidecar_mesh -->|references| concept_service_mesh
  linkStyle 1336 stroke-dasharray: 4 2
  concept_sidecar_mesh -->|references| concept_sidecar
  linkStyle 1337 stroke-dasharray: 4 2
  concept_singleton -->|references| concept_dependency_injection
  linkStyle 1338 stroke-dasharray: 4 2
  concept_singleton -->|references| concept_service_manager
  linkStyle 1339 stroke-dasharray: 4 2
  concept_singleton -->|references| concept_tight_coupling
  linkStyle 1340 stroke-dasharray: 4 2
  concept_snapshot_testing -->|references| concept_fixture_builder
  linkStyle 1341 stroke-dasharray: 4 2
  concept_snapshot_testing -->|references| concept_flaky_tests
  linkStyle 1342 stroke-dasharray: 4 2
  concept_snapshot_testing -->|references| concept_memento
  linkStyle 1343 stroke-dasharray: 4 2
  concept_snowflake_server -->|references| concept_infrastructure_as_code
  linkStyle 1344 stroke-dasharray: 4 2
  concept_social_graph -->|references| concept_cache_aside
  linkStyle 1345 stroke-dasharray: 4 2
  concept_social_graph -->|references| concept_graph
  linkStyle 1346 stroke-dasharray: 4 2
  concept_social_graph -->|references| concept_pub_sub
  linkStyle 1347 stroke-dasharray: 4 2
  concept_soft_delete -->|references| concept_audit_logging
  linkStyle 1348 stroke-dasharray: 4 2
  concept_soft_delete -->|references| concept_registry_model
  linkStyle 1349 stroke-dasharray: 4 2
  concept_soft_delete -->|references| concept_workflow_state_machine
  linkStyle 1350 stroke-dasharray: 4 2
  concept_spaghetti_code -->|references| concept_deep_nesting
  linkStyle 1351 stroke-dasharray: 4 2
  concept_spaghetti_code -->|references| concept_god_object
  linkStyle 1352 stroke-dasharray: 4 2
  concept_spaghetti_code -->|references| concept_train_wreck
  linkStyle 1353 stroke-dasharray: 4 2
  concept_spatial -->|references| concept_cache_aside
  linkStyle 1354 stroke-dasharray: 4 2
  concept_spatial -->|references| concept_pagination
  linkStyle 1355 stroke-dasharray: 4 2
  concept_spatial -->|references| concept_search_index
  linkStyle 1356 stroke-dasharray: 4 2
  concept_spatial_partitioning -->|references| concept_entity_component_system
  linkStyle 1357 stroke-dasharray: 4 2
  concept_spatial_partitioning -->|references| concept_game_loop
  linkStyle 1358 stroke-dasharray: 4 2
  concept_spatial_partitioning -->|references| concept_tick_simulation
  linkStyle 1359 stroke-dasharray: 4 2
  concept_specification -->|references| concept_ddd
  linkStyle 1360 stroke-dasharray: 4 2
  concept_specification -->|references| concept_query_object
  linkStyle 1361 stroke-dasharray: 4 2
  concept_specification -->|references| concept_strategy
  linkStyle 1362 stroke-dasharray: 4 2
  concept_sql_injection -->|references| concept_input_validation
  linkStyle 1363 stroke-dasharray: 4 2
  concept_sql_injection -->|references| concept_insecure_deserialization
  linkStyle 1364 stroke-dasharray: 4 2
  concept_sql_injection -->|references| concept_repository
  linkStyle 1365 stroke-dasharray: 4 2
  concept_state_machine -->|references| concept_workflow_engine
  linkStyle 1366 stroke-dasharray: 4 2
  concept_strangler_fig -->|references| concept_anti_corruption_layer
  linkStyle 1367 stroke-dasharray: 4 2
  concept_strangler_fig -->|references| concept_canary
  linkStyle 1368 stroke-dasharray: 4 2
  concept_strangler_fig -->|references| concept_modular_monolith
  linkStyle 1369 stroke-dasharray: 4 2
  concept_strategy -->|references| concept_bridge
  linkStyle 1370 stroke-dasharray: 4 2
  concept_strategy -->|references| concept_factory
  linkStyle 1371 stroke-dasharray: 4 2
  concept_strategy -->|references| concept_specification
  linkStyle 1372 stroke-dasharray: 4 2
  concept_stream_processing -->|references| concept_batch_processing
  linkStyle 1373 stroke-dasharray: 4 2
  concept_stream_processing -->|references| concept_stream_to_store
  linkStyle 1374 stroke-dasharray: 4 2
  concept_stream_processing -->|references| concept_streaming_flow
  linkStyle 1375 stroke-dasharray: 4 2
  concept_stream_to_store -->|references| concept_data_pipeline
  linkStyle 1376 stroke-dasharray: 4 2
  concept_stream_to_store -->|references| concept_materialized_view
  linkStyle 1377 stroke-dasharray: 4 2
  concept_stream_to_store -->|references| concept_message_queue
  linkStyle 1378 stroke-dasharray: 4 2
  concept_streaming_flow -->|references| concept_pub_sub
  linkStyle 1379 stroke-dasharray: 4 2
  concept_streaming_flow -->|references| concept_server_sent_events
  linkStyle 1380 stroke-dasharray: 4 2
  concept_streaming_flow -->|references| concept_stream_to_store
  linkStyle 1381 stroke-dasharray: 4 2
  concept_stringly_typed -->|references| concept_input_validation
  linkStyle 1382 stroke-dasharray: 4 2
  concept_stringly_typed -->|references| concept_magic_numbers
  linkStyle 1383 stroke-dasharray: 4 2
  concept_stringly_typed -->|references| concept_primitive_obsession
  linkStyle 1384 stroke-dasharray: 4 2
  concept_structured_logging -->|references| concept_correlation_id
  linkStyle 1385 stroke-dasharray: 4 2
  concept_structured_logging -->|references| concept_distributed_tracing
  linkStyle 1386 stroke-dasharray: 4 2
  concept_structured_logging -->|references| concept_metrics_instrumentation
  linkStyle 1387 stroke-dasharray: 4 2
  concept_subscription -->|references| concept_multi_tenant
  linkStyle 1388 stroke-dasharray: 4 2
  concept_subscription -->|references| concept_state_machine
  linkStyle 1389 stroke-dasharray: 4 2
  concept_subscription -->|references| concept_webhook
  linkStyle 1390 stroke-dasharray: 4 2
  concept_suspense_boundary -->|references| concept_error_boundary
  linkStyle 1391 stroke-dasharray: 4 2
  concept_suspense_boundary -->|references| concept_hydration
  linkStyle 1392 stroke-dasharray: 4 2
  concept_suspense_boundary -->|references| concept_lazy_loading
  linkStyle 1393 stroke-dasharray: 4 2
  concept_swallowed_exception -->|references| concept_hidden_side_effects
  linkStyle 1394 stroke-dasharray: 4 2
  concept_swallowed_exception -->|references| concept_log_and_throw
  linkStyle 1395 stroke-dasharray: 4 2
  concept_swallowed_exception -->|references| concept_result_type
  linkStyle 1396 stroke-dasharray: 4 2
  concept_sync_in_async -->|references| concept_busy_waiting
  linkStyle 1397 stroke-dasharray: 4 2
  concept_sync_in_async -->|references| concept_future_promise
  linkStyle 1398 stroke-dasharray: 4 2
  concept_sync_in_async -->|references| concept_reactor
  linkStyle 1399 stroke-dasharray: 4 2
  concept_template_method -->|references| concept_factory
  linkStyle 1400 stroke-dasharray: 4 2
  concept_template_method -->|references| concept_strategy
  linkStyle 1401 stroke-dasharray: 4 2
  concept_template_method -->|references| concept_visitor
  linkStyle 1402 stroke-dasharray: 4 2
  concept_temporal_coupling -->|references| concept_builder
  linkStyle 1403 stroke-dasharray: 4 2
  concept_temporal_coupling -->|references| concept_service_manager
  linkStyle 1404 stroke-dasharray: 4 2
  concept_temporal_coupling -->|references| concept_workflow_state_machine
  linkStyle 1405 stroke-dasharray: 4 2
  concept_tenant_isolation -->|references| concept_multi_tenant
  linkStyle 1406 stroke-dasharray: 4 2
  concept_tenant_isolation -->|references| concept_rbac
  linkStyle 1407 stroke-dasharray: 4 2
  concept_tenant_isolation -->|references| concept_tenant_routing
  linkStyle 1408 stroke-dasharray: 4 2
  concept_tenant_routing -->|references| concept_multi_tenant
  linkStyle 1409 stroke-dasharray: 4 2
  concept_tenant_routing -->|references| concept_sharding
  linkStyle 1410 stroke-dasharray: 4 2
  concept_tenant_routing -->|references| concept_tenant_isolation
  linkStyle 1411 stroke-dasharray: 4 2
  concept_tensor -->|references| concept_feature_store
  linkStyle 1412 stroke-dasharray: 4 2
  concept_tensor -->|references| concept_model_registry
  linkStyle 1413 stroke-dasharray: 4 2
  concept_tensor -->|references| concept_training_pipeline
  linkStyle 1414 stroke-dasharray: 4 2
  concept_test_doubles -->|references| concept_fixture_builder
  linkStyle 1415 stroke-dasharray: 4 2
  concept_test_doubles -->|references| concept_property_testing
  linkStyle 1416 stroke-dasharray: 4 2
  concept_test_doubles -->|references| concept_snapshot_testing
  linkStyle 1417 stroke-dasharray: 4 2
  concept_test_pollution -->|references| concept_flaky_tests
  linkStyle 1418 stroke-dasharray: 4 2
  concept_test_pollution -->|references| concept_singleton
  linkStyle 1419 stroke-dasharray: 4 2
  concept_test_pollution -->|references| concept_test_doubles
  linkStyle 1420 stroke-dasharray: 4 2
  concept_tick_simulation -->|references| concept_entity_component_system
  linkStyle 1421 stroke-dasharray: 4 2
  concept_tick_simulation -->|references| concept_game_loop
  linkStyle 1422 stroke-dasharray: 4 2
  concept_tick_simulation -->|references| concept_spatial_partitioning
  linkStyle 1423 stroke-dasharray: 4 2
  concept_tight_coupling -->|references| concept_dependency_injection
  linkStyle 1424 stroke-dasharray: 4 2
  concept_tight_coupling -->|references| concept_hexagonal
  linkStyle 1425 stroke-dasharray: 4 2
  concept_tight_coupling -->|references| concept_leaky_abstraction
  linkStyle 1426 stroke-dasharray: 4 2
  concept_time_series -->|references| concept_materialized_view
  linkStyle 1427 stroke-dasharray: 4 2
  concept_time_series -->|references| concept_metrics_instrumentation
  linkStyle 1428 stroke-dasharray: 4 2
  concept_time_series -->|references| concept_stream_to_store
  linkStyle 1429 stroke-dasharray: 4 2
  concept_timeout -->|references| concept_circuit_breaker
  linkStyle 1430 stroke-dasharray: 4 2
  concept_timeout -->|references| concept_retry
  linkStyle 1431 stroke-dasharray: 4 2
  concept_train_wreck -->|references| concept_deep_nesting
  linkStyle 1432 stroke-dasharray: 4 2
  concept_train_wreck -->|references| concept_leaky_abstraction
  linkStyle 1433 stroke-dasharray: 4 2
  concept_train_wreck -->|references| concept_tight_coupling
  linkStyle 1434 stroke-dasharray: 4 2
  concept_training_pipeline -->|references| concept_experiment_framework
  linkStyle 1435 stroke-dasharray: 4 2
  concept_training_pipeline -->|references| concept_feature_store
  linkStyle 1436 stroke-dasharray: 4 2
  concept_training_pipeline -->|references| concept_model_registry
  linkStyle 1437 stroke-dasharray: 4 2
  concept_trie -->|references| concept_key_value_model
  linkStyle 1438 stroke-dasharray: 4 2
  concept_trie -->|references| concept_lexer_parser
  linkStyle 1439 stroke-dasharray: 4 2
  concept_trie -->|references| concept_search_index
  linkStyle 1440 stroke-dasharray: 4 2
  concept_unbounded_growth -->|references| concept_lru_cache
  linkStyle 1441 stroke-dasharray: 4 2
  concept_unbounded_growth -->|references| concept_memory_leak
  linkStyle 1442 stroke-dasharray: 4 2
  concept_unbounded_growth -->|references| concept_metric_cardinality_explosion
  linkStyle 1443 stroke-dasharray: 4 2
  concept_unit_of_work -->|references| concept_aggregate
  linkStyle 1444 stroke-dasharray: 4 2
  concept_unit_of_work -->|references| concept_data_mapper
  linkStyle 1445 stroke-dasharray: 4 2
  concept_unit_of_work -->|references| concept_repository
  linkStyle 1446 stroke-dasharray: 4 2
  concept_value_object -->|references| concept_aggregate
  linkStyle 1447 stroke-dasharray: 4 2
  concept_value_object -->|references| concept_ddd
  linkStyle 1448 stroke-dasharray: 4 2
  concept_versioned_document -->|references| concept_block_content
  linkStyle 1449 stroke-dasharray: 4 2
  concept_versioned_document -->|references| concept_event_sourcing
  linkStyle 1450 stroke-dasharray: 4 2
  concept_versioned_document -->|references| concept_optimistic_locking
  linkStyle 1451 stroke-dasharray: 4 2
  concept_visitor -->|references| concept_ast
  linkStyle 1452 stroke-dasharray: 4 2
  concept_visitor -->|references| concept_command
  linkStyle 1453 stroke-dasharray: 4 2
  concept_visitor -->|references| concept_composite
  linkStyle 1454 stroke-dasharray: 4 2
  concept_webhook -->|references| concept_pub_sub
  linkStyle 1455 stroke-dasharray: 4 2
  concept_webhook -->|references| concept_server_route_registration
  linkStyle 1456 stroke-dasharray: 4 2
  concept_webhook -->|references| concept_subscription
  linkStyle 1457 stroke-dasharray: 4 2
  concept_worker_pool -->|references| concept_backpressure
  linkStyle 1458 stroke-dasharray: 4 2
  concept_worker_pool -->|references| concept_competing_consumers
  linkStyle 1459 stroke-dasharray: 4 2
  concept_worker_pool -->|references| concept_producer_consumer
  linkStyle 1460 stroke-dasharray: 4 2
  concept_workflow_state_machine -->|references| concept_state_machine
  linkStyle 1461 stroke-dasharray: 4 2
  concept_workflow_state_machine -->|references| concept_workflow_engine
  linkStyle 1462 stroke-dasharray: 4 2
  concept_write_behind -->|references| concept_cache_aside
  linkStyle 1463 stroke-dasharray: 4 2
  concept_write_behind -->|references| concept_message_queue
  linkStyle 1464 stroke-dasharray: 4 2
  concept_write_behind -->|references| concept_read_through
  linkStyle 1465 stroke-dasharray: 4 2
  framework_angular -->|related to| concept_mvvm
  framework_django -->|related to| concept_layered
  framework_express -->|related to| concept_middleware
  framework_fastapi -->|related to| concept_hexagonal
  framework_fastapi -->|related to| concept_layered
  framework_flask -->|related to| concept_layered
  framework_laravel -->|related to| concept_layered
  framework_nestjs -->|related to| concept_layered
  framework_rails -->|related to| concept_layered
  framework_react -->|related to| concept_prop_drilling
  framework_react -->|related to| concept_reactive_store
  framework_spring -->|related to| concept_layered
  framework_symfony -->|related to| concept_layered
  framework_vue -->|related to| concept_reactive_store
  framework_angular -->|supports| concept_dependency_injection
  framework_angular -->|supports| concept_form_binding
  framework_angular -->|supports| concept_hydration
  framework_angular -->|supports| concept_route_guard
  framework_chi -->|supports| concept_middleware
  framework_django -->|supports| concept_input_validation
  framework_elysia -->|supports| concept_input_validation
  framework_fastapi -->|supports| concept_dependency_injection
  framework_fastapi -->|supports| concept_input_validation
  framework_fastify -->|supports| concept_input_validation
  framework_koa -->|supports| concept_middleware
  framework_laravel -->|supports| concept_dependency_injection
  framework_laravel -->|supports| concept_input_validation
  framework_nestjs -->|supports| concept_dependency_injection
  framework_nestjs -->|supports| concept_input_validation
  framework_quarkus -->|supports| concept_dependency_injection
  framework_rails -->|supports| concept_input_validation
  framework_react -->|supports| concept_error_boundary
  framework_react -->|supports| concept_form_binding
  framework_react -->|supports| concept_hydration
  framework_react -->|supports| concept_suspense_boundary
  framework_spring -->|supports| concept_dependency_injection
  framework_spring -->|supports| concept_input_validation
  framework_symfony -->|supports| concept_dependency_injection
  framework_symfony -->|supports| concept_input_validation
  framework_vue -->|supports| concept_form_binding
  framework_vue -->|supports| concept_hydration
  framework_actix_web -->|uses| concept_server_route_registration
  framework_aiohttp -->|uses| concept_server_route_registration
  framework_aspnet_controllers -->|uses| concept_server_route_registration
  framework_aspnet_minimal -->|uses| concept_server_route_registration
  framework_axum -->|uses| concept_server_route_registration
  framework_chi -->|uses| concept_server_route_registration
  framework_django -->|uses| concept_server_route_registration
  framework_echo -->|uses| concept_server_route_registration
  framework_elysia -->|uses| concept_server_route_registration
  framework_express -->|uses| concept_server_route_registration
  framework_fastapi -->|uses| concept_server_route_registration
  framework_fastify -->|uses| concept_server_route_registration
  framework_fiber -->|uses| concept_server_route_registration
  framework_flask -->|uses| concept_server_route_registration
  framework_gin -->|uses| concept_server_route_registration
  framework_grape -->|uses| concept_server_route_registration
  framework_hono -->|uses| concept_server_route_registration
  framework_koa -->|uses| concept_server_route_registration
  framework_ktor -->|uses| concept_server_route_registration
  framework_laravel -->|uses| concept_server_route_registration
  framework_nestjs -->|uses| concept_server_route_registration
  framework_net_http -->|uses| concept_server_route_registration
  framework_nextjs -->|uses| concept_server_route_registration
  framework_phoenix -->|uses| concept_server_route_registration
  framework_quarkus -->|uses| concept_server_route_registration
  framework_rails -->|uses| concept_server_route_registration
  framework_sinatra -->|uses| concept_server_route_registration
  framework_slim -->|uses| concept_server_route_registration
  framework_spring -->|uses| concept_server_route_registration
  framework_starlette -->|uses| concept_server_route_registration
  framework_sveltekit -->|uses| concept_server_route_registration
  framework_symfony -->|uses| concept_server_route_registration
  framework_vapor -->|uses| concept_server_route_registration
  framework_actix_web -->|uses language| language_rust
  linkStyle 1540 stroke-dasharray: 4 2
  framework_aiohttp -->|uses language| language_python
  linkStyle 1541 stroke-dasharray: 4 2
  framework_angular -->|uses language| language_typescript
  linkStyle 1542 stroke-dasharray: 4 2
  framework_aspnet_controllers -->|uses language| language_csharp
  linkStyle 1543 stroke-dasharray: 4 2
  framework_aspnet_minimal -->|uses language| language_csharp
  linkStyle 1544 stroke-dasharray: 4 2
  framework_axum -->|uses language| language_rust
  linkStyle 1545 stroke-dasharray: 4 2
  framework_chi -->|uses language| language_go
  linkStyle 1546 stroke-dasharray: 4 2
  framework_django -->|uses language| language_python
  linkStyle 1547 stroke-dasharray: 4 2
  framework_echo -->|uses language| language_go
  linkStyle 1548 stroke-dasharray: 4 2
  framework_elysia -->|uses language| language_typescript
  linkStyle 1549 stroke-dasharray: 4 2
  framework_express -->|uses language| language_typescript
  linkStyle 1550 stroke-dasharray: 4 2
  framework_fastapi -->|uses language| language_python
  linkStyle 1551 stroke-dasharray: 4 2
  framework_fastify -->|uses language| language_typescript
  linkStyle 1552 stroke-dasharray: 4 2
  framework_fiber -->|uses language| language_go
  linkStyle 1553 stroke-dasharray: 4 2
  framework_flask -->|uses language| language_python
  linkStyle 1554 stroke-dasharray: 4 2
  framework_gin -->|uses language| language_go
  linkStyle 1555 stroke-dasharray: 4 2
  framework_grape -->|uses language| language_ruby
  linkStyle 1556 stroke-dasharray: 4 2
  framework_hono -->|uses language| language_typescript
  linkStyle 1557 stroke-dasharray: 4 2
  framework_koa -->|uses language| language_typescript
  linkStyle 1558 stroke-dasharray: 4 2
  framework_ktor -->|uses language| language_kotlin
  linkStyle 1559 stroke-dasharray: 4 2
  framework_laravel -->|uses language| language_php
  linkStyle 1560 stroke-dasharray: 4 2
  framework_nestjs -->|uses language| language_typescript
  linkStyle 1561 stroke-dasharray: 4 2
  framework_net_http -->|uses language| language_go
  linkStyle 1562 stroke-dasharray: 4 2
  framework_nextjs -->|uses language| language_typescript
  linkStyle 1563 stroke-dasharray: 4 2
  framework_phoenix -->|uses language| language_elixir
  linkStyle 1564 stroke-dasharray: 4 2
  framework_quarkus -->|uses language| language_java
  linkStyle 1565 stroke-dasharray: 4 2
  framework_rails -->|uses language| language_ruby
  linkStyle 1566 stroke-dasharray: 4 2
  framework_react -->|uses language| language_typescript
  linkStyle 1567 stroke-dasharray: 4 2
  framework_sinatra -->|uses language| language_ruby
  linkStyle 1568 stroke-dasharray: 4 2
  framework_slim -->|uses language| language_php
  linkStyle 1569 stroke-dasharray: 4 2
  framework_spring -->|uses language| language_java
  linkStyle 1570 stroke-dasharray: 4 2
  framework_starlette -->|uses language| language_python
  linkStyle 1571 stroke-dasharray: 4 2
  framework_sveltekit -->|uses language| language_typescript
  linkStyle 1572 stroke-dasharray: 4 2
  framework_symfony -->|uses language| language_php
  linkStyle 1573 stroke-dasharray: 4 2
  framework_vapor -->|uses language| language_swift
  linkStyle 1574 stroke-dasharray: 4 2
  framework_vue -->|uses language| language_typescript
  linkStyle 1575 stroke-dasharray: 4 2
```
