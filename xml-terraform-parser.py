"""
Python Script for Translating Draw.io XML-Exported Architectural Diagrams into Terraform Files

The script is specifically tailored for the Kubernetes provider, so it will generate Kubernetes resources.
Each object's name in the diagram must adhere to one of the following formats:

1. 'imagename' (must be a valid Docker image name stored on Docker Hub)
2. 'imagename_resourcetype' (optional 'resourcetype'. Value: [pod/deployment]; Default: [pod])
3. 'imagename_resourcetype_port' (optional 'port' on which the service should redirect the requests (the port on which the app will be listening). Value: [1024-65535] . Default: 3000)

The need for communication between resources can be signified by arrows connecting them. In cases where pods or deployments are targeted by arrows, additional services will be created on top of each to ensure reliable communication.
A resource that needs to be reachable from outside the cluster, must be the target of an arrow with no source. In that case the service created on top will be of NodePort type.
"""

import xml.etree.ElementTree as ET
import time
import random
from datetime import datetime
from hcl_templates import *
import sys

XML_FILE_NAME = "architectural-diagram.xml"  # name of the xml file to be parsed
TERRAFORM_FILE_PATH = "./terraform/main.tf"  # path of the new/updated terraform file


# the script works by looping over all the element in the xml file: pods, deployments and arrows
# pods and deployments are written instantly when they're found
# services are saved and written only at the end of the parse when all the arrows have been parsed and the service_type is definitive


services = {}
# data structure containing all the services that at the end of the parsing will be written into file
# the arrow processing add the service_type (NodePort/ClusterIP)
# the resource processing add all the other infos (name, target_port and the underlyng resource (pod/deployment))



namespaces_created = (
    set()
)  # data structure that keeps tracks of the already created namespaces. One namespace gets created for each image name

svcs = 0
deps = 0
pods = 0
ns = 0
file = open(TERRAFORM_FILE_PATH, "w")


tree = ET.parse(XML_FILE_NAME)
mxfile = tree.getroot()
elements = mxfile.iter("mxCell")


# loop over the elements of the architectural diagram
for e in elements:
    style = e.get("style")

    if not style:
        continue

    name = e.get("value")
    target = e.get("target")
    
    # distinction between arrows and objects. Arrows are supposed to have at least a target attribute, objects don't
    if target:  # arrow
        source = e.get("source")

        # distinction between arrows with no source (NodePort service) and arrow with a source (ClusterIP service)
        if not source:
            service_type = "NodePort"
        else:
            service_type = "ClusterIP"

        # detection of the direction of the arrow (uni/bidirectional)
        bidirectional = False
        for splitted in style.split(
            ";"
        ):  # arrows are unidirectional if they don't have 'styleArrow' inside their style attribute or if they have it equal to none. Else they're bidirectional
            if "startArrow" not in splitted:
                continue
            bidirectional = False if splitted.split("=")[1] == "none" else True
            break

        print(
            f"[{datetime.now()}]",
            f"Arrow processing (bidirectional:{bidirectional}, source-id:{source}, target-id:{target})",
        )

        # add service_type to a new service or to a service already filled with info
        if target not in services:
            services[target] = {} 
        if "service_type" not in services[target] or services[target]['service_type']!="NodePort":
            services[target]["service_type"] = service_type  
            
        if (
            not bidirectional or not source
        ):  # if the arrow is not bidirectional or the source doesnt'exist, no additional services needs to be saved
            continue
        
        if source not in services:
            services[source] = {}
        if "service_type" not in services[source] or services[source]['service_type']!="NodePort":
            services[source]["service_type"] = "ClusterIP"  

    elif name != "":  # resource
        splitted_name = name.strip().lower().split("_")
        image = splitted_name[0]

        if (
            "/" in image
        ):  # if the imagename contains a slash, it cannot be used to name resources
            stringable_name = image.split("/")[1]
        else:
            stringable_name = image

        # check of the eventual resource type and target_port
        target_port = 3000

        if len(splitted_name) == 1:
            type = "pod"
        elif len(splitted_name) == 2:
            type = splitted_name[1]
        elif len(splitted_name) == 3:
            type = splitted_name[1]
            target_port = splitted_name[2]
            if (
                not target_port.isnumeric()
                or int(target_port) < 1024
                or int(target_port) > 65535
            ):
                print("Port number is not valid! Must be between 1024 and 65535")
                file.truncate()
                sys.exit(1)
        else:
            print("Name format is not valid! Must be image[_type[_port]]")
            file.truncate()
            sys.exit(1)

        print(
            f"[{datetime.now()}]", f"Resource processing (image:{image}, kind:{type})"
        )

        random_feed = str(time.time_ns())

        # namespace creation
        if stringable_name not in namespaces_created:
            print(f"[{datetime.now()}]", f"Writing namespace resource...")
            ns += 1
            file.write(namespace_definition_template.format(
                stringable_name=stringable_name
            ))
            namespaces_created.add(stringable_name)
        

        # writing of the hcl based on the resource type
        match type:
            case "pod":
                file.write(pod_definition_template.format(
                    namespace_name=f"kubernetes_namespace.{stringable_name}_namespace.metadata.0.name",
                    stringable_name=stringable_name,
                    random_feed=random_feed,
                    image=image,
                ))
                print(f"[{datetime.now()}]", "Writing pod resource...")
                pods += 1
            case "deployment":
                replicas = random.randint(2, 10)

                file.write(deployment_definition_template.format(
                    namespace_name=f"kubernetes_namespace.{stringable_name}_namespace.metadata.0.name",
                    replicas=replicas,
                    stringable_name=stringable_name,
                    random_feed=random_feed,
                    image=image,
                ))
                print(f"[{datetime.now()}]", "Writing deployment resource...")
                deps += 1
            case _:
                print("Resource type is not valid! Must be pod, deployment or blank")
                file.truncate()
                sys.exit(1)

        
        # add infos to a new service or to a service already filled with service_type

        infos = {
            "stringable_name": stringable_name,
            "type": type,
            "random_feed": random_feed,
            "target_port": target_port,
        }
        if e.get("id") in services:
            services[e.get("id")].update(infos)

        else:
            services[e.get("id")] = infos

    else:
        print(f"[{datetime.now()}]", "Object non recognised...")

# writing all the services to file
for key in services:
    element = services[key]
    if 'service_type' not in element:
        continue
    print(
        f"[{datetime.now()}]",
        f"Writing service resource of type {element['service_type']}...",
        end="",
    )
    if element["service_type"] == "NodePort":
        node_port = random.randint(30000, 32767)
        print(f"Listening on port {node_port}")

        node_str = f"node_port = {node_port}"
    else:
        node_str = ""
        print("")

    file.write(
        service_definition_template.format(
            namespace_name=f"kubernetes_namespace.{element['stringable_name']}_namespace.metadata.0.name",
            node_port=node_str,
            target_port=element["target_port"],
            service_type=element["service_type"],
            stringable_name=element["stringable_name"],
            random_feed=str(time.time_ns()),
            deployment_app_label=f"kubernetes_{element['type']}.{element['stringable_name']}_{element['type']}_{element['random_feed']}.metadata.0.labels.app",
        )
    )
    svcs += 1

file.close()


print(
    f"\nThe terraform file is completed. Total written resources: namespaces ({ns}), pods({pods}), deployments({deps}), services({svcs})"
)





