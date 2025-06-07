from typing import Callable


def commitable(commitable_method: Callable):
    """This decorator provides opportunity to commit changes in db after calling DBSocket methods. Changes will be commited by default. If don't need commit changes set "commit=False" """

    async def commit(self, *args, **kwargs):
        commit = kwargs.pop('commit', True)
        res = await commitable_method(self, *args, **kwargs)
        if commit:
            await self.session.commit()
        return res
    return commit
