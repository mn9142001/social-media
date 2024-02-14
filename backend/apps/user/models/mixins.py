from django.core.cache import cache


class TokenMixin:
    is_from_token : bool
    last_update : int
    pk : int

    def generate_field_cache_key(self, key):
        return f"user-{self.pk}-{key}"
    
    def get_cached_field(self, key):
        cache_key = self.generate_field_cache_key(key)
        cache_data = cache.get(cache_key, None)

        if cache_data:
            return cache_data

        self.update_cache_field(key)

        return getattr(self, key)

    def update_cache_field(self, key, refresh_from_db=True):
        cache_key = self.generate_field_cache_key(key)

        if self.is_from_token and refresh_from_db:
            self.refresh_from_db(fields=[key])

        cache.set(
            cache_key, getattr(self, key), timeout=24*60*60
        )
        
