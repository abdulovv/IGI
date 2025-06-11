FROM python:3.9-slim

WORKDIR /app

COPY main.py /app/
COPY geometric_lib/circle.py /app/geometric_lib/
COPY geometric_lib/square.py /app/geometric_lib/

ENV CIRCLE_RADIUS=${CIRCLE_RADIUS}
ENV SQUARE_SIDE=${SQUARE_SIDE}

CMD ["python", "main.py"]