import pytest
from typer.testing import CliRunner
from pyjs_code_runner.cli.main import app

import textwrap


def write_main(to_mount_dir, script):
    script = textwrap.dedent(script)
    with open(to_mount_dir / "main.py", "w") as f:
        f.write(script)


class TestCli(object):
    def test_help(self, runner):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    def test_sync_err(
        self, env_prefix, em_work_dir, backend_cli_settings, tmpdir, runner
    ):
        backend_type, backend_args = backend_cli_settings

        to_mount_dir = tmpdir
        cli_mount = f"{str(tmpdir)}:{str(em_work_dir)}"

        write_main(to_mount_dir, "raise RuntimeError('sorry')")

        # fmt: off
        cli_args = [
            "run",
            "script",
            backend_type,
            "--conda-env",  env_prefix,
            "--mount",      cli_mount,
            "--script",     "main.py",
            "--work-dir",   em_work_dir,
            "--no-async-main"
        ] + backend_args
        # fmt: on

        result = runner.invoke(app, cli_args)
        assert result.exit_code == 1

    def test_async_error(
        self,
        env_prefix,
        em_work_dir,
        backend_cli_settings,
        tmpdir,
        runner,
    ):
        to_mount_dir = tmpdir
        cli_mount = f"{str(tmpdir)}:{str(em_work_dir)}"

        backend_type, backend_args = backend_cli_settings

        main_content = """\n
            import asyncio
            async def main():
                await asyncio.sleep(1)
                raise RuntimeError("fubar")
                return 0
        """
        write_main(to_mount_dir, main_content)

        # fmt: off
        cli_args = [
            "run",
            "script",
            backend_type,
            "--conda-env",  env_prefix,
            "--mount",      cli_mount,
            "--script",     "main.py",
            "--work-dir",   em_work_dir,
            "--async-main"
        ] + backend_args
        # fmt: on

        result = runner.invoke(app, cli_args)
        assert result.exit_code == 1

    def test_sync_hello_world(
        self, env_prefix, em_work_dir, backend_cli_settings, tmpdir, runner
    ):
        to_mount_dir = tmpdir
        cli_mount = f"{str(tmpdir)}:{str(em_work_dir)}"
        backend_type, backend_args = backend_cli_settings

        write_main(to_mount_dir, "print('hello world')")

        # fmt: off
        cli_args = [
            "run",
            "script",
            backend_type,
            "--conda-env",  env_prefix,
            "--mount",      cli_mount,
            "--script",     "main.py",
            "--work-dir",   em_work_dir,
            "--no-async-main"
        ] + backend_args
        # fmt: on

        result = runner.invoke(app, cli_args, catch_exceptions=False)
        assert result.exit_code == 0
        assert "hello world" in result.stdout

    @pytest.mark.parametrize("with_return", [False, True])
    def test_async_hello_world(
        self,
        env_prefix,
        em_work_dir,
        backend_cli_settings,
        with_return,
        tmpdir,
        runner,
    ):
        to_mount_dir = tmpdir
        cli_mount = f"{str(tmpdir)}:{str(em_work_dir)}"
        backend_type, backend_args = backend_cli_settings

        if with_return:
            main_content = """\n
                import asyncio
                async def main():
                    await asyncio.sleep(1)
                    print('hello world')
                    return 0
            """
        else:
            main_content = """\n
                import asyncio
                async def main():
                    await asyncio.sleep(1)
                    print('hello world')
            """
        write_main(to_mount_dir, main_content)

        # fmt: off
        cli_args = [
            "run",
            "script",
            backend_type,
            "--conda-env",  env_prefix,
            "--mount",      cli_mount,
            "--script",     "main.py",
            "--work-dir",   em_work_dir,
            "--async-main"
        ] + backend_args
        # fmt: on

        result = runner.invoke(app, cli_args, catch_exceptions=False)
        assert result.exit_code == 0
        assert "hello world" in result.stdout
