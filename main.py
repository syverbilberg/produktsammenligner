"""Entry point.  Start the app with:  streamlit run main.py

Project layout:
  src/fetching/     varehenting   – varekode/link → Product (talks to elkjop.no)
  src/categories/   kategoriguide – which specs matter per product type
  src/comparison/   sammenligning – matching, scoring, summary and verdict
  src/ui/           grensesnitt   – the Streamlit page
"""
from src.ui.app import run

run()
