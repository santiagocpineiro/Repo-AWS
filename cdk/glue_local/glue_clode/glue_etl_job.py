import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from datetime import datetime
from pyspark.sql.functions import lit
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Leer archivo txt desde bucket simulado
input_df = spark.read.text("s3://my-local-bucket/ejemplo.txt")

# Agregar columnas particionadas por fecha
now = datetime.now()
input_df = input_df.withColumn("year", lit(now.year)) \
                   .withColumn("month", lit(now.month)) \
                   .withColumn("day", lit(now.day))

# Guardar en formato CSV con particionado
input_df.write.partitionBy("year", "month", "day") \
             .mode("overwrite") \
             .csv("s3://my-glue-output-bucket/output/")

job.commit()

class GlueJobStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        glue_role = iam.Role(
            self, "GlueJobRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
            ]
        )

        # Asset: Script Glue desde el folder
        glue_asset = s3_assets.Asset(
            self,
            "GlueScriptAsset",
            path=os.path.join("cdk", "glue_scripts", "glue_etl_job.py")
        )

        # Job Glue
        glue_job = glue.CfnJob(
            self,
            "GlueS3ToS3Job",
            name="S3ToS3Job",
            role=glue_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                python_version="3",
                script_location=f"s3://{glue_asset.s3_bucket_name}/{glue_asset.s3_object_key}"
            ),
            default_arguments={
                "--job-language": "python",
                "--TempDir": "s3://my-local-bucket/temp/",
            },
            glue_version="4.0",
            number_of_workers=2,
            worker_type="Standard"
        )

        # Permitir que el Glue Job acceda al asset
        glue_asset.grant_read(glue_role)
