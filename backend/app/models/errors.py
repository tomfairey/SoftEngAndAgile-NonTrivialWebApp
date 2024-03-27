# Error 400 (operation was not possible how client requested it)
class BadRequest(Exception):
    pass

# Error 401 (not logged in but log-in required)
class Unauthorised(Exception):
    pass

# Error 403 (logged in but no permission for specified action)
class Forbidden(Exception):
    pass

# Error 404 (specified resource does not exist)
class NotFound(Exception):
    pass

# Error 405 (method not allowed e.g. PUT on GET only resource)
class MethodNotAllowed(Exception):
    pass

# Error 409 (conflict on resource, i.e. trying to insert something with a duplicate primary/unique key)
class Conflict(Exception):
    pass

# Error 423 (locked resource, i.e. trying to delete an item without confirming)
class Locked(Exception):
    pass

# Error 503 (generic unavailable server error)
class ServiceUnavailable(Exception):
    pass
