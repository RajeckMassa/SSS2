
# SSS2: Remote Attestation demo in Python
#### Amber Zitman & Rajeck Massa
This project is made for the second assignment for the course 'Systems and Software Security' at Leiden University. This project contains a demo of remote attestation, programmed in Python. 

The demo assumes that the software on the prover (client) runs on a 'TPM', and can therefore not be altered. Furthermore, the demo assumes that the connection can not be intercepted. That is now possible, since we do not use the 'WSS' (like HTTPS for internet), but the 'WS' (like HTTP for internet) connection 

At last, we included the encryption key for AES in the project. Leaving an encryption key in a public repo is something you should **never** do (a better option is to use environment variables!). However, for the simplicity of running this demo 'out of the box' and due the fact that this key is not used anywhere else, we decided to leave the key here.

The following steps can be followed to run the demo on your own machine:
1. Create an virtual environment using `python3 -m venv venv`
2. Activate the venv using `source venv/bin/activate`
3. Install the required packages using `pip install -r requirements.txt`
4. Create the hash using `python3 Client/create\_hash.py > Server/hash.txt`. Call this file from the root directory.
5. Open two terminal windows. In the first one, CD into the 'Server' directory and call the server using `python3 server.py`. The local IP-address is shown on the screen.
6. In the second terminal window, CD into the 'Client' directory and call the client using `python3 client.py -i (ip-address)`.
