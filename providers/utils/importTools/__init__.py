import importlib.util
import sys
from pathlib import Path


def easy_import(module_name: str):
    utils_dir = Path(sys.modules[__name__].__file__).parent
    project_root = utils_dir.parent
    module_path = project_root.joinpath(*module_name.split("."))

    potential_file_path = module_path.with_suffix(".py")

    if potential_file_path.is_file():
        module_name_for_import = module_name
        try:
            imported_module = __import__(
                module_name_for_import, fromlist=[module_name.split(".")[-1]]
            )
            return imported_module
        except ImportError as e:
            spec = importlib.util.spec_from_file_location(
                module_name_for_import, str(potential_file_path)
            )
            if spec is None:
                raise ImportError(
                    f"Could not import module '{module_name_for_import}' from '{potential_file_path}'. Original error: {e}"
                )
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name_for_import] = module
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            raise ImportError(f"Error during import of '{module_name_for_import}': {e}")
    else:
        raise ImportError(
            f"No module named '{module_name}' found relative to the project root."
        )
