import kagglehub

datasetPath = kagglehub.dataset_download("souhagaa/nasa-access-log-dataset-1995")
print("Path to dataset files:", datasetPath)

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

dataFrame = spark.read.csv(datasetPath + "/NASA_access_log_Jul95.gz", header=True, inferSchema=True)
dataFrame.show(5)
dataFrame.printSchema()