from fastapi import HTTPException, status


class NotFoundError(HTTPException):

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictError(HTTPException):

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class BusinessRuleError(HTTPException):

    def __init__(self, detail: str = "Business rule violation"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
