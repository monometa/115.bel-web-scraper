# import os

import pyspark.sql.functions as f
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

schema = StructType(
    [
        StructField("adress", StringType(), True),
        StructField("category", StringType(), True),
        StructField("district", StringType(), True),
        StructField("malfunction_type", StringType(), True),
        StructField("number", StringType(), False),
        StructField("organization_comment", StringType(), True),
        StructField("performer", StringType(), True),
        StructField("rating", StringType(), True),
        StructField("request_moddate", StringType(), True),
        StructField("request_regdate", StringType(), True),
        StructField("status", StringType(), True),
        StructField("status_date", StringType(), True),
        StructField("user_comment", StringType(), True),
        StructField("x", StringType(), True),
        StructField("y", StringType(), True),
        StructField("z", StringType(), True),
    ]
)


def get_spark():
    spark = (
        SparkSession.builder.master("local[*]")
        .appName("SparkDelta")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config(
            "spark.jars.packages",
            "io.delta:delta-core_2.12:1.1.0,"
            "org.apache.hadoop:hadoop-aws:3.2.2,"
            "com.amazonaws:aws-java-sdk-bundle:1.12.180",
        )
        .getOrCreate()
    )
    spark._jsc.hadoopConfiguration().set("com.amazonaws.services.s3.enableV4", "true")
    spark._jsc.hadoopConfiguration().set(
        "fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"
    )
    spark._jsc.hadoopConfiguration().set(
        "fs.s3a.aws.credentials.provider",
        "com.amazonaws.auth.InstanceProfileCredentialsProvider,com.amazonaws.auth.DefaultAWSCredentialsProviderChain",
    )
    spark._jsc.hadoopConfiguration().set(
        "fs.AbstractFileSystem.s3a.impl", "org.apache.hadoop.fs.s3a.S3A"
    )
    spark.sparkContext.setLogLevel("DEBUG")
    return spark


def transform_spark(file):
    spark = get_spark()
    df = (
        spark.read.schema(schema)
        .format("json")
        .load(f"s3a://115bel/from_parser/{file}.json")
    )

    df = (
        df.withColumn(
            "request_regdate", f.to_timestamp("request_regdate", "dd.MM.yyyy HH:mm")
        )
        .withColumn(
            "request_moddate", f.to_timestamp("request_moddate", "dd.MM.yyyy HH:mm")
        )
        .withColumn("rating", f.col("rating").cast(IntegerType()))
        .withColumnRenamed("status", "stage")
    )

    split_col = f.split(df["status_date"], " ")

    df = (
        df.withColumn(
            "status",
            f.when(f.col("status_date").contains("Выполнено"), "Выполнено")
            .when(f.col("status_date").contains("Просрочено"), "Просрочено")
            .when(f.col("status_date").contains("до "), "В процессе выполнения")
            .otherwise(None),
        )
        .withColumn(
            "current_deadline",
            f.when(f.col("status_date").contains("до "), split_col.getItem(1)),
        )
        .drop("status_date")
        .withColumn(
            "current_deadline", f.to_date(f.col("current_deadline"), "dd.MM.yyyy")
        )
    )

    df = df.select(
        "number",
        "category",
        "malfunction_type",
        "performer",
        "adress",
        "district",
        "stage",
        "status",
        "current_deadline",
        "rating",
        "request_regdate",
        "request_moddate",
        "user_comment",
        "organization_comment",
    )
    (
        df.write.mode("overwrite")
        .options(header="True", delimiter=",")
        .parquet(f"s3a://115bel/processed_parquet/{file}.parquet")
    )


def print_df_5_rows(file):
    spark = get_spark()
    df = spark.read.format("parquet").load(
        f"s3a://115bel/processed_parquet/{file}.parquet/*"
    )

    df.show(5, vertical=True)


def main():
    transform_spark("2020_may")
    print_df_5_rows("2020_may")


if __name__ == "__main__":
    main()
