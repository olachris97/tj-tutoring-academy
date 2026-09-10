def paginated_response(pagination, item_to_dict):
    return {
        "items": [item_to_dict(item) for item in pagination.items],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }
