from argg_hdl.ast.ast_classes.ast_base import v_ast_base
class v_noop(v_ast_base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):

        return ""


