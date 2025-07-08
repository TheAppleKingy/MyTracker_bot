def parse_integrity_err_msg(msg: str):
    detail = msg.split('\n')[1].split(maxsplit=1)[1]
    return detail


class BaseCustomException(Exception):
    _layer_class_name: str
    layer_instance_class_name: str

    def __init__(self, msg: str, e: Exception = None):
        detail = {self._layer_class_name: self.layer_instance_class_name}
        if e:
            detail.update({'internal exception class': e.__class__.__name__})
        detail.update({'msgs': msg.split('\n')})
        self.detail = detail
