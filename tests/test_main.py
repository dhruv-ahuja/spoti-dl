import pytest

import spotidl.main as package


def test_cli():
    with pytest.raises(SystemExit):
        # raises system exit since no arguments are passed onto the app
        # which we'll test in the "test_cli" module
        package.cli()
