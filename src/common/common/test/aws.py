'''
Resources for testing in AWS.
'''
from collections import namedtuple
from typing import Any, Dict, List, Tuple, Union

import boto3

def create_lambda_function_context(function_name: str, object_name: str = 'LambdaContext') -> Tuple:
    '''Return a named tuple representing a context object'''
    context_info = {
        'aws_request_id': '00000000-0000-0000-0000-000000000000',
        'function_name': function_name,
        'invoked_function_arn': 'arn:aws:lambda:us-east-1:012345678910:function:{}'.format(function_name),
        'memory_limit_in_mb': 128
    }

    Context = namedtuple(object_name, context_info.keys())
    return Context(*context_info.values())


class CfnStackClient(object):
    '''client for working with a CFN stack'''

    def __init__(self, stack_name):
        '''init'''
        self.stack_name = stack_name

        self._cfn_client = boto3.client('cloudformation')
        self._stack = {}
        self.refresh()


    def refresh(self) -> None:
        '''Refresh stack info'''
        self._stack = self._cfn_client.describe_stack_resources(StackName=self.stack_name)


    def get_stack_resource_by_logical_id(self, logical_id: str) :
        '''Get a resource by it's logical ID'''
        resources = self._stack.get('StackResources', [])
        r = None

        for _r in resources:
            if _r.get('LogicalResourceId') == logical_id:
                r = _r.get('LogicalResourceId')
                break
        return r


    def get_stack_resource_by_physical_id(self, physical_id: str) -> Union[dict, None]:
        '''Get a resource by it's logical ID'''
        resources = self._stack.get('StackResources', [])
        r = None

        for _res in resources:
            if _res.get('PhysicalResourceId') == physical_id:
                r = _res.get('PhysicalResourceId', {})
                break

        return r


    def get_stack_resources_by_type(self, resource_type: str) -> List[Dict[str, Any]]:
        '''Get resources by resource type'''
        resources = self._stack.get('StackResources', [])
        r = []

        for _res in resources:
            if _res.get('ResourceType') == resource_type:
                r.append(_res.get('ResourceType'))

        return r

