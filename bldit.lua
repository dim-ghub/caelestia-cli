bldit_version = "0.1.3"
package_name = "caelestia-cli"
package_version = "1.0.0"
global_dependencies = {}
dependencies = {}

targets = {
    default = {
        pre_build = function()
            if os.execute("command -v pacman >/dev/null 2>&1") == 0 then
                if os.execute("pacman -Qq caelestia-cli >/dev/null 2>&1") == 0 or os.execute("pacman -Qq caelestia-cli-git >/dev/null 2>&1") == 0 then
                    os.execute("sudo pacman -Rdd --noconfirm caelestia-cli caelestia-cli-git >/dev/null 2>&1")
                end
            end
            return 0
        end,
        build = function()
            os.execute("rm -rf dist")
            os.execute("python -m build --wheel")
            return 0
        end,
        install = function()
            local pfx = prefix or "/usr/local"
            os.execute("python -m installer --overwrite-existing --prefix " .. pfx .. " dist/*.whl")
            os.execute("mkdir -p " .. pfx .. "/share/fish/vendor_completions.d")
            os.execute("cp completions/caelestia.fish " .. pfx .. "/share/fish/vendor_completions.d/caelestia.fish")
            return 0
        end,
        uninstall = function()
            local pfx = prefix or "/usr/local"
            os.execute("rm -f " .. pfx .. "/bin/caelestia")
            os.execute("rm -f " .. pfx .. "/share/fish/vendor_completions.d/caelestia.fish")
            return 0
        end
    },
    quiet = {
        pre_build = function()
            if os.execute("command -v pacman >/dev/null 2>&1") == 0 then
                if os.execute("pacman -Qq caelestia-cli >/dev/null 2>&1") == 0 or os.execute("pacman -Qq caelestia-cli-git >/dev/null 2>&1") == 0 then
                    os.execute("sudo pacman -Rdd --noconfirm caelestia-cli caelestia-cli-git >/dev/null 2>&1")
                end
            end
            return 0
        end,
        build = function()
            os.execute("rm -rf dist >/dev/null 2>&1")
            os.execute("python -m build --wheel >/dev/null 2>&1")
            return 0
        end,
        install = function()
            local pfx = prefix or "/usr/local"
            os.execute("python -m installer --overwrite-existing --prefix " .. pfx .. " dist/*.whl >/dev/null 2>&1")
            os.execute("mkdir -p " .. pfx .. "/share/fish/vendor_completions.d")
            os.execute("cp completions/caelestia.fish " .. pfx .. "/share/fish/vendor_completions.d/caelestia.fish >/dev/null 2>&1")
            return 0
        end,
        uninstall = function()
            local pfx = prefix or "/usr/local"
            os.execute("rm -f " .. pfx .. "/bin/caelestia >/dev/null 2>&1")
            os.execute("rm -f " .. pfx .. "/share/fish/vendor_completions.d/caelestia.fish >/dev/null 2>&1")
            return 0
        end
    }
}
