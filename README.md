Utilising an SDN to Secure an IOT network in a Medical Setting 
CSC7078_KevinBrolly_40313770

Project Scenario
A healthcare centre would like to implement IoT devices into their patient 
monitoring infrastructure as an RFID based patient chart due 
to the inexpensive nature and speed of deployment, they are keen to implement. 

However there have been concerns deploying such devices due to issues 
concerning security, data protection, service continuity and monitoring.

Areas of concern utilising IOT devices includes:
- Lack of device support via firmware/security updates. 
- Weak / default credentials. 
- Device specification limits inbuilt security measures. 
- Issues of maintainability. 
- Due to the inexpensive nature the number of devices 
- Can exponentially grow quickly.

These issues provide malicious actors attack vectors to the health 
centres business network, affecting service and potentially 
compromising patient information and safety.

Network Topology
I have defined a network to demonstrate my Firewall solution.
There is a single switch connecting four networks, as demonstrated below


- s1 represents Switch 1
- h1 represents the Doctor Network.
- l1 represents the Patient Network.
- r1 represents the network hosting Patient Records.
- m1 represents a Public Access Point for patients and visitors.



Attack Type



Proposed Solution
I have implemented a Packet-filtering firewall, utilising flow roles in the RYU 
controller to filter packets based on their ip source and destination. 
Any inbound packets that do not meet the criteria of the flow roles are dropped,
I have developed a whitelist effectively by defining the allowed traffic

A benefit of using such an implementation is that it is not resource intensive 
and should have a low impact on system performance an important factor when 
considering the scalability of IoT devices.

This firewall is stateless, only analysing packets in isolation, 
impacting the overall level of protection it can provide as vulnerabilities 
may be exploited to bypass these conditions. 

Ideally a multi-layered approach to network security would be implemented,
however this is a demonstration of the firewall, further aspects are 
discussed in the repository.

Evaluation Plan



Repository Structure


