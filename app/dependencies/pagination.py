

from fastapi import Query


class PaginationParams:
    def __init__(
            self, 
            page: int = Query(default=1, ge=1, description="页码"), 
            size: int = Query(20, ge=1, le=100, description="每页大小")
    ):
        self.page = page
        self.size = size
    @property
    def offset(self):
        return (self.page - 1) * self.size


