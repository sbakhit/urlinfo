# URL Lookup Servie
This service allows users to pass a URL and get back a response indicating if it is known to contain malware.

## Architecture Diagram
This diagram is taken from [optimize-your-spring-boot-application-for-aws-fargate/](https://aws.amazon.com/blogs/containers/optimize-your-spring-boot-application-for-aws-fargate/). It is more or less accurate.
![architecture-diagram](https://github.com/sbakhit/urlinfo/assets/22949276/9d6064f0-c9ef-4116-b259-492b72186563)

## Entrypoint
```bash
URLInfoAppLB-1524785317.us-east-1.elb.amazonaws.com
```

## Available APIs

### Get (`/urlinfo/1/<url>`)
```bash
$ curl --request GET \
  --header "Content-Type: application/json" \
  http://URLInfoAppLB-1524785317.us-east-1.elb.amazonaws.com/urlinfo/1/testurl.com
{
  "Item": {
    "is_safe": false,
    "url": "testurl.com"
  }
}
```

### Create (`/urlinfo/1`)
```bash
$ curl --request POST \
  --header "Content-Type: application/json" \
  --data '{"url":"testurl.com", "is_safe": "True"}' \
  http://URLInfoAppLB-1524785317.us-east-1.elb.amazonaws.com/urlinfo/1
{
  "msg": "Added successfully"
}
```

### Create/Update safe (`/urlinfo/1/<url>/safe`)
```bash
$ curl --request PUT \
  --header "Content-Type: application/json" \
  http://URLInfoAppLB-1524785317.us-east-1.elb.amazonaws.com/urlinfo/1/testurl.com/safe
{
  "ModifiedAttributes": {
    "is_safe": true
  },
  "msg": "Updated successfully"
}
```

### Create/Update unsafe (`/urlinfo/1/<url>/unsafe`)
```bash
$ curl --request PUT \
  --header "Content-Type: application/json" \
  http://URLInfoAppLB-1524785317.us-east-1.elb.amazonaws.com/urlinfo/1/testurl.com/unsafe
{
  "ModifiedAttributes": {
    "is_safe": false
  },
  "msg": "Updated successfully"
}
```

### Delete (`/urlinfo/1/<url>`)
```bash
$ curl --request DELETE \
  --header "Content-Type: application/json" \
  http://URLInfoAppLB-1524785317.us-east-1.elb.amazonaws.com/urlinfo/1/testurl.com
{
  "msg": "Deleted successfully"
}
```


## How to Deploy

### clone
```
$ git clone https://github.com/sbakhit/urlinfo.git
$ cd urlinfo
$ touch .env # edit AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
$ cat .env
AWS_ACCESS_KEY_ID=<access_key>
AWS_SECRET_ACCESS_KEY=<secret_access_key>
REGION_NAME='us-east-1'
```

### make changes and run tests
```bash
$ python3 -m pytest tests
============================================================== test session starts ==============================================================
platform linux -- Python 3.10.12, pytest-7.4.2, pluggy-1.3.0
rootdir: /mnt/c/Users/sbakhit/Desktop/cisco_interview_assignment/urlinfo
collected 8 items

tests/test_urlinfo.py ........                                                                                                            [100%]

=============================================================== 8 passed in 2.36s ===============================================================
```

### push new image to ECR
```bash
# 1. Retrieve an authentication token and authenticate your Docker client to your registry
$ aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 221643473271.dkr.ecr.us-east-1.amazonaws.com

# 2. Build your Docker image using the following command. For information on building a Docker file from scratch see the instructions here . You can skip this step if your image is already built:
``
$ docker build -t urlinfo-app .

# 3. After the build completes, tag your image so you can push the image to this repository:
$ docker tag urlinfo-app:latest 221643473271.dkr.ecr.us-east-1.amazonaws.com/urlinfo-app:latest

# 4. Run the following command to push this image to your newly created AWS repository:
$ docker push 221643473271.dkr.ecr.us-east-1.amazonaws.com/urlinfo-app:latest
```

### update ECS Cluster Service
```bash
$ aws ecs update-service --cluster URLInfoAppClusterUpdate --service URLInfoAppService --force-new-deployment
```

## Thoughts for "Give some thought to the following" Section

### The size of the URL list could grow infinitely, how might you scale this beyond the memory capacity of this VM? **_IMPLEMENTED_**
This would affect the choice of DB. DynamoDB is best here due to its SLA HA of 99.99% and its auto scaling capability. We can also play with the configurations to set some conditions for autoscaling and/or replication

### The number of requests may exceed the capacity of this VM, how might you solve that? **_IMPLEMENTED_**
In order to address this, I made the container(s) set behind an Application Load Balancer and created an Auto Scaling Group with a minimun of 2 and a maximum of 6 containers (each with 2 GB of memory and 1 vCPU). The condition to scale out/in is 60% of CPU usage.

### What are some strategies you might use to update the service with new URLs? Updates may be as much as 5 thousand URLs a day with updates arriving every 10 minutes. **_IMPLEMENTED_**
Since the requirement is 5000 writes per day, we have about 35 writes per 10 minutes. So, setting WCU (Write Capacity Unit) to 5 WCU (I think this is the default) in DynamoDB should satisfy this requirement. Here's why:
```
Assuming 5KB max per write:
  - 5 WCU = 1 write (up to 5 KB) per second capacity
  - this means I should be able to do up to 600 writes per 10 minutes --> more than enough for the 35 writes per 10 minutes requirement
```
