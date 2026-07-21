# Review Focus — Samachar Intelligence Integration Runtime

## Primary Review Objective

Validate that Samachar operates as the governed upstream Intelligence Ingestion Layer for SVACS.

The implementation should be reviewed as an integration and orchestration layer.

It is not a Vision Runtime and does not implement maritime reasoning.

---

## Primary Runtime Flow

```text
Manual Input / Image / Satellite Feed
                |
                v
             Samachar
                |
                +----------------------+
                |                      |
                | Image Input          | Manual / Satellite
                v                      v
         Vision Runtime         Samachar Ingestion
                |                      |
                +----------+-----------+
                           |
                           v
              Canonical Intelligence
                           |
                           v
               SVACS Contract Mapper
                           |
                           v
                     SVACS Runtime