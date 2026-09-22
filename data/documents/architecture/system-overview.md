# Aegis System Overview

Aegis is a retrieval-augmented knowledge assistant for engineering teams. It
ingests internal documentation, indexes it, and answers questions grounded in
that documentation.

## Components

The system is composed of a small number of services that each own one
responsibility.

### Ingestion Service

Reads raw documents from object storage, parses them, and produces chunks
with metadata attached. This is the first stage of the pipeline and has no
dependency on any other service.

### Retrieval Service

Given a query, finds the most relevant chunks using a combination of vector
similarity and keyword search. Depends on the ingestion service having
already populated the index.

### Answer Service

Combines retrieved chunks with the user's question and calls a language
model to produce a grounded answer, citing the source documents it used.

## Data Flow

Documents flow through the system in one direction: ingestion writes chunks
to the index, retrieval reads from the index, and the answer service reads
from retrieval. No component writes back upstream.

## Non-Goals

Aegis does not attempt to modify source documents, nor does it attempt to
answer questions outside the scope of the ingested knowledge base.
