bldit_version = "0.1.3"
package_name = "caelestia-cli"
package_version = "1.0.0"
global_dependencies = {}
dependencies = {}

targets = {
    default = {
        build = function()
            os.execute("rm -rf dist")
            os.execute("python -m build --wheel")
            return 0
        end,
        install = function()
            os.execute("sudo python -m installer --overwrite-existing dist/*.whl")
            os.execute("sudo mkdir -p /usr/share/fish/vendor_completions.d")
            os.execute("sudo cp completions/caelestia.fish /usr/share/fish/vendor_completions.d/caelestia.fish")
            return 0
        end,
        uninstall = function()
            os.execute("sudo rm -f /usr/local/bin/caelestia /usr/bin/caelestia")
            os.execute("sudo rm -f /usr/share/fish/vendor_completions.d/caelestia.fish")
            -- We just delete the binary and completion. Removing the python package completely 
            -- via installer is tricky, but usually binary deletion is enough.
            return 0
        end
    },
    quiet = {
        build = function()
            os.execute("rm -rf dist >/dev/null 2>&1")
            os.execute("python -m build --wheel >/dev/null 2>&1")
            return 0
        end,
        install = function()
            os.execute("sudo python -m installer --overwrite-existing dist/*.whl >/dev/null 2>&1")
            os.execute("sudo mkdir -p /usr/share/fish/vendor_completions.d")
            os.execute("sudo cp completions/caelestia.fish /usr/share/fish/vendor_completions.d/caelestia.fish >/dev/null 2>&1")
            return 0
        end,
        uninstall = function()
            os.execute("sudo rm -f /usr/local/bin/caelestia /usr/bin/caelestia >/dev/null 2>&1")
            os.execute("sudo rm -f /usr/share/fish/vendor_completions.d/caelestia.fish >/dev/null 2>&1")
            return 0
        end
    }
}
