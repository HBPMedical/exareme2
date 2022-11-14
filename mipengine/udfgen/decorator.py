import ast
from typing import List

from mipengine.udfgen.ast import Signature
from mipengine.udfgen.ast import breakup_function
from mipengine.udfgen.helpers import get_func_body_from_ast
from mipengine.udfgen.helpers import get_func_parameter_names
from mipengine.udfgen.helpers import get_items_of_type
from mipengine.udfgen.helpers import parse_func
from mipengine.udfgen.iotypes import InputType
from mipengine.udfgen.iotypes import LoopbackOutputType
from mipengine.udfgen.iotypes import OutputType
from mipengine.udfgen.iotypes import RelationType
from mipengine.udfgen.iotypes import TensorType
from mipengine.udfgen.iotypes import UDFLoggerType


class UDFDecorator:
    registry = {}

    def __call__(self, **kwargs):
        def decorator(func):
            parameter_names = get_func_parameter_names(func)
            validate_decorator_parameter_names(parameter_names, kwargs)
            signature = make_udf_signature(parameter_names, kwargs)
            validate_udf_signature_types(signature)
            validate_udf_return_statement(func)
            funcparts = breakup_function(func, signature)
            validate_udf_table_input_types(funcparts.table_input_types)
            funcname = funcparts.qualname
            self.registry[funcname] = funcparts
            return func

        return decorator


# Singleton pattern
udf = UDFDecorator()
del UDFDecorator


def validate_decorator_parameter_names(parameter_names, decorator_kwargs):
    """
    Validates:
     1) that decorator parameter names and func kwargs names match.
     2) that "return_type" exists as a decorator parameter.
     3) the udf_logger
    """
    validate_udf_logger(parameter_names, decorator_kwargs)

    if "return_type" not in decorator_kwargs:
        raise UDFBadDefinition("No return_type defined.")
    parameter_names = set(parameter_names)
    decorator_parameter_names = set(decorator_kwargs.keys())
    decorator_parameter_names.remove("return_type")  # not a parameter
    if parameter_names == decorator_parameter_names:
        return

    parameters_not_provided = decorator_parameter_names - parameter_names
    if parameters_not_provided:
        raise UDFBadDefinition(
            f"The parameters: {','.join(parameters_not_provided)} were not provided in the func definition."
        )

    parameters_not_defined_in_dec = parameter_names - decorator_parameter_names
    if parameters_not_defined_in_dec:
        raise UDFBadDefinition(
            f"The parameters: {','.join(parameters_not_defined_in_dec)} were not defined in the decorator."
        )


def validate_udf_logger(parameter_names, decorator_kwargs):
    """
    udf_logger is a special case of a parameter.
    It won't be provided by the user but from the udfgenerator.
    1) Only one input of this type can exist.
    2) It must be the final parameter, so it won't create problems with the positional arguments.
    """
    udf_logger_param_name = None
    for param_name, param_type in decorator_kwargs.items():
        if isinstance(param_type, UDFLoggerType):
            if udf_logger_param_name:
                raise UDFBadDefinition("Only one 'udf_logger' parameter can exist.")
            udf_logger_param_name = param_name

    if not udf_logger_param_name:
        return

    all_parameter_names_but_the_last = parameter_names[:-1]
    if udf_logger_param_name in all_parameter_names_but_the_last:
        raise UDFBadDefinition("'udf_logger' must be the last input parameter.")


def make_udf_signature(parameter_names, decorator_kwargs):
    parameters = {name: decorator_kwargs[name] for name in parameter_names}
    if isinstance(decorator_kwargs["return_type"], List):
        main_return_annotation = decorator_kwargs["return_type"][0]
        sec_return_annotations = decorator_kwargs["return_type"][1:]
    else:
        main_return_annotation = decorator_kwargs["return_type"]
        sec_return_annotations = []
    signature = Signature(
        parameters=parameters,
        main_return_annotation=main_return_annotation,
        sec_return_annotations=sec_return_annotations,
    )
    return signature


def validate_udf_signature_types(funcsig: Signature):
    """Validates that all types used in the udf's type signature, both input
    and output, are subclasses of InputType or OutputType."""
    parameter_types = funcsig.parameters.values()
    if any(not isinstance(input_type, InputType) for input_type in parameter_types):
        raise UDFBadDefinition(
            f"Input types of func are not subclasses of InputType: {parameter_types}."
        )

    main_return = funcsig.main_return_annotation
    if not isinstance(main_return, OutputType):
        raise UDFBadDefinition(
            f"Output type of func is not subclass of OutputType: {main_return}."
        )

    sec_returns = funcsig.sec_return_annotations
    if any(
        not isinstance(output_type, LoopbackOutputType) for output_type in sec_returns
    ):
        raise UDFBadDefinition(
            f"The secondary output types of func are not subclasses of LoopbackOutputType: {sec_returns}."
        )


def validate_udf_return_statement(func):
    """Validates two things concerning the return statement of a udf.
    1) that there is one and
    2) that it is of the simple `return foo, bar` form, as no
    expressions are allowed in udf return statements."""
    tree = parse_func(func)
    statements = get_func_body_from_ast(tree)
    try:
        ret_stmt = next(s for s in statements if isinstance(s, ast.Return))
    except StopIteration as stop_iter:
        raise UDFBadDefinition(f"Return statement not found in {func}.") from stop_iter
    if not isinstance(ret_stmt.value, ast.Name) and not isinstance(
        ret_stmt.value, ast.Tuple
    ):
        raise UDFBadDefinition(
            f"Expression in return statement in {func}."
            "Assign expression to variable/s and return it/them."
        )


def validate_udf_table_input_types(table_input_types):
    tensors = get_items_of_type(TensorType, table_input_types)
    relations = get_items_of_type(RelationType, table_input_types)
    if tensors and relations:
        raise UDFBadDefinition("Cannot pass both tensors and relations to udf.")


class UDFBadDefinition(Exception):
    """Raised when an error is detected in the definition of a udf decorated
    function. These checks are made as soon as the function is defined."""
