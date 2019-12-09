## The drawing controller
* The controller.py is aimed to help you draw results automatically. 

* And its argument parser is based on the **argparse** in python library. 

* All of the functions was tested in the python3.x .

* Python3 requirements:

                            pip install argparse
                            pip install numpy
                            pip install matplotlib

## Quick Start
                           
                            python3 controller.py --ip  {Server IP} --port {Port} --numbers 60 --server_name dtp_server --client_name dtp_client

* --ip          : the ip of **container_server_name** that required 

* --port        : the port of dtp_server that required,default is 2222, and you can randomly choose 

* --numbers     : the numbers of blocks that you can control 

* --server_name : the container_server_name 

* --client_name : the container_client_name 

## Tips 
* more details about parameters 
          
                          python3 controller.py --help