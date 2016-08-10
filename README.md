How to stream the data?
Please note that stream connector require urllib3.

Setup Stream Connector
1. Downlaod the stream connector
git clone https://github.com/beirbear/HarmonicSC.git

2. Change directory into the stream connector
cd HarmonicSC

3. Install stream connector
sudo python3.5 setup.py install


How to use StreamConnector?

1. Import module
from stream_connector import StreamConnector

2. Instanitiate
sc = StreamConnector(MASTER_ADDR, MASTER_PORT, [TOKEN], [IDEL_TIME], [MAX_RETRY])

3. Stream the data
data must be in a bytearray type
sc.send_data(data)
