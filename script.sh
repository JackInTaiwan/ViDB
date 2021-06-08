# Run the ViDB server
python3 -m cli.server


# Run client test cases
python3 -m test_case.client_insert -o insert_one_by_path
python3 -m test_case.client_insert -o insert_many_by_dir
python3 -m test_case.client_insert -o insert_one_by_byte
python3 -m test_case.client_insert -o insert_many_by_byte

python3 -m test_case.client_update -o update_one_by_id
python3 -m test_case.client_update -o update_many_by_ids

python3 -m test_case.client_browse -o browse_by_random
python3 -m test_case.client_browse -o browse_by_cluster

python3 -m test_case.client_retrieve -o retrieve_one
python3 -m test_case.client_retrieve -o retrieve_many

python3 -m test_case.client_query -o query_nearest_by_content
python3 -m test_case.client_query -o query_nearest_by_style
python3 -m test_case.client_query -o query_farthest_by_content
python3 -m test_case.client_query -o query_farthest_by_style
python3 -m test_case.client_query -o query_by_tag_all
python3 -m test_case.client_query -o query_by_tag_partial
python3 -m test_case.client_query -o query_range_by_content
python3 -m test_case.client_query -o query_range_by_style

python3 -m test_case.client_delete -o delete_one_by_id
python3 -m test_case.client_delete -o delete_many_by_ids
python3 -m test_case.client_delete -o delete_all_data
