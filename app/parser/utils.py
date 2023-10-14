class Utils:
    @staticmethod
    def exclude_dim_info(data: dict):
        stop_words = ["Вес", "Глубина", "Длина", "Ширина", "Высота", "Страна"]
        keywords = list(data)
        filtered = data

        for keyword in keywords:
            for stopword in stop_words:
                if stopword in keyword:
                    filtered.pop(keyword)
        return filtered
