from fastapi.responses import JSONResponse

from ..models.errors import BadRequest, Conflict, Forbidden, Locked, MethodNotAllowed, NotFound, ServiceUnavailable, Unauthorised

def exceptionToHTTPResponse(exception: Exception):
    if isinstance(exception, BadRequest):
        return JSONResponse(content={"message": str(exception)}, status_code = 400)
    elif isinstance(exception, Unauthorised):
        return JSONResponse(content={"message": str(exception)}, status_code = 401)
    elif isinstance(exception, Forbidden):
        return JSONResponse(content={"message": str(exception)}, status_code = 403)
    elif isinstance(exception, NotFound):
        return JSONResponse(content={"message": str(exception)}, status_code = 404)
    elif isinstance(exception, MethodNotAllowed):
        return JSONResponse(content={"message": str(exception)}, status_code = 405)
    elif isinstance(exception, Conflict):
        return JSONResponse(content={"message": str(exception)}, status_code = 409)
    elif isinstance(exception, Locked):
        return JSONResponse(content={"message": str(exception)}, status_code = 423)
    elif isinstance(exception, ServiceUnavailable):
        return JSONResponse(status_code = 503)
    else:
        return JSONResponse(content={"message": "Oops! An unknown error occured..."}, status_code = 500)
