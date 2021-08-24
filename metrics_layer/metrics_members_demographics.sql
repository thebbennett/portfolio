{{ config(materialized='table') }}
{{ generate_demographics('metrics_active_members', 'date_week') }}
