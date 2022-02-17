import boto3
import time
import errors
import kopf
import objects
import fluxutils
import kubernetes.client
from kubernetes.client.rest import ApiException
import yaml
import k8sUtils
refactor_space_client = boto3.client('migration-hub-refactor-spaces')

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    settings.persistence.finalizer = 'refactorspace-operator.eks.amazonaws.com/finalizer'
    settings.watching.server_timeout = 60
    settings.watching.connect_timeout = 60

@kopf.on.create('refactorspaceservice')
def create_fn(spec,meta, status, **kwargs):

    svcname=meta.get("name")
    cfgname_with_namespace = spec.get("configurationName")
    namespace = meta.get("namespace")
    svcSelector = spec.get("serviceSelector").get("matchLabels") 
    protocol = spec.get("protocol").lower()
    method = spec.get("method")
    route = spec.get("route")  
    healthCheckPrefix = spec.get("healthCheckPrefix")  
    if healthCheckPrefix is None:
        healthCheckPrefix=""
    prefix = spec.get("prefix")  
    if prefix is None:
        prefix= ""

    status = {'route': route }

    cfgname_arr = cfgname_with_namespace.split(".")
    cfgname=cfgname_arr[0]
    cfgname_namespace = namespace

    if (len(cfgname_arr)>1):
        cfgname = cfgname_arr[1]
        cfgname_namespace = cfgname_arr[0]

    cfg = {}

    print("svcname:"+svcname)
    print("namespace:"+namespace)
    print(svcSelector)
    print("cfgname:"+cfgname)
    print("cfgname_namespace:"+cfgname_namespace)

    try:
        #load RefcatorSpaceConfig object specified in the RefcatorSpaceService spec
        cfg = k8sUtils.get_flux_config(cfgname,cfgname_namespace)

        status["appId"]=cfg.get_appId()
        status["envId"]=cfg.get_envId()
        status["vpcId"]=cfg.get_vpcId()

        print("appId:"+cfg.get_appId())
        print("envId:"+cfg.get_envId())
        print("vpcId:"+cfg.get_vpcId())

        print ("create_fn: OK1")

    except errors.ObjectNotFound as e:
        status["state"]='ERROR'
        status["message"]=str(e)
        print (str(e))
        return status   #stop processing

    try:
        endpoint = k8sUtils.getk8sServiceEndPoint(namespace,svcSelector,protocol)
        print(endpoint)
        print ("create_fn: OK2")
    except errors.InvalidSpecError as e:
        status["state"]='ERROR'
        status["message"]=str(e)
        print (str(e))
        return status   #stop processing
    
    try:
        print ("create_fn: OK3")
        print (prefix)
        print ("create_fn: OK3.1")
        serviceId = fluxutils.create_flux_service(cfg.get_envId(),cfg.get_appId(),cfg.get_vpcId(),
                                                svcname,endpoint["url"]+prefix,endpoint["url"]+healthCheckPrefix, 
                                                route, method)
        print ("create_fn: OK4")
    except BaseException as e:
        status["state"]='ERROR'
        status["message"]=str(e)
        print (str(e))
        return status   #stop processing

    print("serviceId:"+serviceId)

    status["state"]='SUCCESS'
    status["k8sService"]=endpoint["serviceName"]
    status["endpoint"]=endpoint["url"]+prefix
    status["serviceId"]=serviceId

    try:
        k8sUtils.add_finalizer_to_config(cfgname,cfgname_namespace,namespace,svcname, serviceId)
    except BaseException as e:
        status["state"]='ERROR'
        status["message"]=str(e)
        print (str(e))
        return status   #stop processing

    return status

@kopf.on.create('refactorspaceconfig')
def cfg_create(spec,meta, status, **kwargs):
    pass


@kopf.on.delete('refactorspaceservice')
def delete_fn(spec,meta, status, **kwargs):

    print("delete_flux_service")

    svcname=meta.get("name")
    cfgname_with_namespace = spec.get("configurationName")
    namespace = meta.get("namespace")

    cfgname_arr = cfgname_with_namespace.split(".")
    cfgname=cfgname_arr[0]
    cfgname_namespace = namespace

    if (len(cfgname_arr)>1):
        cfgname = cfgname_arr[1]
        cfgname_namespace = cfgname_arr[0]

    print (status.get("create_fn"))
    if status.get("create_fn") is not None:
    
        serviceId = status.get("create_fn").get("serviceId")
        print (serviceId)

        status = {}
        cfg = {}

        try:
            #load RefcatorSpaceConfig object specified in the RefcatorSpaceService spec
            cfg = k8sUtils.get_flux_config(cfgname,cfgname_namespace)
            status["appId"]=cfg.get_appId()
            status["envId"]=cfg.get_envId()
            status["vpcId"]=cfg.get_vpcId()
        except errors.ObjectNotFound as e:
            status["state"]='ERROR'
            status["message"]=str(e)
            return status   #stop processing

        print("now deleting flux service")
        try:
            fluxutils.delete_flux_service(cfg.get_envId(),cfg.get_appId(),svcname)
            print("flux service deleted")
        except BaseException as e:
            status["state"]='ERROR'
            status["message"]=str(e)
            print (str(e))
            return status   #stop processing
            
        print("now delete_finalizer_binding ")
        try:
            k8sUtils.delete_finalizer_binding(cfgname,cfgname_namespace,namespace,svcname, serviceId)
            print("finalizer_binding deleted")
        except BaseException as e:
            status["state"]='ERROR'
            status["message"]=str(e)
            print (str(e))
            return status   #stop processing

@kopf.on.delete('refactorspaceconfig')
def on_delete_cfg(spec,meta, status, **kwargs):
    print ("on_delete_cfg")
    pass


@kopf.timer('refactorspaceconfig', interval=15.0)
def reconcile(spec,meta, status, **kwargs):
    #TODO
    print (meta.get("finalizers"))
    #print (status.get("create_fn").get("serviceId"))
    
    pass    



