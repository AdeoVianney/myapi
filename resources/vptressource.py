# Flask imports
from flask import g, url_for
import flask_restful as restful
from flask_restful import marshal

# Flaskit imports
from celery.result import AsyncResult
from celery.exceptions import TimeoutError
from consumer_vptressource import CONSUMER_APP
from pagination import get_paginated_list
from flaskit import app
from flaskit.utils import ErrorNotFound, ErrorDuplicate
from flaskit.resource import MetaResource, init_api, generate_swagger_from_schema
from celery.signals import after_task_publish

# Project imports

# Python imports
import sys
import copy
import json



#=========================
# VptressourceGet swagger fields
#=========================
@generate_swagger_from_schema(schemaRef="VptressourceGet", schemaPath="definitions/response/properties/results/items", type="Response")
class VptressourceGetResponseResourceFields:
    pass

@generate_swagger_from_schema(schemaRef="VptressourceGet", schemaPath="definitions/response", type="Response")
class VptressourceGetResponseFields:
    pass

@generate_swagger_from_schema(schemaRef="VptressourceStatus", schemaPath="definitions/response", type="Response")
class VptressourceStatusResponseFields:
    pass

@generate_swagger_from_schema(schemaRef="VptressourceCount", schemaPath="definitions/response", type="Response")
class VptressourceCountResponseFields:
    pass

@generate_swagger_from_schema(schemaRef="VptressourceFirstLast", schemaPath="definitions/response", type="Response")
class VptressourceFirstLastResponseFields:
    pass


#=========================
# VptressourcePost swagger fields
#=========================
@generate_swagger_from_schema(schemaRef="VptressourcePost", schemaPath="", type="Request")
class VptressourcePostRequestFields:
    pass

@generate_swagger_from_schema(schemaRef="VptressourcePost", schemaPath="definitions/response/properties/", type="Response")
class VptressourcePostResponseResourceFields:
    pass

@generate_swagger_from_schema(schemaRef="VptressourcePost", schemaPath="definitions/response", type="Response")
class VptressourcePostResponseFields:
    pass

#=========================
# VptressourceDelete swagger fields
#=========================
@generate_swagger_from_schema(schemaRef="VptressourceDelete", schemaPath="definitions/response/properties/vptressource", type="Response")
class VptressourceDeleteResponseResourceFields:
    pass

@generate_swagger_from_schema(schemaRef="VptressourceDelete", schemaPath="definitions/response", type="Response")
class VptressourceDeleteResponseFields:
    pass

##################################################################################################
# Vptressource resource for post verbs
##################################################################################################
class Vptressource(MetaResource):
    """Manage vptressource
    """

    ####################################################################################
    # Create a vptressource
    ####################################################################################
    @init_api("VptressourcePost")
    def post(self):
        """Create a vptressource

        TITLE:Sample
        <pre>
        CURL:"/vptressource" -d '{"description": "..."}'
        </pre>
        """

        self.initializeAPI()

        if g.dryrun:
            VptressourceRecord = {
                'id': 'this-is-my-id',
                'description': g.args["description"],
            }
            return VptressourceRecord, 200, {}

        kwargs = copy.deepcopy(g.args)
        kwargs.pop('range', None)
        kwargs.pop('async', None)
        async_result = CONSUMER_APP.send_task(
            'vptressource.post', kwargs=kwargs)

        if g.args['async']:
            headers = {
                'Location': url_for(
                    'vptressourceStatusById',
                    id=async_result.id,
                    _external=True),
                'Content-Location': url_for(
                    'vptressourceById',
                    id=async_result.id,
                    _external=True),
            }

            return {}, 202, headers
        else:
            resp = async_result.get()
            if not isinstance(resp['results'], list):
                resp['results'] = [resp['results']]
            return get_paginated_list(
                resp['results'], async_result.id,
                g.args['range'], 'vptressourceById')


############################
# Qualified Vptressource
############################
class VptressourceById(MetaResource):
    """Manage qualified Vptressource
    """
    ####################################################################################
    # Get a vptressource
    ####################################################################################
    @init_api("VptressourceGet")
    def get(self, id):
        """Get vptressource

        Get vptressource informations

        TITLE:Sample
        <pre>
        CURL:"/vptressource/<id>"
        </pre>
        """

        # verify request
        self.initializeAPI(data = { "id": id })

        if g.dryrun:
            VptressourceRecord = {
                'id': 'this-is-my-id',
                'description': g.args["description"],
            }
            return VptressourceRecord, 200

        kwargs = copy.deepcopy(g.args)
        async_result = AsyncResult(id, app=CONSUMER_APP)

        # Check if we are getting a resource or a task result. (A resource being
        # a task.get result)
        if async_result.state == 'SUCCESS':
            resp = async_result.get()
            if not resp.get('success', False):
                return resp.get('error_msg', 'Task failed'), 200
            if not resp.get('results', False):
                resp['results'] = []
            if not isinstance(resp['results'], list):
                resp['results'] = [resp['results']]
            return get_paginated_list(
                resp['results'], async_result.id,
                g.args['range'], 'vptressourceById')

        return {}, 404


    ####################################################################################
    # Delete a vptressource
    ####################################################################################
    @init_api("VptressourceDelete")
    def delete(self, id):
        """Delete a task result

        TITLE:Sample
        <pre>
        CURL:"/vptressource/<id>"
        </pre>
        """

        # verify request
        self.initializeAPI(data = { "id": id })
        task = AsyncResult(id, app=CONSUMER_APP)
        if task.state != 'SUCCESS':
            return 'Task result not found', 404
        task.forget()
        return '', 204




class VptressourceStatusById(MetaResource):
    """Get Vptressource status
    """
    ###############################
    # Get a vptressource status
    ###############################
    @init_api("VptressourceStatus")
    def get(self, id):
        """Get a vptressource status

        TITLE:Sample
        <pre>
        CURL:"/vptressource/<id>/status"
        </pre>
        """
        self.initializeAPI(data = { "id": id })

        async_res = AsyncResult(id, app=CONSUMER_APP)
        return {'state': async_res.state}, 200


class VptressourceFirstById(MetaResource):
    """Get Vptressource first element
    """
    @init_api("VptressourceFirstLast")
    def get(self, id):
        """Get the first element of a vptressource

        TITLE:Sample
        <pre>
        CURL:"/vptressource/<id>/first"
        </pre>
        """
        # verify request
        self.initializeAPI(data = { "id": id })

        if g.dryrun:
            VptressourceRecord = {
                'id': 'this-is-my-id',
                'description': g.args["description"],
            }
            return VptressourceRecord, 200

        async_result = AsyncResult(id, app=CONSUMER_APP)

        # Check if we are getting a resource or a task result. (A resource being
        # a task.get result)
        if async_result.state == 'SUCCESS':
            resp = async_result.get()
            if not resp.get('success', False):
                return resp.get('error_msg', 'Task failed'), 200
            if not resp.get('results', False):
                resp['results'] = []
            if isinstance(resp['results'], list):
                resp['results'] = resp['results'][0]
            else:
                resp['results'] = [resp['results']]
            return get_paginated_list(
                resp['results'], async_result.id,
                g.args['range'], 'vptressourceFirstById')

        return {}, 404


class VptressourceLastById(MetaResource):
    """Get Vptressource last element
    """
    ###############################
    # Get a vptressource status
    ###############################
    @init_api("VptressourceFirstLast")
    def get(self, id):
        """Get the last element of a vptressource

        TITLE:Sample
        <pre>
        CURL:"/vptressource/<id>/last"
        </pre>
        """
        # verify request
        self.initializeAPI(data = { "id": id })

        if g.dryrun:
            VptressourceRecord = {
                'id': 'this-is-my-id',
                'description': g.args["description"],
            }
            return VptressourceRecord, 200

        async_result = AsyncResult(id, app=CONSUMER_APP)

        # Check if we are getting a resource or a task result. (A resource being
        # a task.get result)
        if async_result.state == 'SUCCESS':
            resp = async_result.get()
            if not resp.get('success', False):
                return resp.get('error_msg', 'Task failed'), 200
            if not resp.get('results', False):
                resp['results'] = []
            if isinstance(resp['results'], list):
                resp['results'] = resp['results'][-1]
            else:
                resp['results'] = [resp['results']]
            return get_paginated_list(
                resp['results'], async_result.id,
                g.args['range'], 'vptressourceLastById')

        return {}, 404


class VptressourceCountById(MetaResource):
    """Get Vptressource count
    """
    ###############################
    # Get a vptressource status
    ###############################
    @init_api("VptressourceCount")
    def get(self, id):
        """Get the last element of a vptressource

        TITLE:Sample
        <pre>
        CURL:"/vptressource/<id>/count"
        </pre>
        """
        # verify request
        # verify request
        self.initializeAPI(data = { "id": id })

        if g.dryrun:
            VptressourceRecord = {
                'id': 'this-is-my-id',
                'description': g.args["description"],
            }
            return VptressourceRecord, 200

        # Check if we are getting a resource or a task result. (A resource being
        # a task.get result)
        if async_result.state == 'SUCCESS':
            resp = async_result.get()
            if not resp.get('success', False):
                return resp.get('error_msg', 'Task failed'), 200
            if not resp.get('results', False):
                resp['results'] = []
            if not isinstance(resp['results'], list):
                resp['results'] = [resp['results']]
            return {'count': len(resp['results'])}, 200

        return {}, 404