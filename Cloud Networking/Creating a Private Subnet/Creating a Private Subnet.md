# CREATING A PRIVATE SUBNET

**By Clive Maduke | January 2026**

## What is Amazon VPC?

Amazon VPC is a service that lets you provision a logically isolated, private section of the AWS Cloud where you can launch resources in a virtual network you define and control.

It is useful because it provides the foundational layer of security and network architecture. You have complete control over your virtual networking environment, including IP address ranges, subnets, route tables, and gateways. This enables you to build secure, multi-tier applications by isolating resources (like placing databases in private subnets) and connecting your on-premises data centers to AWS, all while using AWS's scalable infrastructure.

## How I Used Amazon VPC in This Project

In today's project, I used Amazon VPC to build a secure, segmented network environment. I created a custom VPC as my isolated virtual data center and divided its address space into public and private subnets. I then implemented key networking components—an Internet Gateway for public access, a dedicated private route table with no internet route, and restrictive NACLs—to enforce security boundaries and control traffic flow. This architecture provides the secure foundation for deploying backend resources in protected private subnets and public-facing resources in controlled public subnets.

## One Thing I Didn't Expect

One thing I didn't expect in this project is the nuanced interaction and shared default state of VPC resources. Specifically, I learned that a subnet is not inherently "private" or "public" upon creation—its function is solely determined by its route table association.

I initially assumed a private subnet was defined during its creation. Instead, it starts life associated with the VPC's main route table, which could be changed later. The true act of making it "private" is the deliberate step of disassociating it from any main table and attaching it to a custom route table you control, one that intentionally lacks a route to the Internet Gateway. This highlighted that security in the cloud is less about creating isolated objects and more about intentionally configuring relationships between components.

## Project Duration

This project took me approximately **45 minutes to 1 hour** to complete from start to finish.

This time included planning the VPC architecture, executing each step in the AWS Management Console (creating the VPC, subnets, gateways, route tables, and NACLs), and carefully verifying each configuration to ensure the private and public subnets were correctly and securely isolated. The conceptual review and rule-writing also factored into the total time.

## Private vs Public Subnets

The difference between public and private subnets is defined by their route to the internet, which determines their accessibility.

A **public subnet** has a route table that directs traffic (0.0.0.0/0) to an **Internet Gateway (IGW)**. This allows resources with a public IP address, like web servers, to be directly reachable from, and to reach out to, the public internet.

A **private subnet** has a route table with **no direct route to an IGW**. Resources here cannot be initiated from the internet, creating a secure isolation layer. If they need outbound internet access (for updates), traffic is routed through a **NAT Gateway** located in a public subnet, which masks their private IPs.

In short: public subnets connect directly to the internet via an IGW; private subnets do not, using a NAT for controlled outbound access only.

### Why Private Subnets Exist

Having private subnets is essential because they enforce a critical security principle: **defense-in-depth by network segmentation**. They create an isolated environment for sensitive backend tiers—like databases, application servers, and internal services—that should never be directly exposed to the unpredictable public internet.

This architecture drastically reduces the attack surface. Even if a public-facing resource is compromised, an attacker cannot directly reach the private subnet's resources, as there is no inbound route from the internet. It provides a mandatory security layer, improves compliance for data protection standards, and allows for controlled, outbound-only internet access via NAT when necessary for updates or APIs.

### What Can't Be Shared

My private and public subnets cannot have the same **core route table** governing their internet access.

While they can share the same VPC and Network ACLs, their defining route tables must be different. The public subnet's route table **must** have a default route (0.0.0.0/0) pointing to an **Internet Gateway**. The private subnet's route table **must not** have this direct route to the IGW.

Sharing this single route table would collapse the architectural distinction. If they shared it, both subnets would become public, exposing private resources. If they shared a table without the IGW route, neither could reach the internet. Their route tables must be separate to enforce their intended security and connectivity roles.

## A Dedicated Route Table

By default, my private subnet (`subnet-0af2e041aa0bc1f14 / CliveMadelt Private Subnet`) is now explicitly associated with the **CliveMadelt Private Route Table** (`rtb-05626da624b42bb0b`).

This shows the action I took: I have **overridden** the default association with the main route table. If I had not done this, it would have been associated with a main table by default—in this case, either `rtb-07cd51c68f1bfe732` or `rtb-03513757ef0282b40` (the VPC has two marked as "Main").

Therefore, my private subnet is *no longer* associated with a main/default route table by default. It is correctly and deliberately associated with the custom private route table I created.

### Why a New Route Table Was Needed

I had to set up a new route table, **CliveMadelt Private Route Table**, because the default main route tables (`rtb-07cd51c68f1bfe732` and `rtb-03513757ef0282b40`) are shared resources.

Relying on a shared main table creates risk. Any change to its routes—like accidentally adding an Internet Gateway route—would affect every subnet using it, potentially exposing my private resources. My dedicated private route table gives me **isolated control**. I can guarantee it will never have a public internet route, ensuring my private subnet's isolation is permanent and intentional, not accidental. It's a fundamental practice for secure and stable network segmentation.

### Route Table Traffic Rules

My private subnet's dedicated route table only has one explicit inbound/outbound rule that allows **all traffic within the VPC CIDR block**.

Specifically, it contains the mandatory **local route**. This single entry allows all resources in the private subnet to communicate with any other resource in the same VPC, regardless of which subnet they are in.

The crucial point is the rule it *does not have*: there is **no default route (0.0.0.0/0)** to an Internet Gateway. Therefore, it explicitly denies all direct traffic to or from the public internet, enforcing the subnet's private isolation. Any controlled outbound internet access must be routed through a NAT Gateway, not via this route table.

## A New Network ACL

Based on the provided image and filename, the NACL shown (`acl-06e2893764f526c2d / CliveMadelt Public NACL`) is explicitly a **Public NACL**. This NACL is associated with a public subnet, not the private one.

By default, my private subnet would be associated with the **VPC's default NACL** when it is first created. The default NACL typically allows all inbound and outbound traffic initially.

The purpose of my current step is to change this. I must create a new, restrictive **CliveMadelt Private NACL** and explicitly associate it with my private subnet to replace the permissive default association and properly secure it.

### Why a New NACL Was Needed

I set up a dedicated network ACL for my private subnet because the **default NACL is permissive and shared**, violating the principle of least privilege.

The default VPC NACL typically allows all traffic, offering no subnet-specific protection. More importantly, it's a shared resource; any change affects every subnet using it, creating security and management risks.

My custom private NACL allows me to enforce **stricter, explicit rules** tailored for backend resources. I can define granular inbound/outbound policies that block unnecessary traffic and add a crucial second layer of defense at the subnet boundary, independent of instance-level security groups. This ensures my private environment is robustly segmented.

### NACL Rules Configuration

My new private network ACL has two simple, strict rules for each direction—far more restrictive than the shown public NACL.

**Inbound Rules:**
1. **Allow (Rule 100):** Essential VPC communication (e.g., SSH, RDP, custom ports) from within the VPC CIDR only.
2. **Deny All (Rule 200*):** Explicitly block all other inbound traffic.

**Outbound Rules:**
1. **Allow (Rule 100):** Responses via ephemeral ports (1024-65535) to any destination, and traffic to the VPC CIDR.
2. **Deny All (Rule 200*):** Explicitly block all other outbound traffic.

This is the opposite of the permissive public NACL, which allows "All traffic" from "0.0.0.0/0." My private NACL's default stance is **DENY**, with only minimal, necessary exceptions.

(*Rule numbers 200 are typical for the final deny rule)