import argparse
import requests
import json
import sseclient
import re
import time
import sys
import os
 
#export TOKEN=$(kubectl create token default-editor -n kubeflow-user-example-com --audience=istio-ingressgateway.istio-system.svc.cluster.local --duration=9999h)
if "TOKEN" in os.environ:
    token = os.environ["TOKEN"]
else:
    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImY1ZGZ0ZmdNRnh0V0NnaUFPRjVseTNsZm1IV1J5dGVHZDdRcEk5bDd5V0UifQ.eyJhdWQiOlsiaXN0aW8taW5ncmVzc2dhdGV3YXkuaXN0aW8tc3lzdGVtLnN2Yy5jbHVzdGVyLmxvY2FsIl0sImV4cCI6MTc0NzU2MzQxMCwiaWF0IjoxNzExNTY3MDEwLCJpc3MiOiJodHRwczovL2t1YmVybmV0ZXMuZGVmYXVsdC5zdmMuY2x1c3Rlci5sb2NhbCIsImt1YmVybmV0ZXMuaW8iOnsibmFtZXNwYWNlIjoia3ViZWZsb3ctdXNlci1leGFtcGxlLWNvbSIsInNlcnZpY2VhY2NvdW50Ijp7Im5hbWUiOiJkZWZhdWx0LWVkaXRvciIsInVpZCI6IjQ4ZTc2OTg3LTBkNjYtNDdkZC1iMTNlLTBiNWEzMzQwOTk4NSJ9fSwibmJmIjoxNzExNTY3MDEwLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZWZsb3ctdXNlci1leGFtcGxlLWNvbTpkZWZhdWx0LWVkaXRvciJ9.BSu9SFsk0RlciQlheyaCiqlaApBe_h8RVFIz9HPeEHh56EtpUn8BLTnPbfW-8uC-Xzhiv7uubD24GTzzSyIn2YRPVHkZVIv8Wti4J346UDw1xJGwh96pBzcbYuhybNa5CPMM2AUpI64rp1_mEVFhAd_L-GANWCSo7x1gBk-uDdeLlADXvUeUpqlvU-BNqjMTvhaIKvOhd68D5wBwAB9pD8ynU0BLVXxczJA-MT_gJevcOEo-JCJXi4GlfD7SzTMkn9X1I1uUfAyTZGpFE_4lNYvY7pctQ39uJ3tF9XvOI_ba-QPAnEnlqL5zzFXpR_IZQLKQvgTjxLLYZbQW7DpwGg"
kfp_bearer = "Bearer "+token    
host = "http://10.230.17.54:32549"
#host = "http://localhost:7007"
#host = "http://10.149.8.3:7007"

model_endpoint = "silicon-trt-vllm.kubeflow-user-example-com.example.com"
#headers = {"Content-type": "application/json","Host":model_endpoint }
#headers = {"Content-type": "application/json","Authorization":kfp_bearer,"Host":model_endpoint }
ep_url = "user-org.example.com"
max_tokens = 512
isvc = [
    {"model": "mistral-trt-llm","ep": ep_url, "api_type": "trt", "gen_cmd": "/v2/models/ensemble/generate","stream_cmd": "/v2/models/ensemble/generate_stream"},
    {"model": "mistral-vllm","ep": ep_url, "api_type": "vllm", "gen_cmd": "/generate","stream_cmd": "not supported"},
    {"model": "llama-vllm","ep": ep_url, "api_type": "vllm", "gen_cmd": "/generate","stream_cmd": "not supported"},
    {"model": "llama-3-vllm","ep": ep_url, "api_type": "vllm", "gen_cmd": "/generate","stream_cmd": "not supported"},
    {"model": "llama-trt-llm", "ep": ep_url, "api_type": "trt", "gen_cmd": "/v2/models/ensemble/generate","stream_cmd": "/v2/models/ensemble/generate_stream"},
    {"model": "silicon-trt-vllm", "ep": ep_url, "api_type": "trt", "gen_cmd": "/v2/models/vllm_model/generate","stream_cmd": "/v2/models/vllm_model/generate_stream"}
]

def test_stream(model):
    url = host + model["stream_cmd"]
    headers = {"Content-type": "application/json","Host":model["model"]+"."+model["ep"] }
    if model["api_type"] == "trt":
        data = json.dumps(
            {
            "text_input": "Tell me about Silicon Valley and Stanford University, and name the top 10 inventions?",
                "parameters": {
                    "max_tokens": 512,
                    "stream": True
                }
            }
        )

    else: #vllm
        print("Not Supported")
        # url = host + "/generate"
        # data = json.dumps(
        #     {
        #         "prompt": "Tell me about Silicon Valley and Stanford University, and name the top 10 inventions?",
        #         "max_tokens": 512,
        #         "stream": "true"
        #     }
        #)

    resp = requests.post(url=url, stream=True, headers=headers, data=data)
    for line in resp.iter_lines():
        if line:
            sline = line.decode('utf-8')
            sline = sline[6:]
            data_dict = json.loads(sline)
            print(data_dict['text_output'],end='',flush=True)
    print("\n")    

def test_model(model):
    # This is a placeholder for whatever testing or actions you need to perform with the model dictionary
    print(f"Model Details: {model}")
    url = host + model["gen_cmd"]
    headers = {"Content-type": "application/json","Host":model["model"]+"."+model["ep"] }
    print(url,headers)
    if model["api_type"] == "vllm":
        data = json.dumps(
            {
                "prompt": "Tell me about Silicon Valley and Stanford University, and name the top 10 inventions?",
                "max_tokens": max_tokens
            }
        )
    else:
        data = json.dumps(
            {
            "text_input": "Tell me about Silicon Valley and Stanford University, and name the top 10 inventions?",
                "parameters": {
                    "max_tokens": max_tokens
                }
            }
        )


    resp = requests.post(url=url, stream=False, headers=headers, data=data)
    #response = json.loads(resp.text)
    print(resp.text,end='\n')
    

if __name__ == '__main__':
    #streaming

    parser = argparse.ArgumentParser(description="testing model..")
    parser.add_argument("model", type=str, help="The model name to test.")
    parser.add_argument("--stream", type=str, choices=['on', 'off'], default='off', help="Enable or disable streaming (default: off).")
    # Parse arguments
    args = parser.parse_args()

    # Check if the provided model is in the list
    model_found = next((item for item in isvc if item["model"] == args.model), None)

    if model_found:
        print(f"Model found: {model_found}")
        #generate_oneshot(model_found)
        if args.stream =="off":
            test_model(model_found)
        else:
            test_stream(model_found)

    else:
        print("Model not supported. Please choose from the following models:")
        for item in isvc:
            print(item["model"])
