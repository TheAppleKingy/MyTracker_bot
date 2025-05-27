from security import hash_password


def commitable(commitable_method):
    async def commit(self, *args, **kwargs):
        commit = kwargs.pop('commit', False)
        res = await commitable_method(self, *args, **kwargs)
        if commit:
            await self.session.commit()
        return res
    return commit


def hashable(fields: list[str]):
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            for field_name in fields:
                if field_name in kwargs:
                    hashed = hash_password(kwargs[field_name])
                    kwargs[field_name] = hashed
            return await func(self, *args, **kwargs)
        return wrapper
    return decorator
