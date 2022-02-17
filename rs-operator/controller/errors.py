class ObjectNotFound(Exception):    
    def __init__(self, objectName, namespace):
        self.objectName = objectName
        self.namespace = namespace
        super().__init__(f'{self.objectName} not found in the namesopace: -> {self.namespace}')

    def __str__(self):
        return f'{self.objectName} not found in the namesopace: -> {self.namespace}'


class InvalidSpecError(Exception):    
    def __init__(self, msg):
        self.msg = msg
        super().__init__(msg)

    def __str__(self):
        return self.msg
