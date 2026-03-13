import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()


class DetectorRepository:

    def __init__(self):

        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

    def get_detectors(self, document_id):

        with self.conn.cursor() as cur:

            cur.execute(
                "SELECT detectors_json FROM detectors WHERE document_id=%s",
                (document_id,)
            )

            rows = cur.fetchall()

        detectors = []
        for row in rows:
            data = row[0]
            if isinstance(data, list):
                detectors.extend(data)
            else:
                detectors.append(data)
        return detectors

    def store_detectors(self, document_id, detectors):

        with self.conn.cursor() as cur:

            for d in detectors:

                cur.execute(
                    """
                    INSERT INTO detectors(document_id, rule_id, detector_json)
                    VALUES(%s,%s,%s)
                    """,
                    (
                        document_id,
                        d["rule_id"],
                        json.dumps(d)
                    )
                )

        self.conn.commit()

    def close(self):
        self.conn.close()