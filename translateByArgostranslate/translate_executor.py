import argostranslate.translate
import argostranslate.package
import shutil
from pathlib import Path
import socket
import time
import urllib.request
import urllib.error

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

def _check_network_connectivity(timeout=3):
    """Check if network connection is available by attempting DNS resolution."""
    hosts = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]

    for host in hosts:
        try:
            socket.create_connection((host, 53), timeout=timeout)
            return True
        except (socket.timeout, socket.error, OSError):
            continue

    return False

def download_models():
    """Download required translation models."""
    try:
        if not _check_network_connectivity():
            raise RuntimeError("ネットワーク接続がありません。インターネット接続を確認してください。")

        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()

        if not available_packages:
            raise RuntimeError("サーバーからパッケージリストを取得できませんでした。ネットワーク接続を確認してください。")

        ja_en_package = next(
            filter(lambda x: x.from_code == "ja" and x.to_code == "en", available_packages),
            None
        )
        en_ja_package = next(
            filter(lambda x: x.from_code == "en" and x.to_code == "ja", available_packages),
            None
        )

        if not ja_en_package or not en_ja_package:
            raise RuntimeError("必要な翻訳パッケージが見つかりません。")

        argostranslate.package.install_from_path(ja_en_package.download())
        argostranslate.package.install_from_path(en_ja_package.download())

        return True
    except RuntimeError:
        raise
    except urllib.error.URLError as e:
        raise RuntimeError("ネットワーク通信エラー: インターネット接続を確認してください。")
    except Exception as e:
        raise RuntimeError(f"モデルダウンロード失敗: {e}")

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
    except urllib.error.URLError as e:
        raise RuntimeError("ネットワーク通信エラー: オフライン翻訳環境では外部リソースにアクセスできません。")
    except Exception as e:
        raise RuntimeError(f"翻訳失敗: {e}")

def translate_eng_to_jpn(text):
    try:
        return argostranslate.translate.translate(text, "en", "ja")
    except urllib.error.URLError as e:
        raise RuntimeError("ネットワーク通信エラー: オフライン翻訳環境では外部リソースにアクセスできません。")
    except Exception as e:
        raise RuntimeError(f"翻訳失敗: {e}")

def translate(text, src_lang, dest_lang):
    try:
        return argostranslate.translate.translate(text, src_lang, dest_lang)
    except urllib.error.URLError as e:
        raise RuntimeError("ネットワーク通信エラー: オフライン翻訳環境では外部リソースにアクセスできません。")
    except Exception as e:
        raise RuntimeError(f"翻訳失敗: {e}")

if __name__ == "__main__":
    print(translate_ja_to_en("もし「どうしても言い換えまで自動化したい、でもセキュリティが心配」という場合は、やはり「Javaでの機械的チェック」と「ローカルLLM（Ollama）でのリライト」の二段構えが最強です。"))