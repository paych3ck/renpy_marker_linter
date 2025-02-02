import os
import argparse
import yaml


def load_markers_from_yaml(yaml_file_path):
    try:
        with open(yaml_file_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            markers = config.get("markers", [])
            return markers
    except Exception as e:
        print(f"Ошибка при загрузке YAML файла с маркерами: {e}")
        return []


def search_markers_in_file(file_path, markers):
    results = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                for marker in markers:
                    if marker in line:
                        idx = line.find(marker)
                        main_part = line[:idx].rstrip()
                        marker_text = line[idx:].strip()
                        results.append((i, main_part, marker_text))
                        break

    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Поиск маркеров в файлах Ren'Py проекта"
    )
    parser.add_argument(
        "folder",
        help="Путь к папке с проектом"
    )
    parser.add_argument(
        "--markers",
        default="markers.yml",
        help="Путь к YML файлу с маркерами (по умолчанию: markers.yml)"
    )
    args = parser.parse_args()

    folder = args.folder
    if not os.path.isdir(folder):
        parser.error(f"Указанный путь '{folder}' не является директорией")

    markers = load_markers_from_yaml(args.markers)
    if not markers:
        print("Список маркеров пуст или YAML файл не может быть прочитан.")
        return

    found_files = {}
    output_buffer = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".rpy"):
                file_path = os.path.join(root, file)
                results = search_markers_in_file(file_path, markers)

                if results:
                    found_files[file_path] = results

    if found_files:
        for file_path, occurrences in found_files.items():
            output_buffer.append(f"<h2> 🔵 Пометки в файле: {file_path}</h2>")
            for line_no, main_part, marker_text in occurrences:
                output_buffer.append(f"🔴 Строка {line_no}<br />")
                output_buffer.append(f"🟡 Основная часть: {main_part}<br />")
                output_buffer.append(f"🟢 Пометка: {marker_text}<br />")

            output_buffer.append("<hr>")

        final_report = "\n".join(output_buffer)
        summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_file:
            with open("report.md", "a", encoding="utf-8") as f:
                f.write(final_report + "\n")

    else:
        print("Пометки не найдены.")


if __name__ == "__main__":
    main()
