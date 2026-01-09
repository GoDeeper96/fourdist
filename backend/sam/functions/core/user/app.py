# functions/core/company/app.py
import json
import logging
from service.UserService import UserService
from type.routerUser import RoutePath as Path

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize service once (outside handler for reuse across invocations)
service = UserService()

def lambda_handler(event, context):
    """
    Lambda handler for Company operations
    """
    logger.info(f"Processing event: {event.get('httpMethod')} {event.get('requestContext', {}).get('resourcePath', '')}")
    
    # Default response
    response_data = {"message": "Path not found"}
    status_code = 404
    
    # CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*", 
        "Access-Control-Allow-Methods": "*",
        "Content-Type": "application/json"
    }
    
    try:
        method = event['httpMethod']
        path = event['requestContext']['resourcePath']
        
        # Parse request body safely
        body = {}
        if event.get('body'):
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in request body: {e}")
                return build_response(400, {"error": "Invalid JSON in request body"}, headers)
        
        # Route requests
        status_code, response_data = route_request(method, path, body, event.get('pathParameters', {}), event, event.get('headers', {}))
        
    except KeyError as e:
        logger.error(f"Missing required parameter: {e}")
        status_code = 400
        response_data = {"error": f"Missing required parameter: {str(e)}"}
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        status_code = 500
        response_data = {"error": "Internal server error"}
    
    return build_response(status_code, response_data, headers)


def route_request(method, path, body, path_params, event, headers):
    """
    Route requests to appropriate service methods
    """
    try:
        # Create company
        if method == 'GET' and Path.GET_HEALTH.match(path):
            return service.get_health(body)
            
        # Get company by ID
        # elif method == 'GET' and Path.GET_COMPANY.match(path):
        #     company_id = path_params.get('companyId')
        #     if not company_id:
        #         return 400, {"error": "companyId is required"}
        #     return service.get_company(company_id)

            
        else:
            logger.warning(f"No route found for {method} {path}")
            return 404, {"error": "Path not found", "path": path, "method": method}
            
    except Exception as e:
        logger.error(f"Error in route_request: {e}")
        return 500, {"error": f"Service error: {str(e)}"}


def build_response(status_code, data, headers):
    """
    Build standardized API response
    """
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(data, default=json_serializer, ensure_ascii=False)
    }


def json_serializer(obj):
    """
    JSON serializer for objects not serializable by default
    """
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")