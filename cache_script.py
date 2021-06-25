'''
        self.cache = {
            "query_nearest_by_content": self.set_parameters(["target_index","num_inst","return_origin_size"]),
            "query_nearest_by_style": self.set_parameters(["target_index","num_inst","return_origin_size"]),
            "query_farthest_by_content": self.set_parameters(["target_index","num_inst","return_origin_size"]),
            "query_farthest_by_style": self.set_parameters(["target_index","num_inst","return_origin_size"]),
            "query_by_tag_all": self.set_parameters(["target_index", "num_inst", "tags", "return_origin_size"]),
            "query_by_tag_partial": self.set_parameters(["target_index", "num_inst", "tags", "return_origin_size"]),
            "query_range_by_content": self.set_parameters(["group_index", "num_inst", "return_origin_size"]),
            "query_range_by_style": self.set_parameters(["group_index", "num_inst", "return_origin_size"]),
            "retrieve_one": self.set_parameters(["target_index", "return_origin_size"]),
            "retrieve_many": self.set_parameters(["target_index_list", "return_origin_size"]),
            "browse_by_cluster": self.set_parameters(["num_inst"])
        }
        '''