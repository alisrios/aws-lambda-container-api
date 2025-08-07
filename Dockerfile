# AWS Lambda Container Image for Python 3.11
FROM public.ecr.aws/lambda/python:3.11

# Copy requirements and install dependencies
COPY src/requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY src/lambda_function.py ${LAMBDA_TASK_ROOT}
COPY src/app.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["lambda_function.lambda_handler"]