from typing import List


def list_new_ids(recom_ids: List[int], seen_ids: List[int]) -> List[int]:
    filtered_list = [id for id in recom_ids if id not in seen_ids]
    return filtered_list


if __name__ == "__main__":
    print(list_new_ids(recom_ids=[2, 3, 1], seen_ids=[3, 10, 20]))
