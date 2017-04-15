# Please make sure that stream connector has been installed.
from stream_connector import StreamConnector

# Example program
# The use case number can be defined by varying the number in use case variable
MASTER_ADDR = "127.0.0.1"
MASTER_PORT = 8080

if __name__ == '__main__':
    sc = StreamConnector(MASTER_ADDR, MASTER_PORT)
    data = sc.get_data_contaner()

    """
    # byte data (text file)
    with open('str_array.txt', 'rb') as f:
        lines = f.readlines()

        for line in lines:
            data += line
    """

    # Byte data (image file)
    with open('lena512.bmp', 'rb') as f:
        lines = f.readlines()

        for line in lines:
            data += line

    if sc.is_master_alive():
        sc.send_data(data)
    print("Finish.")
