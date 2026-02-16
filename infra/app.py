import aws_cdk as cdk
from aws_cdk import (
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct

class AetheriumInfraStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC for the cluster
        vpc = ec2.Vpc(self, "AetherVpc", max_azs=2)

        # EKS Cluster
        cluster = eks.Cluster(
            self, "AetherCluster",
            vpc=vpc,
            default_capacity=2,
            default_capacity_instance=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM),
            version=eks.KubernetesVersion.V1_29,
        )

        # Add HPA support (Metrics Server is usually required)
        cluster.add_helm_chart(
            "MetricsServer",
            chart="metrics-server",
            repository="https://kubernetes-sigs.github.io/metrics-server/",
            namespace="kube-system"
        )

        # IAM Role for the SystemHealthAgent
        health_agent_role = iam.Role(
            self, "HealthAgentRole",
            assumed_by=iam.ServicePrincipal("eks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSClusterPolicy")
            ]
        )

        cdk.CfnOutput(self, "ClusterName", value=cluster.cluster_name)

app = cdk.App()
AetheriumInfraStack(app, "AetheriumInfraStack")
app.synth()
