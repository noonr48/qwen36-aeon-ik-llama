# Comprehensive Production Matrix

- github_mcp_commits_fix_repeat | q4nl_ckpt386_s025_repeat2_t07_graph_fa_c65536_pair49 | pass=False | score=0.875 | rc=1 | elapsed=367s
  - checks: build_passes=yes, handler_reads_branch=yes, output_mentions_branch=yes, readme_mentions_get_commits_branch=yes, request_does_not_use_sha_commit_path=yes, request_uses_path_param=yes, request_uses_sha_branch=yes, schema_has_branch=no
- github_mcp_pr_details_fix | q4nl_ckpt386_s025_repeat2_t07_graph_fa_c65536_pair49 | pass=False | score=0.625 | rc=0 | elapsed=331s
  - checks: build_passes=yes, does_not_use_list_additions=yes, does_not_use_list_changed_files=yes, does_not_use_list_deletions=yes, fetches_pr_detail_endpoint=yes, uses_detail_additions=no, uses_detail_changed_files=no, uses_detail_deletions=no
- local_search_kill_excess_fix | q4nl_ckpt386_s025_repeat2_t07_graph_fa_c65536_pair49 | pass=True | score=1.0 | rc=0 | elapsed=148s
  - checks: build_passes=yes, does_not_use_blanket_pkill=yes, has_targeted_kill_logic=yes, references_process_pid=yes
- local_search_search_timeout_fix | q4nl_ckpt386_s025_repeat2_t07_graph_fa_c65536_pair49 | pass=False | score=0.75 | rc=1 | elapsed=343s
  - checks: build_passes=yes, handler_passes_timeout=no, handler_reads_timeout=yes, schema_has_timeout=yes
- local_search_web_search_race_fix | q4nl_ckpt386_s025_repeat2_t07_graph_fa_c65536_pair49 | pass=False | score=0.5 | rc=0 | elapsed=154s
  - checks: build_passes=yes, does_not_wait_all_settled=no, still_has_multiple_engines=yes, uses_first_success_pattern=no
