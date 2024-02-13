from django.core.cache import cache


class TokenMixin:
    def get_cached_random_id(self):

        cache_data = cache.get(self.pk, None)

        if cache_data:
            return cache_data

        self.update_cache_random_id()

        return self.random_id

    def update_cache_random_id(self):
        if self.is_from_token:
            self.refresh_from_db(fields=['random_id'])

        cache.set(
            self.pk, self.random_id, timeout=24*60*60
        )
        
