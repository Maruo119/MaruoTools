import subprocess
import csv
import os
import shutil
from datetime import datetime
from collections import defaultdict
import pytz

def run_git_command(command, repo_path):
    """Gitコマンドを実行し、結果を返す。失敗した場合はエラーメッセージを表示。"""
    result = subprocess.run(command, cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {' '.join(command)}")
        print(result.stderr)
        return None
    return result.stdout.strip()

def get_commit_history(repo_path, since=None, until=None):
    """指定した期間内のコミット履歴を取得する"""
    command = ["git", "log", "--pretty=format:%H,%an,%ae,%cd,%cn,%ce,%s", "--date=iso8601"]
    if since:
        command.append(f"--since={since}")
    if until:
        command.append(f"--until={until}")
    return run_git_command(command, repo_path).split("\n")

def get_changed_files(repo_path, commit_hash):
    """コミットハッシュに関連する変更されたファイルを取得する"""
    command = ["git", "show", "--name-only", "--pretty=format:", commit_hash]
    return run_git_command(command, repo_path).split("\n")

def parse_commit_data(commit_data, repo_path):
    """コミットデータを解析して指定したメッセージを含む場合のみCSV用のデータを準備する"""
    tz = pytz.timezone('Asia/Tokyo')
    parsed_data = []
    for line in commit_data:
        commit_hash, author_name, author_email, commit_date, committer_name, committer_email, commit_message = line.split(",", 6)
        
        changed_files = get_changed_files(repo_path, commit_hash)
        for file in changed_files:
            parsed_data.append([commit_hash, author_name, author_email, commit_date, commit_message, committer_name, committer_email, file])
    
    return parsed_data


def write_to_csv(parsed_data, output_file):
    """データをCSVファイルに書き込む"""
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Commit Hash", "Author Name", "Author Email", "Commit Date", "Commit Message", "Committer Name", "Committer Email", "File Changed"])
        writer.writerows(parsed_data)

def read_commit_history(input_file):
    """CSVからコミット履歴を読み込み、ファイルごとのデータにまとめる"""
    commit_data = defaultdict(list)
    with open(input_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # ヘッダーをスキップ
        for row in reader:
            commit_hash = row[0]
            file_changed = row[7]
            commit_date = row[3]
            commit_data[file_changed].append({"commit_hash": commit_hash, "commit_date": commit_date})
    return commit_data

def get_file_commit_info(commit_data):
    """ファイルごとの最古・最新の更新日、コミット回数を取得する"""
    result_data = []
    for file_path, commits in commit_data.items():
        sorted_commits = sorted(commits, key=lambda x: x["commit_date"])
        oldest_commit = sorted_commits[0]
        newest_commit = sorted_commits[-1]
        result_data.append([file_path, oldest_commit["commit_date"], oldest_commit["commit_hash"], newest_commit["commit_date"], newest_commit["commit_hash"], len(sorted_commits)])
    return result_data

def write_to_output_csv(output_file, result_data):
    """集計した結果をCSVファイルに書き込む"""
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Changed Files (Full Path)", "Oldest Update Date", "Oldest Commit Hash", "Newest Update Date", "Newest Commit Hash", "Commit Count"])
        writer.writerows(result_data)

def create_folder(folder_name):
    """指定されたフォルダが存在しない場合、作成する"""
    os.makedirs(folder_name, exist_ok=True)

def checkout_commit(repo_path, commit_hash, file_path, output_folder):
    """指定したコミットのファイルをチェックアウトして保存する"""
    command = ["git", "checkout", commit_hash, "--", file_path]
    if run_git_command(command, repo_path) is None:
        return
    destination = os.path.join(output_folder, file_path)
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    try:
        shutil.copy(os.path.join(repo_path, file_path), destination)
        #print(f"File {file_path} from commit {commit_hash} has been copied to {output_folder}")
    except FileNotFoundError:
        print(f"Warning: File {file_path} not found in the commit {commit_hash}. Skipping...")
    except Exception as e:
        print(f"Error: Failed to copy file {file_path} to {destination}. {e}")

def process_file_update_summary(input_file, repo_path):
    """ファイル更新情報に基づいて、Old/ New フォルダにファイルをチェックアウト"""
    with open(input_file, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # ヘッダーをスキップ
        for row in reader:
            file_path = row[0]
            oldest_commit_hash = row[2]
            newest_commit_hash = row[4]
            checkout_commit(repo_path, oldest_commit_hash, file_path, "Old")
            checkout_commit(repo_path, newest_commit_hash, file_path, "New")

def main():
    repo_path = "/Users/yuta/Documents/myGithub/freeCodeCamp"  # リポジトリのローカルパス
    output_file = "commit_history.csv"  # 出力するCSVファイル名
    since = "2024-12-01"  # 取得する期間の開始日
    until = "2024-12-31"  # 取得する期間の終了日

    # Step1 コミット履歴情報を取得
    commit_data = get_commit_history(repo_path, since, until)
    if not commit_data:
        return
    
    parsed_data = parse_commit_data(commit_data, repo_path)
    write_to_csv(parsed_data, output_file)
    print(f"Commit history has been saved to {output_file}")


    # Step2 コミット履歴からファイル単位の情報に整形する
    input_file = "commit_history.csv"  # 入力CSVファイル名
    output_file = "file_update_summary.csv"  # 出力CSVファイル名
    
    commit_data = read_commit_history(input_file)
    result_data = get_file_commit_info(commit_data)
    write_to_output_csv(output_file, result_data)
    print(f"File update summary has been saved to {output_file}")

    # Step3 Step2の情報を利用してOld, Newのファイルをダウンロードする
    #       プログラム実行後にWinMerge等の差分比較ツールを利用して変更箇所を目視確認するなど各自の利用用途に応じて活用ください
    create_folder("Old")
    create_folder("New")
    
    process_file_update_summary("file_update_summary.csv", repo_path)
    print("Process completed.")

if __name__ == "__main__":
    main()
