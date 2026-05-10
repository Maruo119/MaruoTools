import argostranslate.package
import argostranslate.translate

# モデルの更新とダウンロード（初回のみ）
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(lambda x: x.from_code == "ja" and x.to_code == "en", available_packages)
)
argostranslate.package.install_from_path(package_to_install.download())