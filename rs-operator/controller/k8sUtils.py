import kubernetes.client
import objects
import errors
from kubernetes.client.rest import ApiException


def get_flux_config(cfgname, namespace):

    try:
        api_client = kubernetes.client.ApiClient()
        api_instance = kubernetes.client.CustomObjectsApi(api_client)
        api_response = api_instance.get_namespaced_custom_object("eks.amazonaws.com", "v1", namespace,
                                                                    "refactorspaceconfigs", cfgname)
        obj = objects.FluxConfig(api_response)
        return obj
    except Exception as e:
        raise errors.ObjectNotFound(cfgname,namespace)

def add_finalizer_to_config(cfgname,cfgname_namespace,namespace,svcname, serviceId):
    #try:

        print("inside add_finalizer_to_config")
        print("cfgname:"+cfgname)
        print("cfgname_namespace:"+cfgname_namespace)
        print("namespace:"+namespace)
        print("svcname:"+svcname)
        print("serviceId:"+serviceId)

        api_client = kubernetes.client.ApiClient()
        api_instance = kubernetes.client.CustomObjectsApi(api_client)
        print("ok1")
        api_response = api_instance.get_namespaced_custom_object("eks.amazonaws.com", "v1", cfgname_namespace,
                                                                    "refactorspaceconfigs", cfgname)
        print("ok2")
        entryList = []
        try:
            entryList = api_response["metadata"]["finalizers"]
        except:
            # do nothing
            pass    

        entryList.append(serviceId+'.'+namespace +"."+svcname)
        print("ok3")
        service_patch = {
                    'metadata': 
                            {'finalizers': entryList}
                        }

        api_response = api_instance.patch_namespaced_custom_object("eks.amazonaws.com", "v1", cfgname_namespace,
                                                                    "refactorspaceconfigs", cfgname, 
                                                                     service_patch)
        print("ok4")
        return api_response
    #except Exception as e:
    #    raise errors.ObjectNotFound(cfgname,namespace)


def delete_finalizer_binding(cfgname,cfgname_namespace, namespace,svcname, serviceId):
        api_client = kubernetes.client.ApiClient()
        api_instance = kubernetes.client.CustomObjectsApi(api_client)

        api_response = api_instance.get_namespaced_custom_object("eks.amazonaws.com", "v1", cfgname_namespace,
                                                                    "refactorspaceconfigs", cfgname)
        entryList = api_response["metadata"]["finalizers"]
        print(entryList)

        s = serviceId+'.'+namespace +"."+svcname
        matchList = [x for x in entryList if s in x]
        resultSet = set(entryList)-set(matchList)
        
        print(resultSet)

        service_patch = {
                    'metadata': 
                            {'finalizers': list(resultSet)}
                        }

        

        api_response = api_instance.patch_namespaced_custom_object("eks.amazonaws.com", "v1", cfgname_namespace,
                                                                    "refactorspaceconfigs", cfgname, 
                                                                     service_patch)
        print(api_response)

        return api_response

def get_service(label_selector, namespace):
    try:
        api_client = kubernetes.client.ApiClient()
        api_instance = kubernetes.client.CoreV1Api(api_client)
        k8s_v1b1 = kubernetes.client.ExtensionsV1beta1Api(api_client)
        api_response_svc = api_instance.list_namespaced_service(namespace, label_selector=label_selector)
        
        if len(api_response_svc.items)>1 :
            return api_response_svc
        else:
            api_response_ingress = k8s_v1b1.list_namespaced_ingress(namespace, label_selector=label_selector)
            return api_response_ingress
    except ApiException as e:
        raise e

def getk8sServiceEndPoint(namespace,svcSelector,protocol):
    url = ""
    label_selector =""
    for key in svcSelector.keys():
        label_selector = key+"="+svcSelector[key]
    
    api_client = kubernetes.client.ApiClient()
    api_instance = kubernetes.client.CoreV1Api(api_client)
    k8s_v1b1 = kubernetes.client.ExtensionsV1beta1Api(api_client)
    
    res = api_instance.list_namespaced_service(namespace, label_selector=label_selector)

    if len(res.items)>=1 : # it is a service
        if len(res.items)>1:
            raise errors.InvalidSpecError(f"label_selector: {label_selector} returned multiple service match in {namespace} namespace. Must match with exactly one service.")
        
        if res.items[0].spec.type == 'ClusterIP' :
            raise errors.InvalidSpecError(f"label_selector: {label_selector} matches to service {serviceName} in {namespace} namespace which is of type ClusterIP. Cannot connect this service from Refactor Space Proxy")

        serviceName = res.items[0].metadata.name
        if res.items[0].spec.type == 'LoadBalancer' :
            url = protocol+"://"+res.items[0].status.load_balancer.ingress[0].hostname
        if res.items[0].spec.type == 'NodePort' :
            url = protocol+"://" + k8sUtils.getNodeIP()+ ":"+str(res.items[0].spec.ports[0].node_port)
    else: # it may be a ingress
        api_response_ingress = k8s_v1b1.list_namespaced_ingress(namespace, label_selector=label_selector)
        print (">>>>>>>>>>>>.")
        print(api_response_ingress.items)
        print (">>>>>>>>>>>>>")
        if len(api_response_ingress.items)>1:
            print("len(api_response_ingress.items)>1")
            raise errors.InvalidSpecError(f"label_selector: {label_selector} returned multiple ingress match in {namespace} namespace. Must match with exactly one ingress.")
        elif len(api_response_ingress.items)==0:
            print("len(api_response_ingress.items)==0")
            raise errors.InvalidSpecError(f"label_selector: {label_selector} does not match any service/ingress in {namespace} namespace")

        serviceName = api_response_ingress.items[0].metadata.name
        url = protocol+"://"+api_response_ingress.items[0].status.load_balancer.ingress[0].hostname    

    print ("-------->"+url)

    return {'serviceName': serviceName, 'url': url }


def getNodeIP():
    try:
        api_client = kubernetes.client.ApiClient()
        api_instance = kubernetes.client.CoreV1Api(api_client)
        v1nodeList = api_instance.list_node()

        #print(v1nodeList.items[0].status.addresses)

        internalIP = [x.address for x in v1nodeList.items[0].status.addresses if x.type == 'InternalIP'][0]

        #print (internalIP)

        return internalIP

    except ApiException as e:
        raise e
