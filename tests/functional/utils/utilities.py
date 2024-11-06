class Utilities:

    @staticmethod
    def transform_data_to_es_format(
        index_name: str, id_field_name: str, data: list[dict]
    ) -> list[dict]:
        query: list[dict] = []
        for item in data:
            query_item = {
                "_index": index_name,
                "_id": item[id_field_name],
            }
            query_item.update({"_source": item})
            query.append(query_item)

        return query
