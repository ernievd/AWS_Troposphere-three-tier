# To generate just run  - python vpc_stack.py > vpc_stack.yml
# To launch the stack - aws cloudformation create-stack --stack-name Trop-Trial-Stack --template-body file://vpc_stack.yml --region us-east-1
## aws cloudformation update-stack --stack-name Trop-Trial-Stack --template-body file://vpc_stack.yml --region us-east-1 --capabilities CAPABILITY_NAMED_IAM
# LATER FULL FORMED LAUNCH - aws cloudformation create-stack --stack-name Trop-Trial-Stack --template-body file://vpc_stack.yml --region us-east-1 --capabilities CAPABILITY_IAM --parameters file://qa-parameters.json


from troposphere import Ref, Template, Tags, Join, GetAtt
from troposphere.ec2 import VPC, Subnet, NetworkAcl, NetworkAclEntry, InternetGateway, \
    VPCGatewayAttachment, RouteTable, Route, SubnetRouteTableAssociation, SubnetNetworkAclAssociation, \
    EIP, NatGateway, SecurityGroup, SecurityGroups, SecurityGroupRule, SecurityGroupIngress, SecurityGroupEgress
from troposphere.iam import Role, InstanceProfile, Policy
from troposphere.elasticloadbalancingv2 import LoadBalancer, Listener, ListenerRule, Action, TargetGroup

import troposphere.elasticloadbalancingv2 as elb

from awacs.aws import Action
from awacs.aws import Allow
#from awacs.aws import Policy
from awacs.aws import PolicyDocument
from awacs.aws import Principal
from awacs.aws import Statement

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
        Name="QA-MainRoutingTable--TROP"
    )
))

# Create a public route for the main route table linked to the internet gateway so the main table can reach the internet
PublicRoute = t.add_resource(Route(
    "PublicRoute",
    RouteTableId=Ref(MainRouteTable),
    DestinationCidrBlock="0.0.0.0/0",
    GatewayId=Ref(InternetGateway)
))

# DMZ Route table creation
DmzRouteTable = t.add_resource(RouteTable(
    "DmzRouteTable",
    VpcId=Ref(vpc),
    Tags=Tags(
        Name="QA-DMZRouteTable--TROP"
    )
))

# Create a public route for the DMZ route table linked to the internet gateway so the DMZ table can reach the internet
DmzPublicRoute = t.add_resource(Route(
    "DmzPublicRoute",
    RouteTableId=Ref(DmzRouteTable),
    DestinationCidrBlock="0.0.0.0/0",
    GatewayId=Ref(InternetGateway)
))

# Associate the DMZ Subnets to the DMZ route table  AWS::EC2::SubnetRouteTableAssociation
DMZSubnet1aRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
    "DMZSubnet1aRouteTableAssociation",
    RouteTableId=Ref(DmzRouteTable),
    SubnetId=Ref(DMZSubnet1a)
))
DMZSubnet1bRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
    "DMZSubnet1bRouteTableAssociation",
    RouteTableId=Ref(DmzRouteTable),
    SubnetId=Ref(DMZSubnet1b)
))

# Public Route table creation
PublicRouteTable = t.add_resource(RouteTable(
    "PublicRouteTable",
    VpcId=Ref(vpc),
    Tags=Tags(
        Name="QA-PublicRouteTable--TROP"
    )
))

PublicPublicRoute = t.add_resource(Route(
    "PublicPublicRoute",
    RouteTableId=Ref(PublicRouteTable),
    DestinationCidrBlock="0.0.0.0/0",
    GatewayId=Ref(InternetGateway)
))

# Associate the Public Subnets to the public route table - AWS::EC2::SubnetRouteTableAssociation
PublicSubnet1aRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
    "PublicSubnet1aRouteTableAssociation",
    RouteTableId=Ref(PublicRouteTable),
    SubnetId=Ref(PublicSubnet1a)
))
PublicSubnet1bRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
    "PublicSubnet1bRouteTableAssociation",
    RouteTableId=Ref(PublicRouteTable),
    SubnetId=Ref(PublicSubnet1b)
))

# # ###Create Elastic IP USING OTHER NOTATION ####
# import troposphere.ec2 as ec2
# template = Template()
# EEIP01 = ec2.EIP("EElasticIP")
# # EIP01.InstanceId = Ref(i01)
# EEIP01.Domain = "vpc"
# #template.add_resource(EEIP01)
# t.add_resource(EEIP01)
# # ###Create Elastic IP####

# Create Elastic IPs needed for NAT Gateways
QANatGateway1EIP = t.add_resource(EIP(
    "QANatGateway1EIP",
    DependsOn=VPCGatewayAttachment.title,
    Domain="vpc"
))
QANatGateway2EIP = t.add_resource(EIP(
    "QANatGateway2EIP",
    DependsOn=VPCGatewayAttachment.title,
    Domain="vpc"
))

# Create NAT Gateways - associate them to a public subnet so they can reach the internet when needed
NATGatewayAZ1 = t.add_resource(NatGateway(
    "NATGatewayAZ1",
    AllocationId=GetAtt("QANatGateway1EIP", "AllocationId"),
    SubnetId=Ref(PublicSubnet1a),
    Tags=Tags(
        Name="QA-NAT_Gateway-AZ1--TROP"
    )
))
NATGatewayAZ2 = t.add_resource(NatGateway(
    "NATGatewayAZ2",
    AllocationId=GetAtt("QANatGateway2EIP", "AllocationId"),
    SubnetId=Ref(PublicSubnet1b),
    Tags=Tags(
        Name="QA-NAT_Gateway-AZ2--TROP"
    )
))

# Private Route table creation for availability zone 1
PrivateRouteTableAZ1 = t.add_resource(RouteTable(
    "PrivateRouteTableAZ1",
    VpcId=Ref(vpc),
    Tags=Tags(
        Name="QA-PrivateRouteTableAZ1--TROP"
    )
))

# Create a private route for the private route table linked to the NAT so the public table can reach the internet
PrivateNATRoute1 = t.add_resource(Route(
    "PrivateNATRoute1",
    RouteTableId=Ref(PrivateRouteTableAZ1),
    DestinationCidrBlock="0.0.0.0/0",
    NatGatewayId=Ref(NATGatewayAZ1)
))

PrivateSubnet1aRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
    "PrivateSubnet1aRouteTableAssociation",
    RouteTableId=Ref(PrivateRouteTableAZ1),
    SubnetId=Ref(PrivateSubnet1a)
))

# Private Route table creation for availability zone 2
PrivateRouteTableAZ2 = t.add_resource(RouteTable(
    "PrivateRouteTableAZ2",
    VpcId=Ref(vpc),
    Tags=Tags(
        Name="QA-PrivateRouteTableAZ2--TROP"
    )
))

# Create a private route for the private route table linked to the NAT so the public table can reach the internet
PrivateNATRoute2 = t.add_resource(Route(
    "PrivateNATRoute2",
    RouteTableId=Ref(PrivateRouteTableAZ2),
    DestinationCidrBlock="0.0.0.0/0",
    NatGatewayId=Ref(NATGatewayAZ2)
))

PrivateSubnet1bRouteTableAssociation = t.add_resource(SubnetRouteTableAssociation(
    "PrivateSubnet1bRouteTableAssociation",
    RouteTableId=Ref(PrivateRouteTableAZ2),
    SubnetId=Ref(PrivateSubnet1b)
))

# Add IAM Role
#       Good reference -   https://www.programcreek.com/python/example/96280/troposphere.iam.Role
QAEC2RoleTrop = t.add_resource(Role(
    'QAEC2RoleTrop',
    RoleName="QAEC2RoleTrop",
    Policies=[Policy(
        PolicyName="QAs3BuildAccessPolicyCF",
        PolicyDocument={"Version": "2012-10-17",
                        "Statement": [
                            {
                                "Action": [
                                    "s3:*"
                                ],
                                "Effect": "Allow",
                                "Resource": [
                                    "arn:aws:s3:::qa-storage--dashboard/*",
                                    "arn:aws:s3:::qa-storage--dashboard"
                                ]
                            },
                            {
                                "Sid": "Stmt1456922473000",
                                "Effect": "Allow",
                                "Action": [
                                    "logs:CreateLogGroup",
                                    "logs:CreateLogStream",
                                    "logs:PutLogEvents",
                                    "logs:DescribeLogStreams"
                                ],
                                "Resource": ["arn:aws:logs:*:*:*"]
                            }
                        ]
                        },
            )
        ],
    AssumeRolePolicyDocument=PolicyDocument(
        Statement=[
            Statement(
                Effect=Allow,
                Action=[
                    Action("sts", "AssumeRole")
                ],
                Principal=Principal("Service", "ec2.amazonaws.com")
            )
        ]
    ),
    Path='/',
))


myEC2RoleInstanceProfile = t.add_resource(InstanceProfile(
    "myEC2RoleInstanceProfile",
    Roles=[Ref(QAEC2RoleTrop)]
))

# Create a security group
instanceSecurityGroup = t.add_resource(
    SecurityGroup(
        "instanceSecurityGroup",
        GroupDescription='Enable SSH access via port 22',
        SecurityGroupIngress=[
            # SecurityGroupRule(
            #     IpProtocol='tcp',
            #     FromPort='22',
            #     ToPort='22',
            #     CidrIp=Ref(sshlocation_param)),
            SecurityGroupRule(
                IpProtocol='tcp',
                FromPort='22',
                ToPort='22',
                CidrIp='74.94.81.157/32')],
        VpcId=Ref(vpc),
    ))


# Create a Load Balancer security group
LoadBalancerSG = t.add_resource(
    SecurityGroup(
        "LoadBalancerSG",
        GroupDescription='Load balancer security group',
        SecurityGroupIngress=[
            SecurityGroupRule(
                IpProtocol='tcp',
                FromPort='80',
                ToPort='80',
                CidrIp='0.0.0.0/0'),
            SecurityGroupRule(
                IpProtocol='tcp',
                FromPort='443',
                ToPort='443',
                CidrIp='0.0.0.0/0')],
        VpcId=Ref(vpc),
    ))

SGBaseIngress = t.add_resource(SecurityGroupIngress(
    "SGBaseIngress",
    DependsOn=[
        instanceSecurityGroup.title,
        LoadBalancerSG.title
        ],
    GroupId=Ref("instanceSecurityGroup"),
    IpProtocol='tcp',
    FromPort='80',
    ToPort='80',
    SourceSecurityGroupId=Ref("LoadBalancerSG")
))

SGBaseEgress = t.add_resource(SecurityGroupEgress(
    "SGBaseEgress",
    Description="Secures traffic to be allowed out of the LoadBalancerSG to the InstanceSecurityGroup",
    DependsOn=[
        instanceSecurityGroup.title,
        LoadBalancerSG.title
        ],
    GroupId=Ref("LoadBalancerSG"),
    IpProtocol='tcp',
    FromPort='80',
    ToPort='80',
    DestinationSecurityGroupId=Ref("instanceSecurityGroup")
))


LoadBalancer = t.add_resource(LoadBalancer(
    "LoadBalancer",
    Name="QAAppLoadBalancerTrop",
    Scheme="internet-facing",
    Subnets=[
        Ref("DMZSubnet1a"),
        Ref("DMZSubnet1b"),
    ],
    SecurityGroups=[
        Ref("LoadBalancerSG")
    ],
))

# Load balancer target group
ALBTargetGroup = t.add_resource(TargetGroup(
    "ALBTargetGroup",
    HealthCheckIntervalSeconds="30",
    HealthCheckProtocol="HTTP",
    HealthCheckTimeoutSeconds="5",
    HealthyThresholdCount="3",
    Name="ALBTargetGroup",
    Port=80,
    Protocol="HTTP",
    UnhealthyThresholdCount="3",
    VpcId=Ref(vpc)
))


alb_listener = t.add_resource(Listener(
    "albListener",
    Port="80",
    Protocol="HTTP",
    LoadBalancerArn=Ref(LoadBalancer),
    DefaultActions=[elb.Action(
        Type="forward",
        TargetGroupArn=Ref(ALBTargetGroup)
    )]
))



print(t.to_yaml())

