# Please make sure that stream connector has been installed.
from stream_connector import StreamConnector

# Example program
# The use case number can be defined by varying the number in use case variable
MASTER_ADDR = "10.42.130.68"
MASTER_PORT = 8080


def read_data_from_file(path):
    func_data = bytearray()

    with open(path, 'rb') as f:
        lines = f.readlines()

        for line in lines:
            func_data += line

    return func_data


def read_sample_data(path):
    data = bytearray()
    # byte data (text file)
    with open(path, 'rb') as f:
        lines = f.readlines()

        for line in lines:
            data += line

    return data


if __name__ == '__main__':

    # Initialize connector driver
    sc = StreamConnector(MASTER_ADDR, MASTER_PORT)

    # Defined function
    f_list = {
        'summation': 'summation_python2_7.p',
        'histogram': 'histogram_python2_7.p'
    }

    # Register function to server
    for key, value in f_list.items():
        if not sc.push_function(key, read_data_from_file(value)):
            print("Function registration error!")
            quit(1)

    # Define data to test
    d_list = {
        'summation': read_data_from_file('str_array.txt'),
        'histogram': read_data_from_file('lena512.bmp')
    }

    # Generate a sample stream order
    item_number = 10
    stream_order = [0] * item_number
    import random
    for i in range(item_number):
        stream_order[i] = (i, 'summation' if (random.randrange(1, 100) % len(d_list)) == 0 else 'histogram')

    # Stream according to the random order
    for _, obj_type in stream_order:
        d_container = sc.get_data_contaner()

        # Assign data to container
        d_container += d_list[obj_type]

        if sc.is_master_alive():
            print("\nStart streaming " + obj_type + ".")
            sc.send_data(obj_type, d_container)

    print("Finish.")
