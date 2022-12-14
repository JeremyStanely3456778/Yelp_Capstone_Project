# -*- coding: utf-8 -*-
"""ETL_pipeline_apache_beam.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oap1sgA5AMZM_o6WP2sF64URoo5zC__X
"""

#install dependencies
import os
import argparse
import logging
import re
from apache_beam.options.pipeline_options import PipelineOptions
import apache_beam as beam

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\jerem\Desktop\yelp_capstone_project\key_auth_4.json"

class dataingestion:

    def parse_method(self, string_input):

        # Strip out carriage return, newline and quote characters.
        values = re.split(",", re.sub('\r\n', '', re.sub('"', '', string_input)))
        row = dict(
            zip(('song_id', 'title', 'year', 'artist_id', 'genre_id'),
                values))
        return row

def run():

    parser = argparse.ArgumentParser()
    parser.add_argument('--input',dest='input',
            required=False,
            help='Input file to read. This can be a local file or '
                 'a file in a Google Storage Bucket.',
            default='gs://capstone_yelp_project/df_songs.csv' )
    parser.add_argument('--output',
                        dest='output',
                        required=False,
                        help='Output BQ table to write results to.',
                        default='Songs.songs')
    parser.add_argument('--project', dest='project', required=False, help='Project name', default='decent-beacon-367514',
                        action="store")
    parser.add_argument('--bucket_name', dest='bucket_name', required=False, help='bucket name',
                        default='dataflow_python_test')
    parser.add_argument('--runner', dest='runner', required=False, help='Runner Name', default='DataflowRunner',
                        action="store")
    parser.add_argument('--jobname', dest='job_name', required=False, help='jobName', default='t4',
                        action="store")
    parser.add_argument('--staging_location', dest='staging_location', required=False, help='staging_location',
                        default='gs://jeremy_staging/staging')
    parser.add_argument('--region', dest='region', required=False, help='Region', default='us-west1',
                        action="store")
    parser.add_argument('--temp_location', dest='temp_location', required=False, help='temp location',
                        default='gs://jeremy_staging/temp/')


    args = parser.parse_args()

    pipeline_options = {
        'project': args.project,
        'staging_location': args.staging_location,
        'runner': args.runner,
        'job_name': args.job_name,
        'region': args.region,
        'output': args.output,
        'input': args.input,
        'temp_location': args.temp_location}
    print(pipeline_options)
    pipeline_options_val = PipelineOptions.from_dictionary(pipeline_options)
    p = beam.Pipeline(options=pipeline_options_val)
    data_ingestion = dataingestion()

    (p | 'Read from a File' >> beam.io.ReadFromText(pipeline_options["input"], skip_header_lines=1)
     | 'String To BigQuery Row' >> beam.Map(lambda s: data_ingestion.parse_method(s)) |
     'Write to BigQuery' >> beam.io.Write(
                beam.io.WriteToBigQuery(
                    pipeline_options["output"],
                    schema='song_id:STRING,title:STRING,year:STRING,artist_id:STRING,genre_id:STRING',
                    create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                    write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE)))
    p.run().wait_until_finish()

#BigQuerySink


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()