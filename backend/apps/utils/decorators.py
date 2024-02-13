def get_queryset_wrapper(func):
    """Decorator used to avoid docs anonymous user error in get_queryset"""
    
    def wrapper(self):
        if self.request.path == '/docs/':
            return self.queryset
        return func(self)
    return wrapper
    