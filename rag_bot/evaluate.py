#!/usr/bin/env python3
"""
Автоматическая оценка RAG-бота (golden_questions.json)
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
import re
from rag_bot import RAGbot

# KONFIG
LOGS_FILE = "rag_evaluation_logs.jsonl"
GOLDEN_QUESTIONS_FILE = "golden_questions.json"

class RAGEvaluator:
    def __init__(self, chroma_path="../chroma_db"):
        self.bot = RAGbot(chroma_path=chroma_path)
        self.logs_file = Path(LOGS_FILE)
        self.golden_questions_file = Path(GOLDEN_QUESTIONS_FILE)

        # Загружаем золотой набор из файла
        with open(self.golden_questions_file, 'r', encoding='utf-8') as f:
            self.golden_questions = json.load(f)

    def log_request(self, query: str, chunks_count: int, sources: list,
                    answer: str, response_length: int) -> str:
        """Логирование в JSONL"""
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "chunks_found": chunks_count,
            "sources": sources,
            "answer": answer,
            "response_length": response_length,
            "is_success": self._is_successful_response(answer, query),
            "coverage_score": self._calculate_coverage(query, answer)
        }

        with open(self.logs_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

        return log_entry["id"]

    def _is_successful_response(self, answer: str, query: str) -> bool:
        """Определение успешного ответа"""
        bad_patterns = [
            "don't know", "не знаю", "нет информации",
            "no relevant", "empty context", "suspicious query"
        ]

        good_length = len(answer) > 50
        has_structure = bool(re.search(r'1\..*2\..*3\.', answer))

        is_bad = any(pattern in answer.lower() for pattern in bad_patterns)
        return good_length and has_structure and not is_bad

    def _calculate_coverage(self, query: str, answer: str) -> float:
        """Оценка полноты (0.0-1.0)"""
        if len(answer) < 50:
            return 0.0

        score = min(len(answer) / 300, 1.0)
        if any(p in answer.lower() for p in ["don't know", "не знаю"]):
            score = 0.0
        return round(score, 2)

    def run_evaluation(self):
        """Тестирование золотого набора"""
        print("🧪 Автоматическая оценка RAG...")
        print(f"📊 Вопросов из golden_questions.json: {len(self.golden_questions)}")

        results = []
        known_count = sum(1 for q in self.golden_questions if q["category"] == "known")
        gap_count = sum(1 for q in self.golden_questions if q["category"] == "gap")

        print(f"✅ Известных тем: {known_count}")
        print(f"🚫 Пробелов: {gap_count}")
        print("-" * 80)

        for i, question in enumerate(self.golden_questions, 1):
            query = question["query"]
            expected = question["expected"]
            category = question["category"]

            print(f"[{i:2d}/{len(self.golden_questions)}] {category.upper()} ❓ {query}")

            try:
                answer = self.bot.query(query)

                # Имитация метаданных (в продакшене берите из rag_bot.query)
                chunks_count = 3 if "don't know" not in answer.lower() else 0
                sources = ["Alaric_Pendragon.md"] if chunks_count > 0 else []
                response_length = len(answer)

                log_id = self.log_request(query, chunks_count, sources, answer, response_length)

                # Оценка
                is_correct = (
                    expected.lower() in answer.lower() if expected != "UNKNOWN"
                    else "don't know" in answer.lower()
                )
                coverage = self._calculate_coverage(query, answer)

                result = {
                    "question": query,
                    "expected": expected,
                    "answer": answer[:100] + "..." if len(answer) > 100 else answer,
                    "chunks_found": chunks_count,
                    "is_correct": is_correct,
                    "coverage": coverage,
                    "log_id": log_id,
                    "category": category
                }
                results.append(result)

                status = "✅ PASS" if is_correct else "❌ FAIL"
                print(f"   {status} Coverage: {coverage} | Chunks: {chunks_count}")

            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                continue

        self.analyze_results(results)
        return results

    def analyze_results(self, results: list):
        """Анализ и отчёт"""
        total = len(results)
        known_results = [r for r in results if r["category"] == "known"]
        gap_results = [r for r in results if r["category"] == "gap"]

        known_correct = sum(1 for r in known_results if r["is_correct"])
        gap_correct = sum(1 for r in gap_results if r["is_correct"])

        print("\n" + "="*80)
        print("📈 ИТОГОВАЯ ОЦЕНКА RAG")
        print("="*80)
        print(f"Всего вопросов: {total}")
        print(f"✅ Известные темы: {known_correct}/{len(known_results)} ({known_correct/len(known_results)*100:.1f}%)")
        print(f"🚫 Пробелы: {gap_correct}/{len(gap_results)} ({gap_correct/len(gap_results)*100:.1f}%)")
        print(f"📊 Общая точность: {sum(1 for r in results if r['is_correct'])/total*100:.1f}%")

        # Пробелы
        failed_gaps = [r for r in gap_results if not r["is_correct"]]
        if failed_gaps:
            print(f"\n🚨 ПРОБЕЛЫ В ЗНАНИЯХ ({len(failed_gaps)}):")
            for gap in failed_gaps:
                print(f"  • {gap['question'][:60]}...")

        # Рекомендации
        print(f"\n🔧 РЕКОМЕНДАЦИИ ПО БАЗЕ ЗНАНИЙ:")
        if failed_gaps:
            print("  1. Добавить документы по темам:")
            for gap in failed_gaps[:3]:
                print(f"     - {gap['question'].split('?')[0].lower()}.md")
        print("  2. Покрытие: quantum magic, multiverse, new tech")
        print("  3. Переиндексировать: python build_index.py")

if __name__ == "__main__":
    evaluator = RAGEvaluator()
    results = evaluator.run_evaluation()
