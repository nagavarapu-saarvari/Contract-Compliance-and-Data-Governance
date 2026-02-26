from typing import Dict, List
import statistics


class AggregatedDataProcessor:

    def __init__(self, dataset_source: str):
        self.dataset_source = dataset_source

    def validate_source(self) -> bool:
        # Ensures data is not coming from restricted internal linking
        if self.dataset_source == "external_licensed_dataset":
            return True
        return False

    def aggregate_metrics(self, records: List[Dict]) -> Dict:

        all_scores = []

        for record in records:
            metrics = record.get("metrics", [])
            all_scores.extend(metrics)

        if not all_scores:
            return {"average_score": 0, "count": 0}

        return {
            "average_score": round(statistics.mean(all_scores), 2),
            "count": len(all_scores)
        }


class ReportingService:

    def generate_population_report(self, aggregated_data: Dict) -> Dict:
        return {
            "report_type": "population_summary",
            "average_score": aggregated_data["average_score"],
            "record_count": aggregated_data["count"]
        }


# -------------------------------------------------
# Simulated Execution
# -------------------------------------------------

def main():

    processor = AggregatedDataProcessor(
        dataset_source="external_licensed_dataset"
    )

    if not processor.validate_source():
        print("Invalid data source.")
        return

    sample_records = [
        {"metrics": [78, 82, 85]},
        {"metrics": [88, 90, 84]},
        {"metrics": [91, 87, 89]}
    ]

    aggregated = processor.aggregate_metrics(sample_records)

    reporter = ReportingService()
    report = reporter.generate_population_report(aggregated)

    print("Generated Report:")
    print(report)


if __name__ == "__main__":
    main()