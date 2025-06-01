from typing import Callable


def commitable(commitable_method: Callable):
    """This decorator provides opportunity to commit changes in db after calling DBSocket methods"""

    async def commit(self, *args, **kwargs):
        commit = kwargs.pop('commit', False)
        res = await commitable_method(self, *args, **kwargs)
        print(commit)
        if commit:
            await self.session.commit()
        return res
    return commit
