# To generate just run  - python vpc_stack.py > vpc_stack.yml
# To launch the stack - aws cloudformation create-stack --stack-name Trop-Trial-Stack --template-body file://vpc_stack.yml --region us-east-1

# LATER FULL FORMED LAUNCH - aws cloudformation create-stack --stack-name Trop-Trial-Stack --template-body file://vpc_stack.yml --region us-east-1 --capabilities CAPABILITY_IAM --parameters file://qa-parameters.json

from troposphere import Ref, Template, Tags, Join
from troposphere.ec2 import VPC, Subnet, NetworkAcl, NetworkAclEntry, InternetGateway, \
    VPCGatewayAttachment, RouteTable, Route, SubnetRouteTableAssociation, SubnetNetworkAclAssociation

VPC_NETWORK = "192.168.0.0/19"
VPC_DMZ_A = "192.168.0.0/23"
VPC_DMZ_B = "192.168.2.0/23"
VPC_PUBLIC_A = "192.168.4.0/23"
VPC_PUBLIC_B = "192.168.6.0/23"
VPC_PRIVATE_A = "192.168.8.0/23"
VPC_PRIVATE_B = "192.168.10.0/23"


t = Template()

t.add_description("Stack creating a VPC")

# Create the VPC
vpc = t.add_resource(VPC(
    "VPC",
    CidrBlock=VPC_NETWORK,
    EnableDnsSupport=True,
    EnableDnsHostnames=False,
    InstanceTenancy="default",
    Tags=Tags(
        Owner="Ernie Van Duyne",
        Environment="QA"
    )
))

# Create the subnets
DMZSubnet1a = t.add_resource(Subnet(
    "DMZSubnet1a",
    AvailabilityZone=Join("", [Ref("AWS::Region"), "a"]),
    VpcId=Ref(vpc),
    CidrBlock=VPC_DMZ_A,
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), " DMZ subnet A"]),
     )
))
DMZSubnet1b = t.add_resource(Subnet(
    "DMZSubnet1b",
    AvailabilityZone=Join("", [Ref("AWS::Region"), "b"]),
    VpcId=Ref(vpc),
    CidrBlock=VPC_DMZ_B,
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), " DMZ subnet B"]),
     )
))
PublicSubnet1a = t.add_resource(Subnet(
    "PublicSubnet1a",
    AvailabilityZone=Join("", [Ref("AWS::Region"), "a"]),
    VpcId=Ref(vpc),
    CidrBlock=VPC_PUBLIC_A,
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), " Public subnet A"]),
     )
))
PublicSubnet1b = t.add_resource(Subnet(
    "PublicSubnet1b",
    AvailabilityZone=Join("", [Ref("AWS::Region"), "b"]),
    VpcId=Ref(vpc),
    CidrBlock=VPC_PUBLIC_B,
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), " Public subnet B"]),
     )
))
PrivateSubnet1a = t.add_resource(Subnet(
    "PrivateSubnet1a",
    AvailabilityZone=Join("", [Ref("AWS::Region"), "a"]),
    VpcId=Ref(vpc),
    CidrBlock=VPC_PRIVATE_A,
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), " Private subnet A"]),
     )
))
PrivateSubnet1b = t.add_resource(Subnet(
    "PrivateSubnet1b",
    AvailabilityZone=Join("", [Ref("AWS::Region"), "b"]),
    VpcId=Ref(vpc),
    CidrBlock=VPC_PRIVATE_B,
    Tags=Tags(
        Name=Join("", [Ref("AWS::StackName"), " Private subnet B"]),
     )
))

# Create an Internet Gateway
InternetGateway = t.add_resource(InternetGateway(
    "InternetGateway",
    Tags=Tags(
        Name="Internet-Gateway-Trop",
        Environment="QA"
    )
))

# Attach the Gateway to the VPC
VPCGatewayAttachment = t.add_resource(VPCGatewayAttachment(
    "InternetGatewayAttachment",
    VpcId=Ref(vpc),
    InternetGatewayId=Ref(InternetGateway)
))

# Main Route table creation
MainRouteTable = t.add_resource(RouteTable(
    "MainRouteTable",
    VpcId=Ref(vpc),
    Tags=Tags(
        Name="QA-RoutingTable--TROP"
    )
))

# Create a public route for the main route table linked to the internet gateway so the main table can reach the internet
PublicRoute = t.add_resource(Route(
    "PublicRoute",
    RouteTableId=Ref(MainRouteTable),
    DestinationCidrBlock="0.0.0.0/0",
    GatewayId=Ref(InternetGateway)
))



print(t.to_yaml())

