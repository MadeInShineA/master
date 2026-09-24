import random

def swap(array: list[int], i: int, j: int) -> None:
    temp = array[i]
    array[i] = array[j]
    array[j] = temp

def partition(array: list[int], left_idx: int, right_idx: int) -> int:
    pivot_value = array[left_idx]

    i = left_idx + 1

    for j in range(left_idx + 1, right_idx):
        if array[j] < pivot_value:
            swap(array, i, j)
            i += 1

    swap(array, left_idx, i-1)

    return i-1

def quicksort(array: list[int], left_index: int, right_index: int) -> None:
    if left_index >= right_index:
        return

    pivot_idx = random.randint(left_index, right_index - 1)

    swap(array, left_index, pivot_idx)

    new_pivot_idx = partition(array, left_index, right_index)

    quicksort(array, left_index, new_pivot_idx)
    quicksort(array,new_pivot_idx + 1, right_index)


# Get the value of the i smallest number of the list
# This is based on the above quicksort implementation
def random_selection(array: list[int], desired_index: int, left_index: int, right_index: int)-> int | None:

    if desired_index < 0 or desired_index >= len(array):
        return None

    def random_selection_rec(array: list[int], desired_index: int, left_index: int, right_index: int)-> int:


        pivot_idx = random.randint(left_index, right_index - 1)

        swap(array, left_index, pivot_idx)

        new_pivot_idx = partition(array, left_index, right_index)

        if new_pivot_idx > desired_index:
            return random_selection_rec(array, desired_index, left_index, new_pivot_idx)
        elif new_pivot_idx < desired_index:
            return random_selection_rec(array, desired_index, new_pivot_idx + 1, right_index)
        else:
            return array[new_pivot_idx]

    return random_selection_rec(array, desired_index, left_index, right_index)




if __name__ == "__main__":
    array = [2, 8, 4, 0, 6, -1]
    quicksort(array, 0, len(array))
    print(array)

    array_2 = [3, 1, 2, 7, 6, 9, 10]
    desired_index = 2
    selected_number = random_selection(array_2, desired_index, 0, len(array_2))

    quicksort(array_2, 0, len(array_2))

    print(f"{selected_number} was selected as the lowest {desired_index + 1}th number in the {array_2} (sorted)")
