import argostranslate.translate
import argostranslate.package
import shutil
from pathlib import Path
import socket
import time

def check_models_installed():
    """Check if required translation models are installed."""
    try:
        installed_packages = argostranslate.package.get_installed_packages()
        has_ja_en = any(pkg.from_code == "ja" and pkg.to_code == "en" for pkg in installed_packages)
        has_en_ja = any(pkg.from_code == "en" and pkg.to_code == "ja" for pkg in installed_packages)
        return has_ja_en and has_en_ja
    except Exception as e:
        raise RuntimeError(f"Failed to check models: {e}")

def reset_models():
    """Clear model cache to reset to uninstalled state."""
    try:
        installed_packages = argostranslate.package.get_installed_packages()
        for pkg in installed_packages:
            pkg_path = Path(pkg.package_path)
            if pkg_path.exists():
                shutil.rmtree(pkg_path)
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to reset models: {e}")

def _check_network_connectivity(host="8.8.8.8", port=53, timeout=3):
    """Check if network connection is available."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM).connect((host, port))
        return True
    except Exception:
        return False

def download_models():
    """Download required translation models."""
    try:
        if not _check_network_connectivity():
            raise RuntimeError("Network connection is not available")

        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()

        if not available_packages:
            raise RuntimeError("Failed to fetch package list from server")

        ja_en_package = next(
            filter(lambda x: x.from_code == "ja" and x.to_code == "en", available_packages),
            None
        )
        en_ja_package = next(
            filter(lambda x: x.from_code == "en" and x.to_code == "ja", available_packages),
            None
        )

        if not ja_en_package or not en_ja_package:
            raise RuntimeError("Required translation packages not found")

        argostranslate.package.install_from_path(ja_en_package.download())
        argostranslate.package.install_from_path(en_ja_package.download())

        return True
    except Exception as e:
        raise RuntimeError(f"Model download failed: {e}")

def preload_models():
    """Preload models into memory to avoid first-use delay."""
    try:
        if check_models_installed():
            argostranslate.translate.translate("", "ja", "en")
            argostranslate.translate.translate("", "en", "ja")
        return True
    except Exception:
        return False

def translate_ja_to_en(text):
    try:
        return argostranslate.translate.translate(text, "ja", "en")
    except Exception as e:
        raise RuntimeError(f"Translation failed: {e}")

def translate_eng_to_jpn(text):
    try:
        return argostranslate.translate.translate(text, "en", "ja")
    except Exception as e:
        raise RuntimeError(f"Translation failed: {e}")

def translate(text, src_lang, dest_lang):
    try:
        return argostranslate.translate.translate(text, src_lang, dest_lang)
    except Exception as e:
        raise RuntimeError(f"Translation failed: {e}")

if __name__ == "__main__":
    print(translate_ja_to_en("もし「どうしても言い換えまで自動化したい、でもセキュリティが心配」という場合は、やはり「Javaでの機械的チェック」と「ローカルLLM（Ollama）でのリライト」の二段構えが最強です。"))