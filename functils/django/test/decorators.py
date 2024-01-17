from django.db import transaction

__all__ = ["cases", "data"]


def cases(cases):
    def test_decorator(subTestFn):
        def repl(self, *args):
            for case_name, case_kwargs in cases.items():
                case_data = []
                expected_exception = None
                expected_message = None

                if type(case_kwargs) is list:
                    case_data = case_kwargs
                elif type(case_kwargs) is dict:
                    case_data = case_kwargs["data"]
                    expected_exception = case_kwargs.get("expected_exception")
                    expected_message = case_kwargs.get("expected_message")

                with transaction.atomic(), self.subTest(case=case_name):
                    if expected_exception is None:
                        subTestFn(self, case_data, *args)
                    elif expected_exception is not None and expected_message is None:
                        with self.assertRaises(expected_exception):
                            subTestFn(self, case_data, *args)
                    else:
                        with self.assertRaisesMessage(
                            expected_exception, expected_message
                        ):
                            subTestFn(self, case_data, *args)

        return repl

    return test_decorator


def data(data_fn_name):
    def wrapper(func):
        def repl(self, *args):
            data_fn = getattr(self, data_fn_name)
            data_fn()
            func(self, *args)

        return repl

    return wrapper
